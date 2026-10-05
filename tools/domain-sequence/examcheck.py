# Exam check: every booklet question vs the week its standard(s) are first taught (writes examcheck_rows.json)
import csv,json,os
from core import GR,GRADE_LABEL
from assesscheck import tdom,top
A=json.load(open("final_map.json"))
FIX={("K","q5","Counting"):"Move this question to the Base Ten test: filling ten frames to 15 is composing a teen number (K.NBT.A.1), taught after the Counting exam.",
     ("G3","q1","Fractions"):"Low risk: the fractions lessons partition shapes into equal parts. Fine to keep.",
     ("G3","q2","Fractions"):"Low risk: the fractions lessons partition shapes into equal parts. Fine to keep.",
     ("G3","q4","Fractions"):"Low risk: the fractions lessons partition shapes into equal parts. Fine to keep.",
     ("G4","q2","Base Ten"):"Above grade: '1/10 of' is Grade 5 (5.NBT.A.1). Rewrite as 'worth 10 times' (4.NBT.A.1) or drop.",
     ("G4","q6","Algebraic"):"Above grade: dividing by a 2-digit number is Grade 5 (5.NBT.B.6). Change to a 1-digit divisor.",
     ("G4","q7","Algebraic"):"Above grade: dividing by a 2-digit number is Grade 5 (5.NBT.B.6). Change to a 1-digit divisor.",
     ("G5","q9","Algebraic"):"Split it: keep the pattern table and ordered pairs on the OA exam; move the plotting part to the Geometry exam (coordinates are taught after the OA exam).",
     ("G5","q8","Geometry"):"Booklet labels it 5.G.3 but drawing quadrilaterals is Grade 3 review. Relabel to 5.G.B.3 and ask students to classify the quadrilaterals they draw."}
out=[]
for g in GR:
    first={}
    for r in A[g]['rows']:
        if r[0]=="" or str(r[10]).startswith("ENRICH"): continue
        for c in [x.strip() for x in r[8].split(",") if x.strip()]: first.setdefault(top(c),r[1])
    exam={d['dom']:d['exam'] for d in A[g]['cal'] if d['exam']}
    for it in csv.DictReader(open(os.path.join("inputs",f"assess_items_{g}.tsv")),delimiter="\t"):
        d=tdom(it['test']); ew=exam.get(d)
        codes=[c.strip() for c in (it['ccss'],it.get('ccss2') or '') if c and c.strip()]
        fws=[first.get(top(c)) for c in codes]
        bad=[c for c,fw in zip(codes,fws) if fw is None or (ew and fw>ew)]
        fix=next((txt for (gg,q,t),txt in FIX.items() if gg==g and q.lstrip('q')==str(it['q']) and t.lower() in it['test'].lower()),"")
        out.append([GRADE_LABEL[g],it['test'],it['q'],it['item'],", ".join(codes),
            ", ".join(f"W{fw:02d}" if fw else "not taught" for fw in fws), f"W{ew:02d}" if ew else "","CHECK" if bad else "OK", fix or (it.get('notes') or "")])
json.dump(out,open("examcheck_rows.json","w")); print("examcheck_rows.json:",len(out),"questions,",sum(1 for r in out if r[7]=="CHECK"),"to check")
