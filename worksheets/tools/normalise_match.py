# usage: normalise_match.py <out|verified> <chunk...>
# Re-keys each output line to the true (grade, unitNum, step) by matching grade+unit name+step+title; rewrites file in place.
import json,sys,os,re
S=os.path.dirname(os.path.abspath(__file__)); stage=sys.argv[1]
def n(t): return re.sub(r'\W+',' ',(t or '').lower()).strip()
for c in sys.argv[2:]:
    p=f'{S}/match/{stage}_{c}.jsonl'
    if not os.path.exists(p): print(c,'missing'); continue
    L=json.load(open(f'{S}/match/lessons_{c}.json'))
    slots=[(u['grade'],u['unitNum'],u['unit'],s['step'],s['title'],u.get('domain')) for u in L for s in u['steps']]
    used=set(); out=[]; unmatched=[]; fixed=0
    rows=[json.loads(l) for l in open(p) if l.strip()]
    for r in rows:
        cand=[i for i,s in enumerate(slots) if i not in used and s[0]==r.get('grade') and s[3]==r.get('step') and n(s[4])==n(r.get('title'))]
        if len(cand)>1:
            c2=[i for i in cand if n(slots[i][2])==n(r.get('unit'))]
            cand=c2 or cand
        if len(cand)>1:
            c3=[i for i in cand if slots[i][1]==r.get('unitNum')]; cand=c3 or cand
        if not cand: unmatched.append((r.get('grade'),r.get('unit'),r.get('step'),r.get('title'))); continue
        i=cand[0]; used.add(i)
        if r.get('unitNum')!=slots[i][1]: fixed+=1
        r['unitNum']=slots[i][1]; r['unit']=slots[i][2]; out.append(r)
    if rows and not out:
        print(c,'ABORT: nothing matched, file left untouched'); open(f'{S}/match/{stage}_{c}.unmatched.json','w').write(json.dumps(unmatched)); continue
    with open(p,'w') as f:
        for r in out: f.write(json.dumps(r,ensure_ascii=False)+'\n')
    if unmatched: open(f'{S}/match/{stage}_{c}.unmatched.json','w').write(json.dumps(unmatched))
    print(f'chunk {c}: kept {len(out)}/{len(slots)}, renumbered {fixed}, unmatched {len(unmatched)}, lessons without output {len(slots)-len(used)}')
