import json
import urllib.request
import urllib.parse
import urllib.error
import re

UA = {"User-Agent": "Mozilla/5.0"}
HOSTS = ["https://iosapps.litten.ca", "https://iphoneosobscura.litten.ca"]
QUERIES = [
    "com.app.idol",
    "tw.app.idol",
    "育ててアイドルの卵",
    "培養偶像之蛋",
    "idol",
    "Chronus",
]

def fetch(url, timeout=60):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.geturl(), dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        try:
            body = e.read()
        except Exception:
            body = b""
        return e.code, e.geturl(), dict(e.headers), body
    except Exception as e:
        return None, url, {}, repr(e).encode()

for host in HOSTS:
    print("\n===== HOST", host, "=====")
    for q in QUERIES:
        url = host + "/search/" + urllib.parse.quote(q, safe="")
        st, final, h, b = fetch(url, 30)
        s = b.decode("utf-8", "replace")
        print("\n--- SEARCH", q)
        print("STATUS", st, "FINAL", final, "BYTES", len(b), "TYPE", h.get("Content-Type"))
        hrefs = re.findall(r'/getAppVersions/[^"< ]+', s)
        centers = re.findall(r'<center>(.*?)</center>', s, re.I | re.S)
        print("APP_LINKS", hrefs[:100])
        print("CENTERS", [re.sub(r"<[^>]+>", "", x).strip() for x in centers[:100]])

    for bid in ["com.app.idol", "tw.app.idol"]:
        url = host + "/getAppVersions/" + urllib.parse.quote(bid, safe="")
        st, final, h, b = fetch(url, 30)
        s = b.decode("utf-8", "replace")
        print("\n--- DIRECT", bid)
        print("STATUS", st, "FINAL", final, "BYTES", len(b), "TYPE", h.get("Content-Type"))
        links = re.findall(r'/getAppVersionLinks/[^"< ]+', s)
        urls = re.findall(r'https?://[^"< ]+?\.ipa(?:[^"< ]*)?', s, re.I)
        titles = re.findall(r'<title>(.*?)</title>', s, re.I | re.S)
        print("VERSION_LINKS", links[:100])
        print("IPA_URLS", urls[:100])
        print("TITLES", [re.sub(r"<[^>]+>", "", x).strip() for x in titles[:20]])

print("\n===== TROLLAPPS =====")
for host in HOSTS:
    url = host + "/trollapps"
    st, final, h, b = fetch(url, 180)
    print("\nHOST", host, "STATUS", st, "FINAL", final, "BYTES", len(b), "TYPE", h.get("Content-Type"))
    if st != 200:
        print(b[:2000].decode("utf-8", "replace"))
        continue
    try:
        data = json.loads(b.decode("utf-8", "replace"))
    except Exception as e:
        print("JSON_ERROR", repr(e))
        print(b[:2000].decode("utf-8", "replace"))
        continue
    apps = data.get("apps", [])
    print("APP_COUNT", len(apps))
    for term in QUERIES:
        t = term.lower()
        hits = []
        for a in apps:
            blob = " ".join(str(a.get(k, "")) for k in ["name", "bundleIdentifier", "developerName"]).lower()
            if t in blob:
                hits.append(a)
        print("\nTERM", term, "HITS", len(hits))
        for a in hits[:100]:
            print(json.dumps(a, ensure_ascii=False))
