import re, urllib.request, urllib.parse, sys, json, time

PAGE = "https://www.pgyer.com/ipa/ipa/tw.app.idol"
UA = {"User-Agent":"Mozilla/5.0"}

def get(url, timeout=40):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), dict(r.headers), r.geturl(), r.status

page_b, page_h, page_final, page_status = get(PAGE)
page = page_b.decode("utf-8","replace")
print("PAGE", page_status, len(page_b), page_final)

jsurls = sorted(set(re.findall(r'https://apkhub-static\.appmeme\.com/[^"\'<>\s]+?\.js', page)))
print("JS_COUNT", len(jsurls))

parts = []
for i,u in enumerate(jsurls,1):
    try:
        b, h, final, status = get(u)
        print("JS", i, status, len(b), u)
        parts.append(b.decode("utf-8","replace"))
    except Exception as e:
        print("JS_ERR", u, repr(e))

alljs = "\n".join(parts)
print("ALLJS_BYTES", len(alljs.encode("utf-8","replace")))

# Extract URLs from JS.
urls = sorted(set(re.findall(r'https?://[^"\'<>\s)]+', alljs)))
print("\n=== URL CANDIDATES ===")
for u in urls:
    low = u.lower()
    if any(k in low for k in ["download","ipa","appmeme","apk.live","api","oss","file"]):
        print(u[:2000])

# Extract string literals and contexts around likely download implementation tokens.
tokens = [
    "download", "downloadUrl", "download_url", "ipaUrl", "ipa_url",
    "oss_object", "assets.apk.live", ".ipa", "appmeme.com",
    "fetch(", "axios", "/api/", "objectName", "object_name"
]
print("\n=== CONTEXTS ===")
seen = set()
for token in tokens:
    for m in list(re.finditer(re.escape(token), alljs, re.I))[:120]:
        a=max(0,m.start()-500); b=min(len(alljs),m.end()+1200)
        ctx=alljs[a:b]
        key=ctx[:500]
        if key in seen: continue
        seen.add(key)
        print("\n###", token)
        print(ctx)

# Look for target-specific strings.
print("\n=== TARGET-SPECIFIC ===")
for patt in [r'tw\.app\.idol[^"\'<>\s]{0,300}', r'[^"\'<>\s]{0,200}tw\.app\.idol[^"\'<>\s]{0,300}']:
    for x in sorted(set(re.findall(patt, alljs, re.I)))[:300]:
        print(x)

# Probe plausible direct object names with Range requests.
cands = [
 "https://assets.apk.live/tw.app.idol--ipa-1_0_1.ipa",
 "https://assets.appmeme.com/tw.app.idol--ipa-1_0_1.ipa",
 "https://assets.apk.live/tw.app.idol--ipa-1_0_1",
 "https://assets.appmeme.com/tw.app.idol--ipa-1_0_1",
 "https://download.apk.live/tw.app.idol--ipa-1_0_1.ipa",
 "https://download.appmeme.com/tw.app.idol--ipa-1_0_1.ipa",
 "https://assets.apk.live/tw.app.idol--ipa-1.0.1.ipa",
 "https://assets.appmeme.com/tw.app.idol--ipa-1.0.1.ipa"
]
print("\n=== DIRECT PROBES ===")
for u in cands:
    req = urllib.request.Request(u, headers={**UA, "Range":"bytes=0-63"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            b=r.read(64)
            print("PROBE", r.status, r.geturl(), r.headers.get("Content-Type"), r.headers.get("Content-Length"), b[:16].hex(), repr(b[:32]))
    except Exception as e:
        code=getattr(e,"code",None)
        headers=getattr(e,"headers",None)
        loc=headers.get("Location") if headers else None
        print("PROBE_ERR", code, u, "LOC", loc, repr(e))
