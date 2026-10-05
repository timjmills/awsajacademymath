import csv,json,re
from plan import *
from mapplan import best_map, schedule_map
from mapcheck import coverage

# CCSS standards missing from their own grade's guide, closed with real WRM steps copied from the nearest guide
COPY_AT_START={"G3"}   # foundational: open the domain run
COPIES={ "G1":[("K","Measure length using objects")],   # Measurement test asks for non-standard units
         "G2":[("G3","Count squares")],
         "G3":[("G2","Multiplication - equal groups"),("G2","Sharing and grouping")],
         "G4":[("G3","Understand angles as turns"),("G3","Identify angles")],
         "G5":[("G4","Cubic centimetres")] }   # "What is volume?" is not in the current WRM Year 5 scheme
MANUAL={ # known cross-domain dependencies that the code tags don't reveal: (grade, lesson-substring) -> note
 ("K","half past"):"Uses 'half', which now comes later; introduce half informally on a clock face.",
 ("G1","half past"):"Uses 'half', which is now taught later in the Geometry run; introduce half informally on a clock face.",
 ("G5","four quadrants"):"Needs negative numbers, now in the end-of-year extension block. Teach the first quadrant only here (that is all 5.G.A.1 asks).",
 ("G5","form ordered pairs"):"Graphing the pairs needs the coordinate plane (Geometry run). Generate the patterns here; graph them in the Geometry run.",
 ("G5","line graphs"):"Plotting points uses the coordinate plane; fine if taught as reading graphs, revisit after Geometry.",
}
# Lesson moves so every type of problem on the Awsaj domain tests is taught before that test
# (grade, lesson) -> (domain, "before"/"after", anchor lesson)
MOVES={("G1","Measure length using objects"):("MD","before","Measure in centimetres"),
 ("G3","Partition shapes into equal areas"):("NF","before","Understand the whole"),
 ("G3","Measure to the half and quarter inch"):("MD","before","Build a line plot from inch measurements"),
 ("G4","Understand and use degrees"):("G","before","Draw lines and angles accurately"),
 ("G4","Measure angles up to 180°"):("G","before","Draw lines and angles accurately"),
 ("G5","The first quadrant"):("OA","before","Form ordered pairs from corresponding terms"),
 ("G5","Form expressions"):("OA","after","Order of operations"),
 ("G5","Multi-step problems"):("NF","after","Subtract mixed numbers")}
def apply_moves(g,steps):
    k=0
    for st in steps:   # White Rose end-of-year projects stay at the end of the year
        if 'Projects' in st.get('unit',''): st['dom']='EXT'; st['kind']='end-of-year projects'
    for (gg,name),(d,where,anchor) in MOVES.items():
        if gg!=g: continue
        st=[s for s in steps if s['lesson']==name]; an=[s for s in steps if s['lesson']==anchor]
        assert st and an,(g,name,anchor)
        st=st[0]; k+=1
        st['dom']=d
        if not st['kind'].startswith('on-grade') and not st.get('is_copy'): st['kind']='on-grade (moved for the domain test)'
        st['wrm_idx']=an[0]['wrm_idx']+(-0.05 if where=="before" else 0.05)+k*0.001
def pacing_dates(g):
    # the live site's calendar (W01 = 6 Sep 2026), not the 22 Aug print
    return {int(w[1:]):(v['q'],v['start']) for w,v in SITEWEEKS.items()}
def fmt_date(iso,q):
    import datetime; return datetime.date.fromisoformat(iso).strftime("%d %b %Y")

ALL={}
for g in GR:
    steps=classify(g)
    orig=list(steps)
    for k,(src,name) in enumerate(COPIES.get(g,[])):
        s0=[s for s in classify(src) if s['lesson']==name][0]
        n=GNUM[g]; mine=[c for c in s0['codes'] if gnum(c)==n]
        cl=".".join(mine[0].split(".")[:3])
        d=dom(mine[0])
        anchor=[] if g in COPY_AT_START else [s['wrm_idx'] for s in orig if s['dom']==d and any(c.startswith(cl+".") and gnum(c)==n for c in s['codes'])]
        if not anchor: anchor=[s['wrm_idx'] for s in orig if s['dom']==d]
        steps.append(dict(unit=s0['unit'],step=s0['step'],src_wrm_week=s0['wrm_week'],lesson=s0['lesson'],codes=s0['codes'],flag="COPY",
            dom=d,kind=f"copied from {src} guide",note=[],build=False,wrm_week=None,wrm_q=None,is_copy=True,copy_src=src,
            wrm_idx=min(anchor)-0.9+k*0.1,
            power=sorted({c for c in s0['codes'] if c in POWERSET[g]})))
    apply_moves(g,steps)
    steps.sort(key=lambda s:s['wrm_idx'])
    score,order,seq,b,cov,le=best_map(g,steps)
    assign_weeks(seq)
    b=balance(g,seq)
    dates=pacing_dates(g)
    first_core={}
    for i,s in enumerate(seq):
        if s['slot']=='step' and not s.get('after_exam') and s['dom'] not in first_core: first_core[s['dom']]=i
    rows=[]; keys=[]
    pblock={int(r['week'][1:]):r['block'] for r in csv.DictReader(open(SP+f'pacing_{g}.tsv'),delimiter='\t')}
    for i,s in enumerate(seq):
        q,dt=dates[s['week']]
        flags=[]
        if s['slot']=='step':
            for n in s.get('note',[]):
                for od in n.replace('also ','').split('/'):
                    if od in first_core and first_core[od]>i:
                        flags.append(f"Also uses {od}, which is now taught later (from W{seq[first_core[od]]['week']:02d}).")
            for (gg,sub),txt in MANUAL.items():
                if gg==g and sub in s['lesson'].lower(): flags.append(txt)
            if s.get('held_from'): flags.append(f"Year-ahead {s['held_from']} step held until place value is done.")
            if s['build']: flags.append("CCSS BUILD lesson: still to be written.")
            if s.get('is_copy'): flags.append(f"Copied from the {GRADE_LABEL[s['copy_src']]} guide so this standard is taught in its own grade. Slides and worksheet live in that grade's lesson folder.")
        typ = "MAP" if s['slot']=='map' else "EXAM" if s['slot']=='exam' else ("BUILD" if s['build'] else ("COPIED IN" if s.get('is_copy') else s['kind']))
        if s.get('post_map') and s['slot']=='step' and s['kind']=='end-of-year projects': typ="ENRICHMENT · end-of-year projects"
        elif s.get('post_map') and s['slot']=='step': ups=sorted({gnum(c) for c in s['codes'] if gnum(c)>GNUM[g]}) or ([4] if 'decimals' in s['kind'] else []); typ="ENRICHMENT · above grade level ("+("Grade "+str(ups[0]) if ups else "no CCSS code")+" standard)"
        moved = "" if s['slot'] in('exam','map') or s.get('wrm_week') is None else s['week']-s['wrm_week']
        rows.append([i+1 if s['slot']=='step' else "", s['week'], q, fmt_date(dt,q), "S1" if q in("Q1","Q2") else "S2",
            s['dom'], DOMNAME.get(s['dom'],"MAP Growth"), s['lesson'], ", ".join(s['codes']), ", ".join(s['power']), typ,
            (f"W{s['wrm_week']:02d}" if s.get('wrm_week') else ""), moved, " ".join(flags)])
        keys.append(dict(slot=s['slot'],site_unit=s.get('unit',''),site_step=s.get('step',''),
            orig_week=s.get('wrm_week') or s.get('src_wrm_week'),orig_block=(pblock.get(s['wrm_week'],'') if s.get('wrm_week') else ''),
            copied_from=s.get('copy_src'),is_build=bool(s.get('build')),kind=s.get('kind',''),
            post_map=bool(s.get('post_map')),codes=s.get('codes',[]),power=s.get('power',[])))
    # renumber steps
    k=0
    for r in rows:
        if r[0]!="": k+=1; r[0]=k
    # baseline: power standards by first-taught semester in the CURRENT WRM sequence
    fst={}
    for s in sorted(steps,key=lambda x:x['wrm_idx']):
        if s.get('is_copy'): continue
        for p in s['power']: fst.setdefault(p,s['wrm_week'])
    base_s1=sum(1 for c in POWERSET[g] if fst.get(c) and fst[c]<=S1_LAST); base_s2=sum(1 for c in POWERSET[g] if fst.get(c) and fst[c]>S1_LAST)
    cal=[]
    for d in order:
        run=[r for r in rows if r[5]==d and not str(r[10]).startswith("ENRICHMENT")] or [r for r in rows if r[5]==d]
        ex=[r for r in run if r[10]=="EXAM"]
        cal.append(dict(dom=d,name=DOMNAME[d],steps=sum(1 for r in run if r[0]!=""),
            start=run[0][1],end=run[-1][1],exam=(ex[0][1] if ex else None),exam_date=(ex[0][3] if ex else ""),
            sem=(ex[0][4] if ex else ""),power=sorted(c for c in POWERSET[g] if dom(c)==d)))
    cov=coverage(g,[([c.strip() for c in r[8].split(',') if c.strip()],r[1]) for r in rows if r[0]!=""])
    mapw=[r[1] for r in rows if r[10]=="MAP"][0]
    ALL[g]=dict(keys=keys,rows=rows,order=order,balance=b,base=(base_s1,base_s2),cal=cal,cov=cov,mapweek=mapw,
        lastexam=max(r[1] for r in rows if r[10]=="EXAM"),post=sum(1 for r in rows if str(r[10]).startswith("ENRICHMENT")),
        n_build=sum(1 for r in rows if r[10].startswith("BUILD")),
        n_flags=sum(1 for r in rows if r[13]),
        moved_mean=round(sum(abs(r[12]) for r in rows if isinstance(r[12],int))/max(1,sum(1 for r in rows if isinstance(r[12],int))),1))
    print(GRADE_LABEL[g],"| cov",cov,"| MAP W",mapw,"| order",order,"| exam S1/S2",b['exam'],"| was",(base_s1,base_s2),
          "| steps",sum(1 for r in rows if r[0]!=""),"| flags",ALL[g]['n_flags'],"| mean move",ALL[g]['moved_mean'],"wks")
json.dump(ALL,open("final_map.json","w"),default=str)
