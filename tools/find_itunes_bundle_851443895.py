import json, urllib.request, urllib.parse, re, concurrent.futures, gzip, io

UA={"User-Agent":"Mozilla/5.0"}
TARGETS=[
 "https://itunes.apple.com/jp/app/id851443895",
 "https://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895",
 "http://itunes.apple.com/jp/app/id851443895",
 "http://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895",
 "https://itunes.apple.com/lookup?id=851443895&country=jp",
 "http://itunes.apple.com/lookup?id=851443895&country=jp",
 "https://itunes.apple.com/jp/lookup?id=851443895",
 "http://itunes.apple.com/jp/lookup?id=851443895",
]

def get(url, timeout=25, headers=None):
    h=dict(UA)
    if headers: h.update(headers)
    req=urllib.request.Request(url,headers=h)
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read(), dict(r.headers), r.status, r.geturl()

print("=== WAYBACK CDX ===")
for u in TARGETS:
    q="https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode({
        "url":u,
        "output":"json",
        "filter":"statuscode:200",
        "fl":"timestamp,original,digest,mimetype,statuscode",
        "collapse":"digest",
    })
    try:
        b,h,st,final=get(q,30)
        print("\nTARGET",u,"STATUS",st,"BYTES",len(b))
        print(b.decode("utf-8","replace")[:50000])
    except Exception as e:
        print("\nTARGET",u,"ERR",repr(e))

print("\n=== COMMON CRAWL ===")
try:
    cols=json.loads(get("https://index.commoncrawl.org/collinfo.json",30)[0])
except Exception as e:
    print("COLLINFO_ERR",repr(e))
    cols=[]

ids=[x["id"] for x in cols if re.match(r"CC-MAIN-(2014|2015|2016|2017|2018|2019|2020)",x["id"])]
# one representative crawl per quarter-ish to reduce load, plus all if few
selected=[]
lastyrmon=set()
for cid in ids:
    m=re.match(r"CC-MAIN-(\d{4})-(\d+)",cid)
    if not m: continue
    y=int(m.group(1)); w=int(m.group(2))
    bucket=(y,(w-1)//13)
    if bucket not in lastyrmon:
        lastyrmon.add(bucket); selected.append(cid)
print("COLLECTIONS",selected)

def ccq(args):
    cid,u=args
    q="https://index.commoncrawl.org/"+cid+"-index?"+urllib.parse.urlencode({"url":u,"output":"json"})
    try:
        b,h,st,final=get(q,20)
        s=b.decode("utf-8","replace").strip()
        if s and "No Captures found" not in s and "No index found" not in s:
            return cid,u,s
    except Exception:
        return None

jobs=[(cid,u) for cid in selected for u in TARGETS]
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    for res in ex.map(ccq,jobs):
        if res:
            cid,u,s=res
            print("\nCC_FOUND",cid,u)
            print(s[:50000])
