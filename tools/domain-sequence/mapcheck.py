import json,re
from core import *
from plan import classify
GOAL={"CC":"N&O","NBT":"N&O","NF":"N&O","OA":"OA","MD":"MD","G":"G"}
CUT=32  # taught by end of W32; spring MAP window assumed to open W33 (2 May 2027)
def coverage(g,seq_weeks):
    # seq_weeks: list of (codes, week). Coverage = share of the grade's on-grade standards (cluster-level code) first taught by CUT
    n=GNUM[g]; allstd={}
    for codes,w in seq_weeks:
        for c in codes:
            if gnum(c)!=n: continue
            base=".".join(c.split(".")[:4])  # collapse sub-letters
            allstd[base]=min(allstd.get(base,99),w if w else 99)
    out={}
    for goal in ["OA","N&O","MD","G"]:
        stds=[s for s in allstd if GOAL.get(dom(s))==goal]
        if not stds: continue
        done=sum(1 for s in stds if allstd[s]<=CUT)
        out[goal]=(done,len(stds))
    return out
if __name__=="__main__":
  A=json.load(open("final.json"))
  res={}
  for g in GR:
      steps=classify(g)
      wrm=[(s['codes'],s['wrm_week']) for s in steps]
      new=[([c.strip() for c in r[8].split(',') if c.strip()],r[1]) for r in A[g]['rows'] if r[0]!=""]
      cw=coverage(g,wrm); cn=coverage(g,new); res[g]=(cw,cn)
      def f(d): return "  ".join(f"{k} {v[0]}/{v[1]}" for k,v in d.items())
      print(f"{GRADE_LABEL[g]:<27} WRM now : {f(cw)}")
      print(f"{'':<27} domain  : {f(cn)}")
  json.dump(res,open("mapcov.json","w"))
