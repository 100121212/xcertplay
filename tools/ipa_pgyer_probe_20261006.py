import re, urllib.request, urllib.parse, http.cookiejar, json, sys

BASE = "https://www.pgyer.com"
PATHS = [
    "/ipa/ipa/tw.app.idol",
    "/ipa/ipa/tw.app.idol/download",
    "/ipa/ipa/tw.app.idol/downloading",
]
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/154 Safari/537.36"

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def fetch(url, referer=None, range_header=None):
    h={"User-Agent":UA, "Accept-Language":"en-US,en;q=0.9"}
    if referer: h["Referer"]=referer
    if range_header: h["Range"]=range_header
    req=urllib.request.Request(url, headers=h)
    with opener.open(req, timeout=45) as r:
        return r.read(), dict(r.headers), r.geturl(), r.status

pages={}
referer=None
for path in PATHS:
    url=BASE+path
    print("\n===== FETCH",url,"=====")
    try:
        b,h,final,status=fetch(url,referer)
        s=b.decode("utf-8","replace")
        pages[path]=s
        print("STATUS",status,"BYTES",len(b),"FINAL",final)
        print("CONTENT_TYPE",h.get("Content-Type"))
        print("COOKIES",[(c.name,c.value[:24],c.domain) for c in jar])
        referer=final

        for key in [
            "oss_object_name_apk","oss_object_name_xapk","shareUrl1",
            "storage.appmeme.com","downloadUrl","download_url",
            "tw.app.idol","1.0.1","1_0_1"
        ]:
            ms=list(re.finditer(re.escape(key),s,re.I))
            if ms:
                print("\n-- KEY",key,"COUNT",len(ms))
                for m in ms[:30]:
                    print(s[max(0,m.start()-700):min(len(s),m.end()+1600)])

        print("\n-- ABS URLS --")
        urls=sorted(set(re.findall(r'https?://[^"\'<>\\\s)]+',s)))
        for u in urls:
            if any(x in u.lower() for x in ["storage.appmeme","apk.live","appmeme","download",".ipa"]):
                print(u[:2000])

        print("\n-- CANDIDATE JSON OBJECTS --")
        for patt in [
            r'"oss_object_name_apk"\s*:\s*"([^"]+)"',
            r'\\?"oss_object_name_apk\\?"\s*:\s*\\?"([^"\\]+)',
            r'"shareUrl1"\s*:\s*"([^"]+)"',
            r'\\?"shareUrl1\\?"\s*:\s*\\?"([^"\\]+)',
        ]:
            for v in re.findall(patt,s,re.I)[:100]:
                print(patt,"=>",v)

    except Exception as e:
        print("FETCH_ERR",repr(e))

# Collect object names from all pages.
alltext="\n".join(pages.values())
names=set()
for patt in [
    r'"oss_object_name_apk"\s*:\s*"([^"]+)"',
    r'\\?"oss_object_name_apk\\?"\s*:\s*\\?"([^"\\]+)',
]:
    names.update(re.findall(patt,alltext,re.I))

# Also infer likely object names from icon convention.
guesses=[
    "tw.app.idol--ipa-1_0_1.ipa",
    "tw.app.idol--ipa-1_0_1",
    "tw.app.idol--ipa-1.0.1.ipa",
    "tw.app.idol--ipa-1_0_1-apk.ipa",
]
names.update(guesses)

print("\n===== STORAGE PROBES =====")
for name in sorted(names):
    for host in ["https://storage.appmeme.com/","https://storage.apk.live/"]:
        u=host+name.lstrip("/")
        try:
            b,h,final,status=fetch(u,BASE+"/ipa/ipa/tw.app.idol/downloading","bytes=0-63")
            print("OK",status,"URL",u,"FINAL",final,"TYPE",h.get("Content-Type"),"LEN",h.get("Content-Length"),"RANGE",h.get("Content-Range"),"HEX",b[:16].hex(),"ASCII",repr(b[:32]))
        except Exception as e:
            code=getattr(e,"code",None)
            hdr=getattr(e,"headers",None)
            print("ERR",code,u,"LOC",hdr.get("Location") if hdr else None,repr(e))


print("\n===== DOWNLOAD API PROBE =====")
api = "https://www.pgyer.com/ipa/api/download?id=tw.app.idol"
try:
    b,h,final,status=fetch(api, BASE+"/ipa/ipa/tw.app.idol/download", "bytes=0-127")
    print("API_STATUS",status)
    print("API_FINAL",final)
    for k,v in h.items():
        if k.lower() in ["content-type","content-length","content-range","content-disposition","location","etag","last-modified","accept-ranges"]:
            print("HDR",k,":",v)
    print("API_HEX",b[:32].hex())
    print("API_ASCII",repr(b[:64]))
except Exception as e:
    print("API_ERR",repr(e))
    code=getattr(e,"code",None)
    hdr=getattr(e,"headers",None)
    if code is not None: print("API_CODE",code)
    if hdr:
        for k,v in hdr.items():
            if k.lower() in ["content-type","content-length","content-range","content-disposition","location","etag","last-modified","accept-ranges"]:
                print("ERR_HDR",k,":",v)
