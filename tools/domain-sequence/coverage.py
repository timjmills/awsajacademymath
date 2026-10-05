# CCSS coverage: first grade-level week each of the grade's standards is taught (writes ccss_cov.json)
import json
from crossgrade import ALLSTD, top
from core import GR, GNUM, gnum
A=json.load(open("final_map.json")); cov={}
for g in GR:
    first={}
    for r in A[g]['rows']:
        if r[0]=="" or str(r[10]).startswith("ENRICH"): continue
        for c in [x.strip() for x in r[8].split(",") if x.strip()]:
            if gnum(c)==GNUM[g]: first.setdefault(top(c),(r[1],r[7]))
    cov[g]=[(s,first[s][0] if s in first else None,first[s][1] if s in first else "") for s in ALLSTD[g]]
json.dump(cov,open("ccss_cov.json","w")); print("ccss_cov.json:",{g:sum(1 for x in v if x[1] and x[1]<=32) for g,v in cov.items()})
