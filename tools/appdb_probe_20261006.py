import urllib.request, urllib.parse, json, sys

BASE="https://api.dbservices.to/v1.7/"
UA="Mozilla/5.0"

def post(path, data):
    body=urllib.parse.urlencode(data, doseq=True).encode()
    req=urllib.request.Request(BASE+path, data=body, headers={
        "User-Agent":UA,
        "Content-Type":"application/x-www-form-urlencoded",
        "Accept":"application/json",
    }, method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            b=r.read().decode("utf-8","replace")
            print("\n###", path, data, "STATUS", r.status)
            print(b[:200000])
            return b
    except Exception as e:
        print("\n###", path, data, "ERR",repr(e),"CODE",getattr(e,"code",None))
        try:
            print(e.read().decode("utf-8","replace")[:200000])
        except: pass
        return ""

tests=[
    {"type":"ios","name":"培養偶像之蛋","lang":"en","brand":"appdb"},
    {"type":"ios","name":"育ててアイドルの卵","lang":"en","brand":"appdb"},
    {"type":"ios","name":"tw.app.idol","lang":"en","brand":"appdb"},
    {"type":"ios","name":"idol","lang":"en","brand":"appdb"},
    {"type":"ios","developer_name":"Chronus Inc.","lang":"en","brand":"appdb"},
    {"name":"培養偶像之蛋","lang":"en","brand":"appdb"},
    {"name":"育ててアイドルの卵","lang":"en","brand":"appdb"},
    {"name":"tw.app.idol","lang":"en","brand":"appdb"},
    {"developer_name":"Chronus Inc.","lang":"en","brand":"appdb"},
]
results=[]
for t in tests:
    s=post("search_index/",t)
    try:
        j=json.loads(s)
        data=j.get("data")
        if isinstance(data,list):
            for x in data:
                if isinstance(x,dict):
                    results.append(x)
    except Exception:
        pass

print("\n=== UNIQUE CANDIDATES ===")
seen=set()
for x in results:
    key=x.get("universal_object_identifier") or x.get("id") or repr(x)
    if key in seen: continue
    seen.add(key)
    print(json.dumps(x,ensure_ascii=False)[:30000])

print("\n=== TARGET-LIKE UOIS ===")
uois=[]
for x in results:
    blob=json.dumps(x,ensure_ascii=False).lower()
    if any(k.lower() in blob for k in ["tw.app.idol","com.app.idol","851443895","培養偶像之蛋","育ててアイドルの卵","chronus"]):
        u=x.get("universal_object_identifier")
        if u and u not in uois: uois.append(u)
        print(json.dumps(x,ensure_ascii=False)[:50000])

for u in uois[:20]:
    print("\n=== UNIVERSAL GATEWAY",u,"===")
    post("universal_gateway/",{"universal_object_identifier":u,"lang":"en","brand":"appdb"})
