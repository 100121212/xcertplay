import urllib.request,re,html

URLS=[
 "https://www.pgyer.com/ipa/ipa/tw.app.idol/downloading",
 "https://www.pgyer.com/ipa/ja/ipa/tw.app.idol/downloading",
]
UA={"User-Agent":"Mozilla/5.0"}

for u in URLS:
    print("\n====",u,"====")
    req=urllib.request.Request(u,headers=UA)
    with urllib.request.urlopen(req,timeout=40) as r:
        b=r.read()
        print("STATUS",r.status,"FINAL",r.geturl(),"BYTES",len(b),"TYPE",r.headers.get("content-type"))
    s=b.decode("utf-8","replace")
    print("MODULE 50529 mappings:")
    for m in re.finditer(r'([0-9a-z]+):I\[50529,',s,re.I):
        ident=m.group(1)
        print("IDENT",ident)
        needles=[f'$L{ident}', f'\\\"$L{ident}\\\"', f'"$L{ident}"']
        for nd in needles:
            for mm in list(re.finditer(re.escape(nd),s))[:30]:
                print("USE",nd)
                print(s[max(0,mm.start()-1200):min(len(s),mm.end()+4000)])
                print("---")
    print("\nALL url props:")
    patterns=[
      r'url\\":\\"([^\"]+)',
      r'"url":"([^"]+)',
      r'url\":\"([^"]+)',
      r'url\\u0022:\\u0022([^\"]+)'
    ]
    vals=[]
    for p in patterns:
      for m in re.finditer(p,s):
        vals.append(m.group(1))
    for v in sorted(set(vals)):
      print("URLPROP",html.unescape(v.replace("\\/","/").replace("\\u0026","&").replace("\\u003d","=")))
    print("\nABS urls containing package-ish tokens:")
    x=s.replace("\\/","/").replace("\\u0026","&").replace("\\u003d","=")
    for z in sorted(set(re.findall(r'https?://[^"\'<>\\s]+',x))):
      if any(k in z.lower() for k in ["storage","appmeme","idol",".ipa","download"]):
        print("ABS",html.unescape(z))
