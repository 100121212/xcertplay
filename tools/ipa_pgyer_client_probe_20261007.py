import subprocess, pathlib, re, os, time

BASE="https://www.pgyer.com/ipa/ipa/tw.app.idol"
PAGES=[
    ("base",BASE,None),
    ("download",BASE+"/download",BASE),
    ("downloading",BASE+"/downloading",BASE+"/download"),
]
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/154 Safari/537.36"
COOKIE="/tmp/pgyer.cookies"

def curl_fetch(name,url,referer=None):
    out=f"/tmp/{name}.html"
    cmd=["curl","-L","--retry","5","--retry-delay","1","--retry-all-errors","--max-time","60","-sS",
         "-A",UA,"-c",COOKIE,"-b",COOKIE,"-o",out,"-w","%{http_code}\n%{url_effective}\n",url]
    if referer:
        cmd[cmd.index("-c"):cmd.index("-c")] = ["-e",referer]
    p=subprocess.run(cmd,capture_output=True,text=True)
    meta=p.stdout.strip().splitlines()
    code=meta[0] if meta else "?"
    final=meta[1] if len(meta)>1 else url
    b=pathlib.Path(out).read_bytes() if pathlib.Path(out).exists() else b""
    print(f"FETCH {name} code={code} final={final} bytes={len(b)} stderr={p.stderr.strip()!r}")
    return b.decode("utf-8","replace")

pages={}
for name,url,ref in PAGES:
    s=""
    # Retry whole request if CDN gives 404.
    for attempt in range(1,5):
        s=curl_fetch(name,url,ref)
        if s and ("<html" in s.lower() or "self.__next_f" in s):
            print("PAGE_BODY_OK",name,"attempt",attempt)
            break
        time.sleep(1)
    pages[name]=s

js_by_page={}
alljs=set()
for name,s in pages.items():
    js=sorted(set(re.findall(r'https://apkhub-static\.appmeme\.com/[^"\'<>\s]+?\.js',s)))
    js_by_page[name]=set(js)
    alljs.update(js)
    print("\n=== PAGE",name,"===")
    print("JS_COUNT",len(js))
    print("KEY_COUNTS",
          "oss_apk",s.count("oss_object_name_apk"),
          "share",s.count("shareUrl1"),
          "storage",s.count("storage.appmeme.com"),
          "downloading",s.count("/downloading"))
    for href in sorted(set(re.findall(r'href=["\']([^"\']+)["\']',s))):
        if any(k in href.lower() for k in ["download","storage","ipa"]):
            print("HREF",href)

print("\n=== EXTRA JS download vs base ===")
for x in sorted(js_by_page.get("download",set())-js_by_page.get("base",set())):
    print(x)
print("\n=== EXTRA JS downloading vs base ===")
for x in sorted(js_by_page.get("downloading",set())-js_by_page.get("base",set())):
    print(x)

# Fetch all JS with curl.
texts=[]
for i,u in enumerate(sorted(alljs)):
    out=f"/tmp/js{i}.js"
    p=subprocess.run(["curl","-L","--retry","3","--max-time","45","-sS","-A",UA,"-o",out,u],capture_output=True,text=True)
    if pathlib.Path(out).exists():
        txt=pathlib.Path(out).read_text(errors="replace")
        texts.append((u,txt))

needles=["storage.appmeme.com","packageCDNPrefix","findPackage","oss_object_name_apk",
         "oss_object_name_xapk","shareUrl1","/downloading","downloadUrl","download_url",
         "fetch(","axios","APKHUB_APP_API_TOKEN","api.","package_url","packageUrl"]

print("\n=== ACTIONABLE JS CONTEXTS ===")
for u,txt in texts:
    hits=[n for n in needles if n.lower() in txt.lower()]
    if not hits:
        continue
    interesting=False
    # Only print chunks that look route/download specific.
    if "/app/ipa/" in u or any(n.lower() in txt.lower() for n in ["oss_object_name_apk","shareUrl1","/downloading","downloadUrl","download_url"]):
        interesting=True
    if not interesting:
        continue
    print("\nCHUNK",u,"BYTES",len(txt.encode()),"HITS",hits)
    for n in ["oss_object_name_apk","shareUrl1","/downloading","downloadUrl","download_url","storage.appmeme.com","fetch(","axios"]:
        ms=list(re.finditer(re.escape(n),txt,re.I))
        if not ms: continue
        print("TOKEN",n,"COUNT",len(ms))
        for m in ms[:25]:
            ctx=re.sub(r'\s+',' ',txt[max(0,m.start()-500):min(len(txt),m.end()+1300)])
            print("CTX",ctx)

print("\n=== LIKELY API/ROUTE LITERALS ===")
vals=set()
for u,txt in texts:
    for m in re.finditer(r'(["\'])(.{1,300}?)\1',txt):
        v=m.group(2)
        lv=v.lower()
        if any(k in lv for k in ["download","storage.appmeme","api/","/api","package"]):
            vals.add(v)
for v in sorted(vals):
    print(repr(v))
