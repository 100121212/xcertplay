import re, urllib.request, urllib.error, json, sys, time

BASE="https://www.pgyer.com"
PATHS=[
 "/ipa/ipa/tw.app.idol",
 "/ipa/ipa/tw.app.idol/download",
 "/ipa/ipa/tw.app.idol/downloading",
 "/ipa/ja/ipa/tw.app.idol",
 "/ipa/ja/ipa/tw.app.idol/download",
 "/ipa/ja/ipa/tw.app.idol/downloading",
]
UA={"User-Agent":"Mozilla/5.0"}

def fetch(url, headers=None, timeout=40):
    h=dict(UA)
    if headers: h.update(headers)
    req=urllib.request.Request(url,headers=h)
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            b=r.read()
            return r.status, r.geturl(), dict(r.headers), b
    except urllib.error.HTTPError as e:
        b=e.read()
        return e.code, e.geturl(), dict(e.headers), b
    except Exception as e:
        return None, url, {}, repr(e).encode()

for path in PATHS:
    url=BASE+path
    print("\n===== PAGE",url,"=====")
    status,final,h,b=fetch(url)
    print("STATUS",status,"FINAL",final,"BYTES",len(b),"TYPE",h.get("Content-Type"),"LOC",h.get("Location"))
    s=b.decode("utf-8","replace")
    for key in ["oss_object_name_apk","oss_object_name_xapk","shareUrl1","storage.appmeme.com",".ipa","download","downloading","tw.app.idol"]:
        ms=list(re.finditer(re.escape(key),s,re.I))
        print("KEY",key,"COUNT",len(ms))
        for m in ms[:20]:
            print(s[max(0,m.start()-350):min(len(s),m.end()+900)].replace("\n"," ")[:1600])
            print("---")

    # RSC-ish fetch
    print("===== RSC",url,"=====")
    status2,final2,h2,b2=fetch(url,{"RSC":"1","Next-Router-Prefetch":"1","Next-Router-State-Tree":"%5B%22%22%2C%7B%22children%22%3A%5B%22ipa%22%2C%7B%22children%22%3A%5B%22ipa%22%2C%7B%22children%22%3A%5B%5B%22id%22%2C%22tw.app.idol%22%2C%22d%22%5D%2C%7B%22children%22%3A%5B%22__PAGE__%22%2C%7B%7D%5D%7D%5D%7D%5D%7D%5D%7D%2Cnull%2Cnull%2Ctrue%5D"})
    print("RSC_STATUS",status2,"BYTES",len(b2),"TYPE",h2.get("Content-Type"))
    rs=b2.decode("utf-8","replace")
    for key in ["oss_object_name_apk","shareUrl1","storage.appmeme.com",".ipa","tw.app.idol"]:
        for m in list(re.finditer(re.escape(key),rs,re.I))[:20]:
            print("RSC_KEY",key,rs[max(0,m.start()-350):min(len(rs),m.end()+900)].replace("\n"," ")[:1600])
            print("---")

    # Fetch JS chunks referenced by this page.
    jsurls=sorted(set(re.findall(r'https://apkhub-static\.appmeme\.com/[^"\'<>\s]+?\.js',s)))
    print("JS_COUNT",len(jsurls))
    chunks=[]
    for u in jsurls:
        st,fi,hh,bb=fetch(u)
        if st==200:
            chunks.append((u,bb.decode("utf-8","replace")))
    joined="\n".join(x[1] for x in chunks)
    for key in ["oss_object_name_apk","shareUrl1","storage.appmeme.com","/download","/downloading",".ipa","findPackage"]:
        ms=list(re.finditer(re.escape(key),joined,re.I))
        if ms:
            print("JSKEY",key,"COUNT",len(ms))
            for m in ms[:40]:
                print(joined[max(0,m.start()-500):min(len(joined),m.end()+1100)].replace("\n"," ")[:2000])
                print("---")
