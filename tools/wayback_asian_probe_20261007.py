import subprocess, urllib.parse, time

queries=[
 ("25pp.com","851443895"),("25pp.com","com.app.idol"),
 ("tongbu.com","851443895"),("tongbu.com","com.app.idol"),
 ("kuaiyong.com","851443895"),("kuaiyong.com","com.app.idol"),
 ("i4.cn","851443895"),("i4.cn","com.app.idol"),
 ("91.com","851443895"),("91.com","com.app.idol"),
 ("itools.cn","851443895"),("itools.cn","com.app.idol"),
 ("chronusinc.jp","idol"),("chronusinc.jp","851443895"),
 ("app.iwww.jp","apps/idol"),("app.iwww.jp","idol"),
]
for domain,needle in queries:
    params={
      "url":domain,"matchType":"domain","from":"2014","to":"2019",
      "output":"json","limit":"100","filter":"original:"+needle,
      "fl":"timestamp,original,statuscode,mimetype,digest"
    }
    url="https://web.archive.org/cdx/search/cdx?"+urllib.parse.urlencode(params)
    print("\n###",domain,needle,url,flush=True)
    p=subprocess.run(
      ["curl","-L","-sS","--max-time","12","-A","Mozilla/5.0 archival-research",url],
      capture_output=True,text=True
    )
    print("RC",p.returncode,"OUT_BYTES",len(p.stdout),"ERR",p.stderr.strip(),flush=True)
    print(p.stdout[:30000],flush=True)
    time.sleep(2)
