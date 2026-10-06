import urllib.request, urllib.parse, json

BASE="https://api.dbservices.to/v1.7/"
UA="Mozilla/5.0"

def post(path,data):
    body=urllib.parse.urlencode(data).encode()
    req=urllib.request.Request(BASE+path,data=body,headers={
        "User-Agent":UA,
        "Content-Type":"application/x-www-form-urlencoded",
        "Accept":"application/json",
    },method="POST")
    try:
        with urllib.request.urlopen(req,timeout=30) as r:
            s=r.read().decode("utf-8","replace")
            print("\nQUERY",data,"STATUS",r.status)
            print(s[:120000])
            return json.loads(s)
    except Exception as e:
        print("\nQUERY",data,"ERR",repr(e))
        return {}

types=["official_app","repo_app","user_app","enhancement"]
queries=[
    ("name","育ててアイドルの卵"),
    ("name","培養偶像之蛋"),
    ("name","tw.app.idol"),
    ("developer_name","Chronus Inc."),
    ("developer_name","Chronus"),
]
found=[]
for typ in types:
    for key,val in queries:
        d={"type":typ,key:val,"brand":"appdb","lang":"en"}
        j=post("search_index/",d)
        arr=j.get("data",[])
        if isinstance(arr,list):
            for x in arr:
                if isinstance(x,dict):
                    x["_matched_by"]=d
                    found.append(x)

print("\n=== UNIQUE RESULTS ===")
seen=set()
for x in found:
    k=x.get("universal_object_identifier") or (x.get("id"),x.get("name"),x.get("type"))
    k=str(k)
    if k in seen: continue
    seen.add(k)
    print(json.dumps(x,ensure_ascii=False)[:60000])

print("\n=== GATEWAY FOR TARGET-LIKE RESULTS ===")
used=set()
for x in found:
    blob=json.dumps(x,ensure_ascii=False).lower()
    if not any(k in blob for k in ["育ててアイドルの卵","培養偶像之蛋","tw.app.idol","com.app.idol","851443895","chronus"]):
        continue
    u=x.get("universal_object_identifier")
    if not u or u in used: continue
    used.add(u)
    print("\nUOI",u)
    j=post("universal_gateway/",{"universal_object_identifier":u,"brand":"appdb","lang":"en"})
    print("GATEWAY",json.dumps(j,ensure_ascii=False)[:120000])
