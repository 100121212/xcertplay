import urllib.request, urllib.error, re, http.cookiejar, hashlib

BASE="https://www.pgyer.com/ipa/ipa/tw.app.idol"
PAGES=[BASE,BASE+"/download",BASE+"/downloading"]
UA={"User-Agent":"Mozilla/5.0"}
cj=http.cookiejar.CookieJar()
opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url):
    req=urllib.request.Request(url,headers=UA)
    with opener.open(req,timeout=45) as r:
        return r.status,r.geturl(),dict(r.headers),r.read()

page_data={}
all_js=set()
for url in PAGES:
    st,final,h,b=fetch(url)
    s=b.decode("utf-8","replace")
    js=sorted(set(re.findall(r'https://apkhub-static\.appmeme\.com/[^"\'<>\s]+?\.js',s)))
    page_data[url]=(st,final,s,js)
    all_js.update(js)
    print("\nPAGE",url)
    print("STATUS",st,"FINAL",final,"BYTES",len(b),"JS_COUNT",len(js))
    for x in js:
        if "/app/ipa/" in x or "chunk" in x:
            print("JS",x)
    print("DOWNLOAD_LINKS")
    for href in sorted(set(re.findall(r'href=["\']([^"\']+)["\']',s))):
        if any(k in href.lower() for k in ["download","storage","ipa"]):
            print(href)
    print("KEY_COUNTS",
          "oss_apk",s.count("oss_object_name_apk"),
          "share",s.count("shareUrl1"),
          "storage",s.count("storage.appmeme.com"))

print("\n=== PAGE-SPECIFIC JS ===")
base_js=set(page_data[BASE][3])
for url in PAGES[1:]:
    print("\nFOR",url)
    for x in sorted(set(page_data[url][3])-base_js):
        print(x)

texts=[]
for u in sorted(all_js):
    try:
        st,final,h,b=fetch(u)
        txt=b.decode("utf-8","replace")
        texts.append((u,txt))
    except Exception as e:
        print("JS_ERR",u,repr(e))

needles=[
 "storage.appmeme.com","packageCDNPrefix","findPackage",
 "oss_object_name_apk","oss_object_name_xapk","shareUrl1",
 "/downloading","/download","downloadUrl","download_url",
 "fetch(","axios","XMLHttpRequest","server action","server-reference",
 "APKHUB_APP_API_TOKEN","api."
]

print("\n=== INTERESTING CHUNKS ===")
for u,txt in texts:
    hits=[n for n in needles if n.lower() in txt.lower()]
    if hits:
        print("\nCHUNK",u,"BYTES",len(txt.encode()),"HITS",",".join(hits))
        # print compact contexts around the rarer/actionable needles only
        for n in ["oss_object_name_apk","shareUrl1","storage.appmeme.com","/downloading","downloadUrl","download_url","fetch(","axios","APKHUB_APP_API_TOKEN"]:
            ms=list(re.finditer(re.escape(n),txt,re.I))
            if not ms: continue
            print("TOKEN",n,"COUNT",len(ms))
            for m in ms[:20]:
                ctx=txt[max(0,m.start()-450):min(len(txt),m.end()+1000)]
                print("CTX",re.sub(r'\s+',' ',ctx))

print("\n=== ROUTE/API STRING LITERALS ===")
strings=set()
for u,txt in texts:
    for q,content in re.findall(r'(["\'])(.{1,400}?)\1',txt):
        if any(k in content.lower() for k in ["download","api","storage","package","ipa"]):
            strings.add(content)
for x in sorted(strings):
    if len(x)<400:
        print(repr(x))
