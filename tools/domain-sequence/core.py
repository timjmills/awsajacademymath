import json,re,csv,sys,bisect,os
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE)
from powerstd import POWER,GRADE_LABEL
MAP=os.path.join(HERE,'inputs','WRM_to_CCSS_Mapping_v3.json')
SP=os.path.join(HERE,'inputs')+os.sep
GR=["K","G1","G2","G3","G4","G5"]
GNUM={"K":0,"G1":1,"G2":2,"G3":3,"G4":4,"G5":5}
TBL={"K":(167,324),"G1":(324,491),"G2":(491,673),"G3":(673,863),"G4":(863,1053),"G5":(1053,None)}
CCSS_DOMAINS={"K":["CC","OA","NBT","MD","G"],"G1":["OA","NBT","MD","G"],"G2":["OA","NBT","MD","G"],
 "G3":["OA","NBT","NF","MD","G"],"G4":["OA","NBT","NF","MD","G"],"G5":["OA","NBT","NF","MD","G"]}
DOMNAME={"CC":"Counting & Cardinality","OA":"Operations & Algebraic Thinking","NBT":"Number & Operations in Base Ten",
 "NF":"Number & Operations: Fractions","MD":"Measurement & Data","G":"Geometry","EXT":"Enrichment (Grade 6 content)"}
POWERSET={g:{c for c,_,_ in POWER[g]} for g in GR}
# sheet miscode: M.K.CC.B.6 printed text = K.CC.B.5
POWER_ALIAS={"K.CC.B.5":"K.CC.B.6"}

def gnum(code):
    h=code.split('.')[0]; return 0 if h=="K" else int(h)
def dom(code): return code.split('.')[1]
def norm(s):
    s=s.lower().replace('–','-').replace('—','-').replace('’',"'").replace('‘',"'")
    s=re.sub(r'\\','',s); s=re.sub(r'\s+',' ',s); return s.strip()

RENAMES=json.load(open(SP+'renames.json'))
DRIVE=json.load(open(SP+'drive_keys.json')); LIVE=json.load(open(SP+'live_titles.json'))
def dkey(t): return re.sub(r'[^a-z0-9]','',re.sub(r'\(US:[^)]*\)','',t).lower())
def current(g,title):
    # a step of the current WRM scheme: on the grade's Drive, or already on the live site for this grade
    return dkey(title) in set(DRIVE[g]) or dkey(title) in {dkey(t) for t in LIVE[g]}
DROPPED={}
def load_steps(g):
    c=json.load(open(MAP))['fileContent'].split('\n')
    s,e=TBL[g]; out=[]
    for l in c[s+1:e]:
        p=[x.strip() for x in l.split('|')]
        if len(p)<7 or not re.match(r'^\d+$',p[2] or ''): continue
        codes=[x.strip() for x in p[4].split(',') if x.strip()]
        name=p[3].replace('\\','')
        name=RENAMES.get(g,{}).get(name,name)
        out.append(dict(unit=p[1],step=int(p[2]),lesson=name,codes=codes,flag=p[6]))
    return out

def load_pacing(g):
    raw=open(SP+f"pacing_{g}_raw.txt").read()
    t=raw
    t=re.sub(r'SUPPORT BLOCK · PICK ONE','\n',t)
    t=re.sub(r'SUPPORT ·','\n',t)
    # drop support items: marker + name up to next marker / newline / End of
    t=re.sub(r'(?:Rec/PK4|Y\d/(?:KG|Gr\.\d)) · .*?(?=(?:Rec/PK4|Y\d/(?:KG|Gr\.\d)) · |\n|End of|$)','',t)
    tn=norm(t)
    weeks=[(m.start(),m.group(1),m.group(2),m.group(3)) for m in re.finditer(r'\bw(\d\d) (q\d) · (\d\d-\d\d)',tn)]
    return tn,weeks

def week_at(weeks,pos):
    i=bisect.bisect_right([w[0] for w in weeks],pos)-1
    i=max(i,0); w=weeks[i]; return int(w[1]),w[2].upper(),w[3]

def load_builds(g):
    raw=open(SP+f"pacing_{g}_raw.txt").read()
    out=[];seen=set()
    for name,codes in re.findall(r"BUILD ([^\n]{3,90}?)((?:\s+(?:K|\d)\.[A-Z]{1,3}\.[A-Z]\.[0-9][A-Z.]*)+)",raw):
        n=norm(name)
        if n in seen: continue
        seen.add(n); out.append((name.strip(),codes.split()))
    return out

def wrm_sequence(g):
    steps=load_steps(g); tn,weeks=load_pacing(g)
    builds=load_builds(g); have={norm(s['lesson']) for s in steps}
    bnames={norm(n) for n,_ in builds}
    for i,(n,codes) in enumerate(builds):
        if norm(n) not in have:
            steps.append(dict(unit="CCSS BUILD (from pacing guide)",step=i+1,lesson=n,codes=[c for c in codes if not re.search(r'\.[A-D]$',c) or True],flag='BUILD'))
    for s in steps: s['is_build']= norm(s['lesson']) in bnames
    keep=[s for s in steps if s['is_build'] or current(g,s['lesson'])]
    DROPPED[g]=[s for s in steps if s not in keep]; steps=keep
    used={}
    found=0
    for st in steps:
        name=norm(st['lesson'])
        base=re.sub(r'\s*\(\d+\)$','',name)
        pos=-1
        for cand in ([name] if name==base else [name,base]):
            start=used.get(cand,0)
            # anchor: a lesson name in the guide is followed by its CCSS code
            m=re.compile(re.escape(cand)+r' (?:k|\d)\.[a-z]{1,3}\.[a-z]\.').search(tn,start)
            pos=m.start() if m else -1
            if pos<0:
                m=re.compile(re.escape(cand)+r'(?![\w,])').search(tn,start)
                pos=m.start() if m else -1
            if pos>=0:
                used[cand]=pos+1; break
        st['pos']=pos
        if pos>=0: found+=1
    # fallback: unmatched -> just after previous step of same unit (by step no.)
    byunit={}
    for st in steps: byunit.setdefault(st['unit'],[]).append(st)
    for u,lst in byunit.items():
        lst.sort(key=lambda x:x['step'])
        for i,st in enumerate(lst):
            if st['pos']<0:
                prev=[x['pos'] for x in lst[:i] if x['pos']>=0]
                nxt=[x['pos'] for x in lst[i+1:] if x['pos']>=0]
                st['pos']=(prev[-1]+0.5) if prev else ((nxt[0]-0.5) if nxt else 10**9)
                st['unmatched']=True
    steps.sort(key=lambda x:(x['pos'],x['unit'],x['step']))
    for i,st in enumerate(steps):
        st['wrm_idx']=i
        p=st['pos'] if st['pos']<10**9 else len(tn)-1
        wk,q,dt=week_at(weeks,int(p)); st['wrm_week']=wk; st['wrm_q']=q
    return steps,found

if __name__=="__main__":
    for g in GR:
        s,f=wrm_sequence(g)
        print(g,len(s),"matched",f, "unmatched:",[x['lesson'] for x in s if x.get('unmatched')][:8])

SITEWEEKS=json.load(open(SP+'site_weeks.json'))
def assign_weeks(seq):
    """Spread items over the site's 39 weeks in proportion to teaching days (W01 = 6 Sep)."""
    days=[(int(w[1:]),v['days']) for w,v in SITEWEEKS.items()]
    tot=sum(d for _,d in days); N=len(seq); cum=0; edges=[]
    for w,d in days: cum+=d; edges.append((cum/tot,w))
    for i,s in enumerate(seq):
        f=(i+0.5)/N
        s['week']=next(w for e,w in edges if f<=e)
    return seq
