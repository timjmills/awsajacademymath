# usage: check_match.py <stage: out|verified> <chunk...>   -> prints problems; exit 1 if any
import json,sys,os,re,collections
def nn(t): return re.sub(r'\W+',' ',(t or '').lower()).strip()
S=os.path.dirname(os.path.abspath(__file__)); stage=sys.argv[1]; chunks=sys.argv[2:]
C=json.load(open(S+'/stage2/catalogue.json'))
ORD={'PK':-1,'K':0,'G1':1,'G2':2,'G3':3,'G4':4,'G5':5,'G6':6}
bad=0
for c in chunks:
    L=json.load(open(f'{S}/match/lessons_{c}.json'))
    want={}
    for u in L:
        for s in u['steps']:
            k=(u['grade'],nn(u['unit']),s['step'],nn(s['title']))
            if k in want: print(c,'INPUT DUPLICATE KEY',k)
            want[k]=(u,s)
    p=f'{S}/match/{stage}_{c}.jsonl'
    if not os.path.exists(p): print(c,'MISSING FILE'); bad+=1; continue
    got=collections.Counter(); probs=[]
    for l in open(p):
        if not l.strip(): continue
        try: r=json.loads(l)
        except Exception: probs.append('bad json line'); continue
        k=(r.get('grade'),nn(r.get('unit')),r.get('step'),nn(r.get('title'))); got[k]+=1
        if k not in want: probs.append(f'unknown lesson {k}'); continue
        g=ORD[k[0]]; seen=set(); k=(k[0],k[1][:25],k[2])
        for kind in ('core','prereq'):
            for w in r.get(kind,[]):
                e=C.get(w.get('id'))
                if not e: probs.append(f'{k} {kind}: id not in catalogue {w.get("id")}'); continue
                if e.get('text_ok') in (False,'False'): probs.append(f'{k} {kind}: UNVERIFIED sheet {e["title"][:50]}')
                if w['id'] in seen: probs.append(f'{k}: {e["title"][:50]} listed twice')
                seen.add(w['id'])
                if not w.get('why'): probs.append(f'{k} {kind}: missing reason')
                sg=ORD.get(e['g'],9)
                if kind=='core' and abs(sg-g)>2: probs.append(f'{k} core: grade {e["g"]} sheet far from lesson grade {k[0]}: {e["title"][:50]}')
                if kind=='prereq' and sg>g: probs.append(f'{k} prereq: sheet grade {e["g"]} is above lesson grade: {e["title"][:50]}')
                if re.search(r'word search|crossword|coloring|colouring|holiday',(e.get('kind','')+' '+e.get('topic','')+' '+e.get('title','')),re.I) and e.get('kind') in ('activity/colouring','puzzle/game'):
                    probs.append(f'{k} {kind}: non-practice sheet {e["title"][:50]}')
        if stage=='verified':
            for w in r.get('core',[])+r.get('prereq',[]):
                if not w.get('opened',True): probs.append(f'{k}: kept without opening')
    miss=[k for k in want if k not in got]; dup=[k for k,v in got.items() if v>1]
    if miss: probs.append(f'{len(miss)} lessons missing e.g. {miss[:3]}')
    if dup: probs.append(f'{len(dup)} lessons duplicated e.g. {dup[:3]}')
    print(f'chunk {c}: {len(got)}/{len(want)} lessons, {len(probs)} problems')
    for x in probs[:12]: print('   ',x)
    bad+=len(probs)
sys.exit(1 if bad else 0)
