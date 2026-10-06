import urllib.request, urllib.parse, json, concurrent.futures, re

UA={"User-Agent":"Mozilla/5.0"}

def get(url, timeout=45):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return r.read(), dict(r.headers), r.geturl(), r.status

print("=== STAHUJ / SLUNECNICE ===")
for u in [
    "https://www.stahuj.cz/ios/zabava/yuteteaidoruno-luan/",
    "https://www.slunecnice.cz/ios/sw/yuteteaidoruno-luan/",
    "https://www.slunecnice.cz/ios/sw/pei-yang-ou-xiang-zhi-dan/",
]:
    print("\n---",u)
    try:
        b,h,final,status=get(u)
        s=b.decode("utf-8","replace")
        print("STATUS",status,"BYTES",len(b),"FINAL",final)
        urls=sorted(set(re.findall(r'https?://[^"\'<>\s]+',s)))
        for x in urls:
            if any(k in x.lower() for k in ["itunes","apple","download","ipa","851443895","tw.app.idol","chronus"]):
                print("URL",x)
        for token in ["download","stáhnout","app store","itunes","851443895","tw.app.idol"]:
            for m in list(re.finditer(re.escape(token),s,re.I))[:20]:
                print("CTX",token,s[max(0,m.start()-350):min(len(s),m.end()+700)].replace("\n"," "))
    except Exception as e:
        print("ERR",repr(e))

print("\n=== WAYBACK ===")
for q in ["*tw.app.idol*","*851443895*","*yuteteaidoruno-luan*","*tw.app.idol*.ipa","*851443895*.ipa"]:
    print("\n---",q)
    url="https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode({
        "url":q,
        "output":"json",
        "fl":"timestamp,original,statuscode,mimetype,digest,length",
        "filter":"statuscode:200",
        "collapse":"urlkey",
        "limit":"2000",
    })
    try:
        b,h,final,status=get(url,90)
        print("STATUS",status,"BYTES",len(b))
        print(b.decode("utf-8","replace")[:300000])
    except Exception as e:
        print("ERR",repr(e))

print("\n=== COMMON CRAWL ===")
try:
    cols=json.loads(get("https://index.commoncrawl.org/collinfo.json",30)[0])
except Exception as e:
    print("COLLINFO_ERR",repr(e))
    cols=[]

ids=[x["id"] for x in cols if x["id"][8:12] in {"2014","2015","2016","2017","2018","2019","2020","2021","2022","2023","2024","2025","2026"}]
queries=["*tw.app.idol*","*851443895*","*yuteteaidoruno-luan*"]

def work(args):
    cid,q=args
    url="https://index.commoncrawl.org/"+cid+"-index?"+urllib.parse.urlencode({
        "url":q,
        "output":"json",
        "filter":"status:200",
        "pageSize":"200",
    })
    try:
        b,h,final,status=get(url,25)
        s=b.decode("utf-8","replace").strip()
        if s and "No Captures found" not in s:
            return cid,q,s[:120000]
    except Exception:
        return None

jobs=[(c,q) for c in ids for q in queries]
print("CC_COLLECTIONS",len(ids),"QUERIES",len(jobs))
with concurrent.futures.ThreadPoolExecutor(max_workers=18) as ex:
    for r in ex.map(work,jobs):
        if r:
            print("\nFOUND",r[0],r[1])
            print(r[2])
