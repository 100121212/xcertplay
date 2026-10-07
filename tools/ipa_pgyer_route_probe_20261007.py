import re, json, urllib.request, urllib.parse, http.cookiejar, sys

BASE = "https://www.pgyer.com/ipa/ipa/tw.app.idol"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/154 Safari/537.36"
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Referer": BASE,
    })
    try:
        with opener.open(req, timeout=45) as r:
            b = r.read()
            return r.status, r.geturl(), dict(r.headers), b
    except Exception as e:
        print("FETCH_ERR", url, repr(e))
        return None, None, {}, b""

pages = [BASE, BASE+"/download", BASE+"/downloading"]
all_text = {}
for u in pages:
    st, final, h, b = fetch(u)
    print("\n=== PAGE ===", u)
    print("STATUS", st, "FINAL", final, "BYTES", len(b))
    print("CTYPE", h.get("Content-Type"), "LOCATION", h.get("Location"))
    s = b.decode("utf-8","replace")
    all_text[u] = s

    pats = [
        "oss_object_name_apk","oss_object_name_xapk","shareUrl1",
        "storage.appmeme.com","packageCDN","downloadUrl","download_url",
        "tw.app.idol","1.0.1","1_0_1",".ipa"
    ]
    for p in pats:
        ms = list(re.finditer(re.escape(p), s, re.I))
        if ms:
            print("\n--", p, "COUNT", len(ms))
            for m in ms[:20]:
                print(s[max(0,m.start()-700):min(len(s),m.end()+1400)].replace("\n"," "))

    hrefs = sorted(set(re.findall(r'href=["\']([^"\']+)["\']', s, re.I)))
    print("\nHREFS")
    for x in hrefs:
        if any(k in x.lower() for k in ["download","downloading","idol","ipa","storage","appmeme"]):
            print(x)

    urls = sorted(set(re.findall(r'https?://[^"\'<>\\\s]+', s)))
    print("\nURLS")
    for x in urls:
        if any(k in x.lower() for k in ["download","idol","ipa","storage","appmeme"]):
            print(x[:2000])

print("\n=== COOKIE JAR ===")
for c in cj:
    print(c.domain, c.name, c.value[:120])

# Try RSC variants; server-rendered app sometimes exposes more data there.
for path in ["download","downloading"]:
    u = f"{BASE}/{path}?_rsc=1"
    st, final, h, b = fetch(u)
    print("\n=== RSC ===", u, "STATUS", st, "FINAL", final, "BYTES", len(b))
    s=b.decode("utf-8","replace")
    for p in ["oss_object_name_apk","storage.appmeme.com","shareUrl1","tw.app.idol",".ipa"]:
        for m in list(re.finditer(re.escape(p),s,re.I))[:20]:
            print("RSC",p,s[max(0,m.start()-600):min(len(s),m.end()+1200)].replace("\n"," "))

# Discover API-looking strings from all pages.
combined="\n".join(all_text.values())
print("\n=== API-LIKE STRINGS ===")
for x in sorted(set(re.findall(r'["\']([^"\']{1,300})["\']', combined))):
    low=x.lower()
    if any(k in low for k in ["/api/","download","downloading","oss_object","shareurl","storage.appmeme"]):
        print(x)
