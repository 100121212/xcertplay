import urllib.request, urllib.parse, json, time

UA={"User-Agent":"Mozilla/5.0"}

def get(url,timeout=45):
    req=urllib.request.Request(url,headers=UA)
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            b=r.read()
            s=b.decode("utf-8","replace")
            print("\nURL",url)
            print("STATUS",r.status,"TYPE",r.headers.get("content-type"),"BYTES",len(b),"FINAL",r.geturl())
            print(s[:180000])
            return s
    except Exception as e:
        print("\nURL",url)
        print("ERR",repr(e),"CODE",getattr(e,"code",None))
        try: print(e.read().decode("utf-8","replace")[:20000])
        except: pass
        return ""

print("===== INTERNET ARCHIVE ADVANCED SEARCH =====")
queries=[
    '"tw.app.idol"',
    '"tw.app.idol--ipa-1_0_1"',
    '"育ててアイドルの卵"',
    '"培養偶像之蛋"',
    '"851443895"',
    '("tw.app.idol" OR "851443895") AND mediatype:software',
    '("育ててアイドルの卵" OR "培養偶像之蛋") AND mediatype:software',
]
for q in queries:
    u="https://archive.org/advancedsearch.php?"+urllib.parse.urlencode({
        "q":q,
        "fl[]":["identifier","title","description","date","mediatype","downloads"],
        "rows":"100","page":"1","output":"json"
    },doseq=True)
    get(u)

print("\n===== WAYBACK CDX =====")
targets=[
    "www.pgyer.com/ipa/ipa/tw.app.idol*",
    "pgyer.com/ipa/ipa/tw.app.idol*",
    "www.pgyer.com/ipa/api/download?id=tw.app.idol",
    "assets.appmeme.com/tw.app.idol*",
    "assets.apk.live/tw.app.idol*",
    "storage.appmeme.com/*tw.app.idol*",
    "storage.appmeme.com/tw.app.idol*",
    "app.iwww.jp/apps/idol/*",
]
for target in targets:
    params={
        "url":target,
        "output":"json",
        "fl":"timestamp,original,statuscode,mimetype,digest,length",
        "filter":"statuscode:200",
        "collapse":"digest",
        "limit":"1000",
    }
    u="https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(params)
    get(u)

print("\n===== WAYBACK AVAILABILITY =====")
for target in [
    "https://www.pgyer.com/ipa/ipa/tw.app.idol",
    "http://app.iwww.jp/apps/idol/help.html",
    "https://storage.appmeme.com/tw.app.idol--ipa-1_0_1.ipa",
]:
    u="https://archive.org/wayback/available?"+urllib.parse.urlencode({"url":target})
    get(u)
