import urllib.request,re,html,json

URLS=[
"https://apkhub-static.appmeme.com/_next/static/chunks/app/ipa/(store)/ipa/%5Bid%5D/download/page-edd68d795de4995c.js",
"https://apkhub-static.appmeme.com/_next/static/chunks/app/ipa/(store)/ipa/%5Bid%5D/downloading/page-9cdd3c3474503718.js",
]
UA={"User-Agent":"Mozilla/5.0"}

for u in URLS:
    print("\n===== CHUNK",u,"=====")
    req=urllib.request.Request(u,headers=UA)
    with urllib.request.urlopen(req,timeout=40) as r:
        b=r.read()
    s=b.decode("utf-8","replace")
    print("BYTES",len(b))
    print("FULL_JS")
    print(s)
    print("\nEXTRACTED_URLS")
    for x in sorted(set(re.findall(r'https?://[^"\'<>\s)]+',s))):
        print(x)
    print("\nLIKELY_PATHS")
    for x in sorted(set(re.findall(r'["\'](/[^"\']{1,220})["\']',s))):
        if any(k in x.lower() for k in ["download","api","ipa","package","file","app","oss","store"]):
            print(x)
    print("\nCONTEXTS")
    for key in [
        "fetch(","axios","XMLHttpRequest","window.location","location.href","router.push",
        "download","downloading","shareUrl1","oss_object_name_apk","oss_object_name_xapk",
        "storage.appmeme.com","findPackage","server action","callServer","actionId","tw.app.idol"
    ]:
        ms=list(re.finditer(re.escape(key),s,re.I))
        if ms:
            print("\n###",key,"COUNT",len(ms))
            for m in ms[:40]:
                print(s[max(0,m.start()-700):min(len(s),m.end()+1600)])
                print("---")
