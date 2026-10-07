import json, urllib.request, urllib.parse, re, concurrent.futures, gzip, io

UA={"User-Agent":"Mozilla/5.0"}
TARGETS=[
 "https://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895?mt=8",
 "http://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895?mt=8",
 "https://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895",
 "http://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895",
 "https://itunes.apple.com/jp/app/id851443895?mt=8",
 "https://itunes.apple.com/lookup?id=851443895&country=jp",
 "http://itunes.apple.com/lookup?id=851443895&country=jp",
]

def get(url,timeout=20,headers=None):
    h=dict(UA)
    if headers: h.update(headers)
    req=urllib.request.Request(url,headers=h)
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read(),dict(r.headers),r.status,r.geturl()

cols=json.loads(get("https://index.commoncrawl.org/collinfo.json",30)[0])
ids=[x["id"] for x in cols if re.match(r"CC-MAIN-(2014|2015|2016|2017|2018|2019|2020)",x["id"])]
print("COLLECTION_COUNT",len(ids),flush=True)

def query(args):
    cid,u=args
    q="https://index.commoncrawl.org/"+cid+"-index?"+urllib.parse.urlencode({"url":u,"output":"json"})
    try:
        b,h,st,final=get(q,15)
        s=b.decode("utf-8","replace").strip()
        rows=[]
        for line in s.splitlines():
            try:
                x=json.loads(line)
                if x.get("status")=="200" or x.get("status") is None:
                    rows.append(x)
            except: pass
        return cid,u,rows
    except Exception as e:
        return cid,u,[]

hits=[]
jobs=[(cid,u) for cid in ids for u in TARGETS]
with concurrent.futures.ThreadPoolExecutor(max_workers=24) as ex:
    for cid,u,rows in ex.map(query,jobs):
        for x in rows:
            hits.append((cid,u,x))
            print("HIT",cid,u,json.dumps(x,ensure_ascii=False),flush=True)

print("TOTAL_HITS",len(hits),flush=True)

# Deduplicate identical WARC locations.
seen=set()
for cid,u,x in hits:
    key=(x.get("filename"),x.get("offset"),x.get("length"))
    if not all(key) or key in seen: continue
    seen.add(key)
    warc="https://data.commoncrawl.org/"+x["filename"]
    off=int(x["offset"]); ln=int(x["length"])
    print("\nFETCH_WARC",cid,x.get("timestamp"),x.get("url"),warc,off,ln,flush=True)
    try:
        raw,h,st,final=get(warc,30,{"Range":f"bytes={off}-{off+ln-1}"})
        try:
            data=gzip.decompress(raw)
        except Exception:
            data=raw
        text=data.decode("utf-8","replace")
        print("WARC_BYTES",len(data),flush=True)
        # Print only useful contexts.
        keys=["bundleId","bundleid","softwareVersionBundleId","CFBundleIdentifier","851443895","育ててアイドルの卵","Chronus","GMO PLAY MUSIC","com.app.idol","jp.app.idol"]
        found=False
        for k in keys:
            ms=list(re.finditer(re.escape(k),text,re.I))
            if ms:
                found=True
                print("KEY",k,"COUNT",len(ms),flush=True)
                for m in ms[:20]:
                    print(text[max(0,m.start()-800):min(len(text),m.end()+2400)].replace("\x00",""),flush=True)
                    print("---",flush=True)
        if not found:
            # Still print body tail/head around HTTP payload for manual inspection.
            print("NO_KEY_MATCH_SAMPLE",text[:8000],flush=True)
    except Exception as e:
        print("WARC_ERR",repr(e),flush=True)
