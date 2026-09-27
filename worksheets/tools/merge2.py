# Stage-2 merge: pairing fixes (stage2/master_fixed.json) + rechecks + added -> stage2/catalogue.json
import json,glob,os,re,collections
S=os.path.dirname(os.path.abspath(__file__))
M=json.load(open(S+'/stage2/master_fixed.json'))
for l in open(S+'/stage2/added.jsonl'):
    e=json.loads(l); e['g']='G1'; M[e['id']]=e
KEEP=('answer_key_id','folder_id','id','title','g')
stats=collections.Counter()
for p in sorted(glob.glob(S+'/recheck/fixed_*.jsonl')):
    for l in open(p):
        if not l.strip(): continue
        r=json.loads(l); base=M.get(r['id'])
        if not base: stats['unknown id']+=1; continue
        ok=str(r.get('text_ok')).lower() in ('visual','text','true','answer key')
        weak=re.search(r'metadata|structural|unconfirm|could not|garbl.*(both|also)|inferred',(r.get('notes') or ''),re.I)
        if ok and not (weak and str(r.get('text_ok')).lower()!='visual'):
            for k,v in r.items():
                if k not in KEEP and k!='recheck_reason': base[k]=v
            base['text_ok']='text' if str(r.get('text_ok')).lower()=='true' else r.get('text_ok')
            stats['applied '+str(r.get('recheck','?'))]+=1
        else:
            base['text_ok']=False
            base['notes']=(base.get('notes') or '')+' [Stage 2: still unverified — '+(r.get('notes') or '')[:200]+']'
            stats['still unverified']+=1
for e in M.values():
    if e.get('g')=='G8': e['g']='G3'
    if str(e.get('text_ok')).lower()=='true': e['text_ok']='text'
    if e.get('text_ok') in (None,'false'): e['text_ok']=False
json.dump(M,open(S+'/stage2/catalogue.json','w'))
print(dict(stats)); print(len(M),collections.Counter(str(e.get('text_ok')) for e in M.values()))
