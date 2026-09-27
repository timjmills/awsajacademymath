# Compare catalogue (master.json) with the clean listing (list2/f_*.json). Writes stage2/report.json
import json,glob,os,re,collections
S=os.path.dirname(os.path.abspath(__file__)); os.makedirs(S+'/stage2',exist_ok=True)
F=[]
for i in range(6): F+=json.load(open(f'{S}/list2/folders_{i}.json'))
files={}; folders_done=set(); byfolder=collections.defaultdict(list)
for p in glob.glob(S+'/list2/f_*.json'):
    d=json.load(open(p)); folders_done.add(d['folder_id'])
    for f in d['files']:
        if f.get('mimeType')=='application/vnd.google-apps.folder': continue
        f['folder_id']=d['folder_id']; files[f['id']]=f; byfolder[d['folder_id']].append(f)
print('folders listed',len(folders_done),'/',len(F),' files',len(files))
M=json.load(open(S+'/master.json'))
def key_title(t): return re.sub(r' - Worksheets?\.pdf$',' - Answer Key.pdf',t)
def norm(t): return re.sub(r'\s+',' ',t or '').strip().lower()
R=collections.defaultdict(list)
for e in M.values():
    f=files.get(e['id'])
    if not f:
        R['catalogue_id_not_in_listing'].append(e['id']); continue
    if norm(f['title'])!=norm(e.get('title')): R['title_differs'].append((e['id'],e.get('title'),f['title']))
    e['folder_id']=f['folder_id']
    want=norm(key_title(f['title']))
    keys=[x for x in byfolder[f['folder_id']] if norm(x['title'])==want]
    right=keys[0]['id'] if keys else None
    if (e.get('answer_key_id') or None)!=right:
        R['answer_key_fixed'].append((e['id'],e.get('answer_key_id'),right,e.get('text_ok')))
        if e.get('text_ok')=='answer key': R['described_from_wrong_key'].append(e['id'])
        e['answer_key_id']=right
catalogued=set(M)
for fid,f in files.items():
    t=f['title']
    if t.endswith('Answer Key.pdf'): continue
    if fid not in catalogued: R['listed_but_not_catalogued'].append((fid,t,f['folder_id']))
dups=collections.Counter(norm(files[i]['title']) for i in catalogued if i in files)
json.dump(M,open(S+'/stage2/master_fixed.json','w'))
json.dump(R,open(S+'/stage2/report.json','w'),indent=1)
for k,v in R.items(): print(k,len(v))
