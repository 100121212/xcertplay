import re, urllib.request, html

UA={"User-Agent":"Mozilla/5.0"}
def get(url):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=40) as r:
        return r.read().decode("utf-8","replace"), r.geturl(), r.status

urls=[
 "https://www.pgyer.com/ipa/ipa/tw.app.idol/download",
 "https://www.pgyer.com/ipa/ipa/tw.app.idol/downloading"
]

for url in urls:
    s,final,status=get(url)
    print("\nPAGE",url,"STATUS",status,"FINAL",final,"LEN",len(s))

    # All anchors whose text or href is download-related.
    for m in re.finditer(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>',s,re.I|re.S):
        href=html.unescape(m.group(1))
        txt=re.sub(r'<[^>]+>',' ',m.group(2))
        txt=html.unescape(re.sub(r'\s+',' ',txt)).strip()
        if "download" in href.lower() or "download" in txt.lower() or "ipa" in txt.lower():
            print("ANCHOR",repr(txt[:300]),"->",href)

    # Flight-data hrefs near Download IPA text.
    for m in re.finditer(r'Download IPA',s,re.I):
        ctx=s[max(0,m.start()-1800):min(len(s),m.end()+1000)]
        hrefs=re.findall(r'(?:href|\\\"href\\\")[:=]\\?"([^"\\]+)',ctx,re.I)
        print("DOWNLOAD_CTX_HREFS",hrefs)
        print(ctx.replace("\n"," ")[:3200])

    # Route-specific JS chunks.
    js=sorted(set(re.findall(r'https://apkhub-static\.appmeme\.com/[^"\'<>\s]+?\.js',s)))
    print("JS",len(js))
    for u in js:
        if "/download/" in u or "/downloading/" in u:
            print("ROUTE_JS",u)
            js_s,_,_=get(u)
            print("ROUTE_JS_LEN",len(js_s))
            for key in ["href","storage.appmeme.com","oss_object_name_apk","shareUrl1","window.location","location.href","download","downloading","fetch(","axios"]:
                ms=list(re.finditer(re.escape(key),js_s,re.I))
                if ms:
                    print("JSKEY",key,"COUNT",len(ms))
                    for x in ms[:20]:
                        print(js_s[max(0,x.start()-500):min(len(js_s),x.end()+1400)])
                        print("---")
