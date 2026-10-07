import urllib.request,re,html
UA={"User-Agent":"Mozilla/5.0"}
urls=[
"https://apkhub-static.appmeme.com/_next/static/chunks/app/ipa/(store)/ipa/%5Bid%5D/download/page-edd68d795de4995c.js",
"https://apkhub-static.appmeme.com/_next/static/chunks/app/ipa/(store)/ipa/%5Bid%5D/downloading/page-9cdd3c3474503718.js",
]
for u in urls:
    print("\n===== FILE",u,"=====")
    req=urllib.request.Request(u,headers=UA)
    with urllib.request.urlopen(req,timeout=30) as r:
        b=r.read()
    s=b.decode("utf-8","replace")
    print("BYTES",len(b))
    # Candidate strings
    strings=sorted(set(re.findall(r'["\']([^"\']{3,400})["\']',s)))
    print("=== INTERESTING STRING LITERALS ===")
    for x in strings:
        low=x.lower()
        if any(k in low for k in ["download","api","ipa","package","storage","oss","shareurl","fetch","http","tw.app.idol","downloading"]):
            print(x)
    # Contexts around network and package logic
    print("=== CONTEXTS ===")
    pats=["fetch(","axios","XMLHttpRequest","/api/","download","downloading","storage.appmeme.com","oss_object_name_apk","shareUrl1","findPackage","location.href","window.location","router.push"]
    seen=set()
    for p in pats:
        for m in list(re.finditer(re.escape(p),s,re.I))[:80]:
            a=max(0,m.start()-700); z=min(len(s),m.end()+1600)
            ctx=s[a:z]
            key=ctx[:600]
            if key in seen: continue
            seen.add(key)
            print("\n###",p)
            print(ctx)
