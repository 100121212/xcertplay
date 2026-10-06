import re, urllib.request, urllib.parse, json

UA={"User-Agent":"Mozilla/5.0"}
base="https://api.dbservices.to/v1.7/"

def fetch(url):
    req=urllib.request.Request(url,headers=UA)
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            b=r.read()
            print("\nURL",url,"STATUS",r.status,"TYPE",r.headers.get("content-type"),"BYTES",len(b),"FINAL",r.geturl())
            return b.decode("utf-8","replace")
    except Exception as e:
        print("\nURL",url,"ERR",repr(e),"CODE",getattr(e,"code",None))
        return ""

spec=fetch(base+"spec/")
print("\n=== SPEC HEAD ===")
print(spec[:15000])

print("\n=== SPEC URLS ===")
for u in sorted(set(re.findall(r'https?://[^"\'<>\s]+',spec))):
    print(u[:2000])

print("\n=== SPEC ASSET REFS ===")
for s in sorted(set(re.findall(r'[^"\'<>\s]+\.(?:json|ya?ml|js)(?:\?[^"\'<>\s]*)?',spec,re.I))):
    print(s[:2000])

candidates=[
    base+"openapi.json", base+"swagger.json", base+"spec.json",
    base+"openapi.yaml", base+"openapi.yml",
    base+"spec/openapi.json", base+"spec/swagger.json",
    base+"spec/openapi.yaml", base+"spec/openapi.yml",
    base+"spec/api.json", base+"spec/spec.json",
]
docs={}
for u in candidates:
    s=fetch(u)
    if s and not s.lstrip().lower().startswith("<!doctype html"):
        docs[u]=s

for u,s in docs.items():
    print("\n=== DOC",u,"SEARCH CONTEXT ===")
    for token in ["search","get_links","bundle_ids","trackids","universal_object_identifier","type"]:
        ms=list(re.finditer(re.escape(token),s,re.I))
        if ms:
            print("\n##",token,"COUNT",len(ms))
            for m in ms[:40]:
                print(s[max(0,m.start()-600):min(len(s),m.end()+1600)])

print("\n=== DIRECT ENDPOINT PROBES ===")
endpoints=["search/","get_links/","search","get_links"]
params=[
    {"type":"ios","bundle_ids":"tw.app.idol"},
    {"type":"ios","bundle_ids":"com.app.idol"},
    {"type":"ios","trackids":"851443895"},
    {"type":"ios","query":"培養偶像之蛋"},
]
for ep in endpoints:
    for p in params:
        q=urllib.parse.urlencode(p)
        u=base+ep+"?"+q
        s=fetch(u)
        if s:
            print("BODY",s[:12000])
