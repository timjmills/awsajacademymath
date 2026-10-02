import json,re,collections
cat=json.load(open('stage2/catalogue.json'))
def nn(t): return re.sub(r'\W+',' ',(t or '').lower()).strip()
slots=[]
for c in range(47):
    for u in json.load(open(f'match/lessons_{c}.json')):
        for s in u['steps']: slots.append((c,u['grade'],u['unitNum'],u['unit'],s['step'],s['title']))
out=[];seen=set();stats=collections.Counter();issues=[]
for c in range(47):
    for l in open(f'match/final_{c}.jsonl'):
        r=json.loads(l)
        k=(r['grade'],nn(r['unit']),r['step'],nn(r['title']))
        if k in seen: issues.append(('dup lesson',k))
        seen.add(k)
        ids=set(); core=[]
        for p in r['core']:
            if p['id'] in ids: stats['dedup']+=1; continue
            if p['id'] not in cat: issues.append(('bad id',p['id'])); continue
            ids.add(p['id']); core.append(p)
        pre=[]
        for p in r['prereq']:
            if p['id'] in ids: stats['prereq_also_core']+=1; continue
            if p['id'] not in cat: issues.append(('bad id',p['id'])); continue
            ids.add(p['id']); pre.append(p)
        r['core']=core;r['prereq']=pre;r['chunk']=c
        stats['core']+=len(core);stats['prereq']+=len(pre)
        stats['core_opened']+=sum(1 for p in core if p.get('opened'))
        stats['zero_core']+= (not core)
        out.append(r)
print('slots',len(slots),'lessons',len(out),'unique',len(seen));print(dict(stats));print(issues[:10],len(issues))
json.dump(out,open('stage3_final.json','w'),ensure_ascii=False)
allk={(g,nn(un),st,nn(t)) for _,g,_,un,st,t in slots}
print('missing',len(allk-seen),'extra',len(seen-allk))
