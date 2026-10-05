import itertools,csv,math
from core import *

# Hard prerequisite edges (A before B). Geometry is unconstrained.
def edges(g):
    # (A,B) = A must come before B. Reasons in EDGE_WHY. Geometry is unconstrained.
    E={"K":[("CC","OA"),("CC","NBT"),("CC","MD")],
       "G1":[("NBT","OA"),("NBT","MD"),("OA","MD")],
       "G2":[("NBT","OA"),("NBT","MD"),("OA","MD")],
       "G3":[("OA","NF"),("OA","MD"),("NBT","MD")],
       "G4":[("OA","NBT"),("NBT","NF"),("OA","NF"),("NBT","MD"),("OA","MD"),("NF","MD")],
       "G5":[("NBT","NF"),("OA","NF"),("NBT","MD"),("OA","MD"),("NF","MD")]}
    return E[g]
EDGE_WHY={
 ("CC","OA"):"adding and subtracting needs counting and cardinality",
 ("CC","NBT"):"teen numbers need counting to 20",
 ("CC","MD"):"comparing and sorting needs counting",
 ("NBT","OA"):"make-ten and bridging strategies need place value",
 ("NBT","MD"):"measuring and data need numbers to 100/1,000",
 ("OA","MD"):"measurement word problems and data questions need the operations",
 ("NBT","NF"):"decimals need place value",
 ("OA","NF"):"fractions need multiplication and division facts",
 ("NF","MD"):"conversions, line plots and measures use fractions and decimals",
 ("OA","NBT"):"multi-digit multiplication and division need facts, factors and multiples",
}

def assign_domain(g,st,prev_dom):
    n=GNUM[g]; codes=st['codes']; valid=CCSS_DOMAINS[g]
    on=[c for c in codes if gnum(c)==n]
    note=[]
    if on:
        ds=[]
        for c in on:
            if dom(c) not in ds: ds.append(dom(c))
        pw=[dom(c) for c in on if c in POWERSET[g] or POWER_ALIAS.get(c) in POWERSET[g]]
        d=pw[0] if pw else ds[0]
        if len(ds)>1: note.append("also "+"/".join(x for x in ds if x!=d))
        return d,"on-grade",note
    if not codes:
        return (prev_dom or valid[0]),"no CCSS code (kept with neighbour)",note
    below=[c for c in codes if gnum(c)<n]; above=[c for c in codes if gnum(c)>n]
    if below:
        d=dom(below[0]);
        if d in valid: return d,"review of earlier grade",note
        return (prev_dom or valid[0]),"review of earlier grade",note
    d=dom(above[0])
    if d in valid: return d,"year-ahead (WRM teaches ahead)",note
    return "EXT","beyond grade-level CCSS",note

def classify(g):
    steps,_=wrm_sequence(g)
    prev=None
    for st in steps:
        d,kind,note=assign_domain(g,st,prev)
        if g=="G3" and st['unit'] in ("Decimals A","Decimals B") and kind=="on-grade":
            kind="year-ahead (decimals are CCSS Grade 4, 4.NF.C)"
        st['dom']=d; st['kind']=kind; st['note']=note
        if d!="EXT": prev=d
        st['power']=sorted({(POWER_ALIAS.get(c,c)) for c in st['codes'] if c in POWERSET[g] or POWER_ALIAS.get(c) in POWERSET[g]})
        st['build']=st.get('is_build',False)
    return steps

WEEKS=39; S1_LAST=14   # site calendar: W14 = 13-17 Dec, W15 = 3 Jan
EXAM_EARLY=True
# a domain's year-ahead tail that needs a domain taught later is held until that domain is done
TAIL_AFTER={"G3":{"NF":"NBT"}}
def schedule(g,steps,order):
    seq=[]; held={}
    ta=TAIL_AFTER.get(g,{})
    for d in order:
        run=[s for s in steps if s['dom']==d]
        if not run: continue
        exam=dict(slot='exam',dom=d,lesson=f"DOMAIN EXAM · {DOMNAME[d]}",codes=[],power=[],kind='',note=[],unit='',step='',build=False)
        if d=="EXT":
            seq+=[dict(s,slot='step') for s in run]; continue
        if EXAM_EARLY:
            core=[s for s in run if not s['kind'].startswith('year-ahead')]
            ahead=[s for s in run if s['kind'].startswith('year-ahead')]
            tail=[dict(s,slot='step',after_exam=True) for s in ahead]
            tgt=ta.get(d)
            if tgt and tgt in order and order.index(tgt)>order.index(d):
                held[tgt]=held.get(tgt,[])+[dict(t,held_from=d) for t in tail]; tail=[]
            seq+=[dict(s,slot='step') for s in core]+[exam]+tail+held.pop(d,[])
        else:
            seq+=[dict(s,slot='step') for s in run]+[exam]
    return assign_weeks(seq)

def balance(g,seq):
    exam_week={s['dom']:s['week'] for s in seq if s['slot']=='exam'}
    first={}
    for s in seq:
        if s['slot']!='step': continue
        for p in s['power']: first.setdefault(p,s['week'])
    s1e=s2e=0; s1t=s2t=0; miss=[]
    for c in POWERSET[g]:
        d=dom(c)
        ew=exam_week.get(d)
        if ew is None: miss.append(c); continue
        if ew<=S1_LAST: s1e+=1
        else: s2e+=1
        fw=first.get(c)
        if fw is None: miss.append(c)
        elif fw<=S1_LAST: s1t+=1
        else: s2t+=1
    return dict(exam=(s1e,s2e),taught=(s1t,s2t),missing=sorted(set(miss)),exam_week=exam_week)

def best_order(g,steps):
    present=[d for d in CCSS_DOMAINS[g] if any(s['dom']==d for s in steps)]
    # WRM centre of mass for tie-breaking
    med={d:sorted(s['wrm_idx'] for s in steps if s['dom']==d)[len([1 for s in steps if s['dom']==d])//2] for d in present}
    base=sorted(present,key=lambda d:med[d])
    E=[(a,b) for a,b in edges(g) if a in present and b in present]
    best=None
    for perm in itertools.permutations(present):
        pos={d:i for i,d in enumerate(perm)}
        if any(pos[a]>pos[b] for a,b in E): continue
        # number domains keep WRM order among themselves (NBT/OA judgement left to WRM)
        order=list(perm)+(["EXT"] if any(s['dom']=="EXT" for s in steps) else [])
        seq=schedule(g,steps,order); b=balance(g,seq)
        disp=sum(1 for i in range(len(perm)) for j in range(i+1,len(perm)) if med[perm[i]]>med[perm[j]])
        score=(abs(b['exam'][0]-b['exam'][1]), abs(b['taught'][0]-b['taught'][1]), disp)
        if best is None or score<best[0]: best=(score,order,seq,b)
    return best,base

if __name__=="__main__":
    import sys
    for g in (sys.argv[1:] or GR):
        steps=classify(g)
        (score,order,seq,b),base=best_order(g,steps)
        from collections import Counter
        cnt=Counter(s['dom'] for s in steps)
        print("="*70); print(GRADE_LABEL[g], dict(cnt))
        print(" WRM centre-of-mass order:",base)
        print(" CHOSEN order:",order," score",score)
        print(" exam weeks:",b['exam_week'])
        print(" power stds by EXAM semester S1/S2:",b['exam']," by FIRST TAUGHT:",b['taught']," missing:",b['missing'])
