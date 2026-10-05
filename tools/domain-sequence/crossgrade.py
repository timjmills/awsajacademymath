import json,re
from collections import defaultdict,Counter
from core import *
from plan import classify
# full CCSS list per grade from the mapping's coverage tables
c=json.load(open(MAP))['fileContent'].split('\n')
ALLSTD=defaultdict(list)
for l in c:
    p=[x.strip() for x in l.split('|')]
    if len(p)>3 and re.match(r'^(K|\d)\.[A-Z]{1,3}\.[A-Z]\.\d+$',p[1]):
        g={"K":"K","1":"G1","2":"G2","3":"G3","4":"G4","5":"G5"}[p[1].split('.')[0]]
        if p[1] not in ALLSTD[g]: ALLSTD[g].append(p[1])
GKEY={0:"K",1:"G1",2:"G2",3:"G3",4:"G4",5:"G5"}
def top(code): return ".".join(code.split(".")[:4])
steps={g:classify(g) for g in GR}
def covered(g,stepl):
    n=GNUM[g]; s=set()
    for st in stepl:
        for cd in st['codes']:
            if gnum(cd)==n: s.add(top(cd))
    return s
before={g:covered(g,steps[g]) for g in GR}
if __name__=="__main__":
  # candidate moves: steps whose kind is year-ahead (all codes above grade, or G3 decimals)
  moves=defaultdict(list)
  for g in GR:
      n=GNUM[g]
      for st in steps[g]:
          if not (st['kind'].startswith('year-ahead') or st['dom']=="EXT"): continue
          ups=sorted({gnum(cd) for cd in st['codes'] if gnum(cd)>n})
          tgt=[u for u in ups if u<=5]
          if not tgt: moves["STAYS"].append((g,st)); continue
          moves[GKEY[tgt[0]]].append((g,st))
  print("Full CCSS standards per grade:",{g:len(ALLSTD[g]) for g in GR})
  print()
  for r in GR:
      inc=moves.get(r,[])
      newcodes=defaultdict(int); fill=0; dup=0
      after=set(before[r])
      for g,st in inc:
          rc={top(cd) for cd in st['codes'] if gnum(cd)==GNUM[r]}
          if rc-before[r]: fill+=1
          else: dup+=1
          after|=rc
      miss_b=[s for s in ALLSTD[r] if s not in before[r]]
      miss_a=[s for s in ALLSTD[r] if s not in after]
      src=Counter(g for g,_ in inc)
      print(f"{GRADE_LABEL[r]:<27} standards {len(ALLSTD[r])} | covered in own guide now {len(ALLSTD[r])-len(miss_b)} | incoming steps {len(inc)} from {dict(src)} -> {fill} fill a gap, {dup} repeat taught content | covered after move {len(ALLSTD[r])-len(miss_a)}")
      if miss_b: print(f"   missing now  : {miss_b}")
      if miss_a: print(f"   missing after: {miss_a}")
  print()
  print("Steps with no K-5 home (Grade 6 only):",len(moves['STAYS']),Counter(g for g,_ in moves['STAYS']))
  json.dump({r:[(g,st['lesson']) for g,st in v] for r,v in moves.items()},open("moves.json","w"))
