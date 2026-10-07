import urllib.request,re,json,html
UA={"User-Agent":"Mozilla/5.0"}
pages=[
 "https://www.pgyer.com/ipa/ipa/tw.app.idol/download",
 "https://www.pgyer.com/ipa/ipa/tw.app.idol/downloading",
]
def get(u):
    req=urllib.request.Request(u,headers=UA)
    with urllib.request.urlopen(req,timeout=30) as r:return r.read().decode("utf-8","replace")
for u in pages:
    s=get(u)
    print("\n===== PAGE",u,"BYTES",len(s),"=====")
    # all hrefs
    print("=== HREFS mentioning target/download/storage ===")
    for x in sorted(set(re.findall(r'href="([^"]+)"',s))):
        if any(k in x.lower() for k in ["idol","download","storage","ipa"]):
            print(x)
    # absolute urls
    print("=== ABS URLS interesting ===")
    for x in sorted(set(re.findall(r'https?://[^"<>\\\s]+',s))):
        if any(k in x.lower() for k in ["idol","storage","appmeme","download","ipa"]):
            print(x[:1200])
    # contexts
    print("=== SERIALIZED PROP CONTEXTS ===")
    for p in ['"url":','\\\"url\\\":','"delay":','\\\"delay\\\":','"package":','\\\"package\\\":','1.0.1','tw.app.idol','downloading']:
        ms=list(re.finditer(re.escape(p),s,re.I))
        print("PAT",p,"COUNT",len(ms))
        for m in ms[:80]:
            print(s[max(0,m.start()-1000):min(len(s),m.end()+2200)])
            print("---")
