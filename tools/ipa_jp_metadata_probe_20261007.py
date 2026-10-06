import json, urllib.request, urllib.parse, urllib.error, re, concurrent.futures, time

UA={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/154 Safari/537.36"}

def fetch(url, timeout=45, headers=None):
    h=dict(UA)
    if headers: h.update(headers)
    req=urllib.request.Request(url,headers=h)
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            b=r.read()
            return r.status,r.geturl(),dict(r.headers),b
    except urllib.error.HTTPError as e:
        return e.code,e.geturl(),dict(e.headers),e.read()
    except Exception as e:
        return None,url,{},repr(e).encode()

def show(label,url,limit=160000,headers=None):
    st,final,h,b=fetch(url,headers=headers)
    print("\n===== "+label+" =====")
    print("URL",url)
    print("STATUS",st,"FINAL",final,"BYTES",len(b),"TYPE",h.get("Content-Type"))
    s=b.decode("utf-8","replace")
    print(s[:limit])
    return st,final,h,b

apple_urls=[
 ("ITUNES_LOOKUP_JP","https://itunes.apple.com/lookup?id=851443895&country=jp"),
 ("ITUNES_LOOKUP_JP_PATH","https://itunes.apple.com/jp/lookup?id=851443895"),
 ("ITUNES_SEARCH_JP","https://itunes.apple.com/search?term="+urllib.parse.quote("育ててアイドルの卵")+"&country=jp&entity=software&limit=50"),
 ("ITUNES_OLD_PAGE","https://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895?mt=8"),
 ("ITUNES_ID_PAGE","https://itunes.apple.com/jp/app/id851443895?mt=8"),
 ("MZ_VIEW_SOFTWARE","https://itunes.apple.com/WebObjects/MZStore.woa/wa/viewSoftware?id=851443895&mt=8"),
 ("APPLE_APPS_PAGE","https://apps.apple.com/jp/app/id851443895"),
]
for label,u in apple_urls:
    show(label,u)

# Wayback CDX exact and wildcard queries.
targets=[
 "https://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895?mt=8",
 "http://itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895?mt=8",
 "https://itunes.apple.com/jp/app/id851443895?mt=8",
 "http://itunes.apple.com/jp/app/id851443895?mt=8",
 "https://itunes.apple.com/lookup?id=851443895&country=jp",
 "http://itunes.apple.com/lookup?id=851443895&country=jp",
 "itunes.apple.com/jp/app/*/id851443895*",
 "apps.apple.com/jp/app/*/id851443895*",
]
all_caps=[]
for i,t in enumerate(targets):
    qs={
      "url":t,
      "output":"json",
      "filter":"statuscode:200",
      "fl":"timestamp,original,statuscode,mimetype,digest,length",
      "collapse":"digest",
      "limit":"200"
    }
    if "*" in t: qs["matchType"]="prefix" if t.endswith("*") and "*" not in t[:-1] else "domain"
    u="https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(qs)
    st,final,h,b=show("WAYBACK_CDX_"+str(i),u,250000)
    try:
        data=json.loads(b.decode("utf-8","replace"))
        if isinstance(data,list) and len(data)>1:
            hdr=data[0]
            for row in data[1:]:
                d=dict(zip(hdr,row)); all_caps.append(d)
    except Exception:
        pass

print("\n===== WAYBACK_CAPTURE_SUMMARY =====")
for d in all_caps[:500]:
    print(json.dumps(d,ensure_ascii=False))

# Fetch up to 20 promising archived snapshots and scan for identifiers.
seen=set()
prom=[]
for d in all_caps:
    key=(d.get("timestamp"),d.get("original"))
    if key in seen: continue
    seen.add(key)
    orig=d.get("original","")
    if "851443895" in orig:
        prom.append(d)
for d in prom[:20]:
    ts=d.get("timestamp"); orig=d.get("original")
    snap=f"https://web.archive.org/web/{ts}id_/{orig}"
    st,final,h,b=fetch(snap,60)
    print("\n===== WAYBACK_SNAPSHOT",ts,orig,"=====")
    print("STATUS",st,"FINAL",final,"BYTES",len(b),"TYPE",h.get("Content-Type"))
    s=b.decode("utf-8","replace")
    # Print only lines/windows with useful metadata terms.
    pats=["bundle","softwareVersionBundleId","CFBundleIdentifier","trackId","851443895","version","seller","artistId","fileSize","appExtVrsId"]
    found=False
    for p in pats:
        for m in list(re.finditer(re.escape(p),s,re.I))[:20]:
            found=True
            print("###",p, re.sub(r"\s+"," ",s[max(0,m.start()-700):min(len(s),m.end()+1800)]))
    if not found:
        print(s[:12000])

# Internet Archive advanced search.
queries=[
 '851443895',
 '"育ててアイドルの卵"',
 '"tw.app.idol"',
 '"com.app.idol" AND mediatype:software',
]
for i,q in enumerate(queries):
    params=[("q",q),("fl[]","identifier"),("fl[]","title"),("fl[]","description"),("fl[]","mediatype"),("rows","100"),("page","1"),("output","json")]
    u="https://archive.org/advancedsearch.php?"+urllib.parse.urlencode(params)
    show("IA_SEARCH_"+str(i),u,250000)

print("\n===== DONE =====")
