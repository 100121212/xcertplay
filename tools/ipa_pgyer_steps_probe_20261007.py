import urllib.request, urllib.error, re, json, http.cookiejar

base = "https://www.pgyer.com/ipa/ipa/tw.app.idol"
paths = ["", "/download", "/downloading"]
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
headers = {"User-Agent":"Mozilla/5.0"}

def fetch(url):
    req = urllib.request.Request(url, headers=headers)
    try:
        with opener.open(req, timeout=45) as r:
            b = r.read()
            return r.status, r.geturl(), dict(r.headers), b
    except urllib.error.HTTPError as e:
        return e.code, e.geturl(), dict(e.headers), e.read()
    except Exception as e:
        return None, url, {}, repr(e).encode()

for path in paths:
    url = base + path
    status, final, hdr, b = fetch(url)
    s = b.decode("utf-8","replace")
    print("\n===== PAGE", path or "/", "=====")
    print("STATUS", status, "FINAL", final, "BYTES", len(b))
    print("LOCATION", hdr.get("Location"))
    print("CONTENT-TYPE", hdr.get("Content-Type"))
    print("COOKIES", [(c.name,c.value,c.domain,c.path) for c in cj])
    pats = [
        "storage.appmeme.com", "oss_object_name_apk", "oss_object_name_xapk",
        "shareUrl1", "downloadUrl", "download_url", "tw.app.idol",
        ".ipa", "/downloading", "/download", "formAction", "server-reference",
        "action="
    ]
    for p in pats:
        ms=list(re.finditer(re.escape(p),s,re.I))
        if not ms: continue
        print("\n###",p,"count",len(ms))
        for m in ms[:30]:
            print(s[max(0,m.start()-700):min(len(s),m.end()+1800)])
            print("---")
    # all storage/appmeme urls and likely package-looking strings
    print("\n### URLS")
    urls=sorted(set(re.findall(r'https?://[^"\'<>\s)]+',s)))
    for u in urls:
        if any(k in u.lower() for k in ["storage.appmeme","appmeme.com","download","ipa"]):
            print(u[:3000])
    print("\n### POSSIBLE OBJECT STRINGS")
    for x in sorted(set(re.findall(r'[^"\'<>\s]{1,240}\.(?:ipa|apk|xapk)',s,re.I))):
        print(x)

# Try RSC-style requests for step pages.
for path in ["/download","/downloading"]:
    url=base+path
    print("\n===== RSC",path,"=====")
    req=urllib.request.Request(url,headers={
        **headers,
        "RSC":"1",
        "Next-Router-State-Tree":'%5B%22%22%2C%7B%22children%22%3A%5B%22ipa%22%2C%7B%22children%22%3A%5B%22ipa%22%2C%7B%22children%22%3A%5B%22tw.app.idol%22%2C%7B%7D%5D%7D%5D%7D%5D%7D%5D'
    })
    try:
        with opener.open(req,timeout=45) as r:
            b=r.read()
            print("STATUS",r.status,"TYPE",r.headers.get("content-type"),"BYTES",len(b))
            s=b.decode("utf-8","replace")
            for p in ["storage.appmeme.com","oss_object_name_apk","shareUrl1",".ipa","tw.app.idol"]:
                if p.lower() in s.lower():
                    print("HAS",p)
                    for m in list(re.finditer(re.escape(p),s,re.I))[:20]:
                        print(s[max(0,m.start()-500):min(len(s),m.end()+1500)])
    except Exception as e:
        print("ERR",repr(e))
