import json, urllib.request, urllib.parse, urllib.error, concurrent.futures, gzip, io, re

UA={"User-Agent":"Mozilla/5.0"}
def get(url,timeout=20,headers=None):
    h=dict(UA)
    if headers: h.update(headers)
    req=urllib.request.Request(url,headers=h)
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            return r.status,dict(r.headers),r.read()
    except Exception as e:
        return None,{},repr(e).encode()

st,h,b=get("https://index.commoncrawl.org/collinfo.json",20)
print("COLLINFO",st,len(b))
cols=json.loads(b.decode())
ids=[x["id"] for x in cols if any(x["id"].startswith("CC-MAIN-"+y) for y in ["2014","2015","2016","2017","2018","2019"])]
print("COLLECTIONS",len(ids),ids)

targets=[
 "https://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895?mt=8",
 "http://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895?mt=8",
 "https://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895",
 "http://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895",
 "itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895?mt=8",
 "itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895",
]

def query(job):
    cid,target=job
    u="https://index.commoncrawl.org/"+cid+"-index?"+urllib.parse.urlencode({"url":target,"output":"json"})
    st,h,b=get(u,15)
    s=b.decode("utf-8","replace").strip()
    out=[]
    if st==200 and s and "No Captures found" not in s:
        for line in s.splitlines():
            try:
                j=json.loads(line)
                if "851443895" in j.get("url","") or "851443895" in target:
                    out.append(j)
            except Exception:
                pass
    return cid,target,st,out,s[:300]

jobs=[(c,t) for c in ids for t in targets]
found=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
    for cid,target,st,out,raw in ex.map(query,jobs):
        if out:
            print("\nFOUND_INDEX",cid,target,"COUNT",len(out))
            for j in out:
                print(json.dumps(j,ensure_ascii=False))
                found.append((cid,j))

print("\nTOTAL_FOUND",len(found))

seen=set()
for cid,j in found:
    key=(j.get("filename"),j.get("offset"),j.get("length"))
    if key in seen: continue
    seen.add(key)
    fn,off,ln=j.get("filename"),int(j.get("offset",0)),int(j.get("length",0))
    if not fn or not ln: continue
    url="https://data.commoncrawl.org/"+fn
    headers={"Range":f"bytes={off}-{off+ln-1}"}
    st,h,b=get(url,30,headers)
    print("\n===== WARC",cid,j.get("timestamp"),j.get("url"),"=====")
    print("RANGE",off,ln,"STATUS",st,"BYTES",len(b),"TYPE",h.get("Content-Type"))
    try:
        raw=gzip.decompress(b)
    except Exception as e:
        print("GZIP_ERR",repr(e),b[:80])
        continue
    print("RAW_BYTES",len(raw))
    # Split WARC headers and HTTP response.
    s=raw.decode("utf-8","replace")
    print("RAW_HEAD",re.sub(r"\s+"," ",s[:1000]))
    terms=["bundleId","softwareVersionBundleId","CFBundleIdentifier","appExtVrsId","851443895","com.app.idol","version","sellerName","artistName","product-header","application-name"]
    hit=False
    for term in terms:
        ms=list(re.finditer(re.escape(term),s,re.I))
        if ms:
            hit=True
            print("\nTERM",term,"COUNT",len(ms))
            for m in ms[:30]:
                print(re.sub(r"\s+"," ",s[max(0,m.start()-900):min(len(s),m.end()+2500)]))
    if not hit:
        print(s[:20000])
