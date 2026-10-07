import json,urllib.request,urllib.parse,concurrent.futures,sys
UA={'User-Agent':'Mozilla/5.0'}
def getjson(url, timeout=20):
    req=urllib.request.Request(url,headers=UA)
    with urllib.request.urlopen(req,timeout=timeout) as r:
        return json.load(r)
cols=getjson('https://index.commoncrawl.org/collinfo.json')
ids=[x['id'] for x in cols if x['id'].startswith('CC-MAIN-') and x['id'][8:12] in {'2014','2015','2016','2017','2018','2019'}]
targets=[
 'itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895',
 'itunes.apple.com/jp/app/yuteteaidoruno-luan/id851443895?mt=8',
 'itunes.apple.com/lookup?id=851443895',
 'itunes.apple.com/jp/lookup?id=851443895',
 'app.iwww.jp/apps/idol/help.html',
 'app.iwww.jp/apps/idol/fin.html',
 'app.iwww.jp/apps/idol/'
]
def one(job):
    cid,u=job
    params={'url':u,'output':'json'}
    if u.endswith('/'): params['matchType']='prefix'
    q=f'https://index.commoncrawl.org/{cid}-index?'+urllib.parse.urlencode(params)
    try:
        req=urllib.request.Request(q,headers=UA)
        with urllib.request.urlopen(req,timeout=15) as r:
            s=r.read().decode('utf-8','replace').strip()
        if s and 'No Captures found' not in s:
            return {'collection':cid,'target':u,'body':s[:50000]}
    except Exception as e:
        return None
jobs=[(c,u) for c in ids for u in targets]
print('COLLECTIONS',len(ids),'QUERIES',len(jobs))
hits=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
    for r in ex.map(one,jobs):
        if r:
            hits.append(r)
            print('\nFOUND',r['collection'],r['target'])
            print(r['body'])
print('\nTOTAL_HITS',len(hits))
