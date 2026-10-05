import itertools,math,json
from plan import *
from mapcheck import coverage, GOAL
CUT=32
# domain order as approved (5 Oct 2026 brief); lesson moves must not reshuffle it
FIXED_ORDER={"K":["CC","OA","NBT","MD","G"],"G1":["NBT","OA","G","MD"],"G2":["NBT","OA","MD","G"],
 "G3":["OA","NF","NBT","MD","G"],"G4":["OA","NBT","NF","G","MD"],"G5":["NBT","OA","NF","MD","G"]}
def schedule_map(g,steps,order):
    seq=[];post=[]
    for d in order:
        run=[s for s in steps if s['dom']==d]
        if not run: continue
        if d=="EXT": post+=[dict(s,slot='step',post_map=True) for s in run]; continue
        core=[s for s in run if not s['kind'].startswith('year-ahead')]
        ahead=[s for s in run if s['kind'].startswith('year-ahead')]
        seq+=[dict(s,slot='step') for s in core]
        seq.append(dict(slot='exam',dom=d,lesson=f"DOMAIN EXAM · {DOMNAME[d]}",codes=[],power=[],kind='',note=[],unit='',step='',build=False))
        post=[dict(s,slot='step',post_map=True) for s in ahead]+post if False else post+[dict(s,slot='step',post_map=True) for s in ahead]
    # post-MAP block: year-ahead steps grouped by domain order, then Grade 6-only extension
    post.sort(key=lambda s:(1 if s['dom']=="EXT" else 0, order.index(s['dom'])))
    seq+= [dict(slot='map',dom='MAP',lesson="MAP GROWTH WINDOW (spring) · all grade-level domains taught and examined · ENRICHMENT LESSONS FOLLOW",codes=[],power=[],kind='',note=[],unit='',step='',build=False)]+post
    return assign_weeks(seq)
def best_map(g,steps):
    present=[d for d in CCSS_DOMAINS[g] if any(s['dom']==d for s in steps)]
    med={d:sorted(s['wrm_idx'] for s in steps if s['dom']==d)[len([1 for s in steps if s['dom']==d])//2] for d in present}
    E=[(a,b) for a,b in edges(g) if a in present and b in present]
    best=None
    perms=[tuple(d for d in FIXED_ORDER[g] if d in present)] if g in FIXED_ORDER else itertools.permutations(present)
    for perm in perms:
        pos={d:i for i,d in enumerate(perm)}
        if any(pos[a]>pos[b] for a,b in E): continue
        order=list(perm)+(["EXT"] if any(s['dom']=="EXT" for s in steps) else [])
        seq=schedule_map(g,steps,order); b=balance(g,seq)
        cov=coverage(g,[(s['codes'],s['week']) for s in seq if s['slot']=='step'])
        short=sum(v[1]-v[0] for v in cov.values())
        lastexam=max(s['week'] for s in seq if s['slot']=='exam')
        disp=sum(1 for i in range(len(perm)) for j in range(i+1,len(perm)) if med[perm[i]]>med[perm[j]])
        score=(short, max(0,lastexam-CUT), abs(b['exam'][0]-b['exam'][1]), abs(b['taught'][0]-b['taught'][1]), disp)
        if best is None or score<best[0]: best=(score,order,seq,b,cov,lastexam)
    return best
if __name__=="__main__":
    for g in GR:
        steps=classify(g)
        score,order,seq,b,cov,le=best_map(g,steps)
        mapw=[s['week'] for s in seq if s['slot']=='map'][0]
        print(f"{GRADE_LABEL[g]:<27} {' → '.join(order):<34} exams S1/S2 {b['exam']} | last exam W{le} | MAP marker W{mapw} | cov {cov} | score {score}")
