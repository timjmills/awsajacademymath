# Merge catalogue + visual fixes -> master.json and compact catalogue.tsv; prints status
import json,glob,os,re,collections
S=os.path.dirname(os.path.abspath(__file__))
M={}
def load(p):
    for l in open(p):
        l=l.strip()
        if not l: continue
        try: e=json.loads(l)
        except Exception: print('BAD LINE',p); continue
        yield e
for p in sorted(glob.glob(S+'/cat/batch_*.jsonl')):
    for e in load(p): e['_src']=os.path.basename(p); M[e['id']]=e
fixed=0
for p in sorted(glob.glob(S+'/vis/fixed_*.jsonl')):
    for e in load(p):
        if e['id'] in M:
            base=M[e['id']]; base.update({k:v for k,v in e.items() if k not in ('id',)}); base['_vis']=1; fixed+=1
        else: M[e['id']]=e
def gnum(g):
    g=str(g); m=re.search(r'(K|\d)',g.replace('Kindergarten','K'))
    return 'K' if m and m.group(1)=='K' else ('G'+m.group(1) if m else '?')
for e in M.values(): e['g']=gnum(e.get('grade') or e.get('title',''))
json.dump(M,open(S+'/master.json','w'))
st=collections.Counter(str(e.get('text_ok')) for e in M.values())
print('worksheets',len(M),'fixed applied',fixed,'status',dict(st))
print('by grade',dict(collections.Counter(e['g'] for e in M.values())))
with open(S+'/catalogue.tsv','w') as f:
    f.write('id\tgrade\ttopic\tnum_title\tkind\tccss\tstatus\tdoes\tnotes\n')
    for e in M.values():
        t=re.sub(r'^.*? Math - ','',e.get('title','')); t=re.sub(r' - (Worksheets?|Answer Key)\.pdf$','',t)
        f.write('\t'.join(str(x).replace('\t',' ').replace('\n',' ') for x in [e['id'],e['g'],e.get('topic',''),t,e.get('kind',''),','.join(e.get('ccss') or []),e.get('text_ok'),e.get('does',''),(e.get('notes') or '')[:300]])+'\n')
