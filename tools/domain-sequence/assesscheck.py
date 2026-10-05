import csv,json,os
from core import GR,GNUM,gnum,GRADE_LABEL
A=json.load(open("final_map.json"))
def tdom(t):
    t=t.lower()
    for k,d in [("counting","CC"),("base ten","NBT"),("algebraic","OA"),("fraction","NF"),("measurement","MD"),("geometry","G")]:
        if k in t: return d
def top(c): return ".".join(c.split(".")[:4])
if __name__=="__main__":
  RES={}; total=ok_n=0
  for g in GR:
      rows=A[g]['rows']
      first={}
      for r in rows:
          if r[0]=="" or str(r[10]).startswith("ENRICH"): continue
          for c in [x.strip() for x in r[8].split(",") if x.strip()]:
              first.setdefault(top(c),r[1])
      exam={d['dom']:d['exam'] for d in A[g]['cal'] if d['exam']}
      items=list(csv.DictReader(open(os.path.join("inputs",f"assess_items_{g}.tsv")),delimiter="\t"))
      flags=[]; tested=set()
      for it in items:
          d=tdom(it['test']); ew=exam.get(d)
          for role,c in (("main",it['ccss']),("also",it.get('ccss2',''))):
              c=(c or "").strip()
              if not c: continue
              tested.add(top(c)) if role=="main" else None
              fw=first.get(top(c))
              if fw is None:
                  flags.append((it['test'],it['q'],it['item'],c,role,"never taught in this grade's sequence",ew,None))
              elif ew and fw>ew:
                  flags.append((it['test'],it['q'],it['item'],c,role,f"taught W{fw:02d}, after the {d} exam (W{ew:02d})",ew,fw))
      nflag_q=len({(f[0],f[1]) for f in flags})
      total+=len(items); ok_n+=len(items)-nflag_q
      RES[g]=dict(n=len(items),flags=flags,by_test={t:sum(1 for i in items if i['test']==t) for t in dict.fromkeys(i['test'] for i in items)})
      print(f"{GRADE_LABEL[g]}: {len(items)} questions | {len(items)-nflag_q} fully taught before their exam | {nflag_q} flagged")
      for f in flags: print(f"    [{f[4]}] {f[0][:28]} q{f[1]}: {f[2][:55]} | {f[3]} | {f[5]}")
  print(f"TOTAL {ok_n}/{total} questions fully taught before their domain exam")
  json.dump(RES,open("assesscheck.json","w"),default=str)
