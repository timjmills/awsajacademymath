import json,csv,datetime
from core import GRADE_LABEL,GR,DOMNAME
A=json.load(open("final_map.json")); cov=json.load(open("ccss_cov.json"))
WRMY={"K":"Year 1","G1":"Year 2","G2":"Year 3","G3":"Year 4","G4":"Year 5","G5":"Year 6"}
def iso(d):
    return datetime.datetime.strptime(d,"%d %b %Y").date().isoformat() if d else ""
out={"meta":{"title":"WRM small steps re-sequenced by CCSS domain, K-Grade 5, 2026-27",
  "generated":"2026-10-05","pk4":"unchanged (no CCSS standards)",
  "sources":["WRM_to_CCSS_Mapping_v3 (Drive 11LMdZVoBNHJNU43dPVMtcZUk-iXO-aThuk6mZUcHI7M)",
             "Weekly Pacing Guide PDFs K-G5 (Curriculum Hub / Printable Pacing Guides, printed 22 Aug 2026)",
             "Math Standards for Report Cards (Drive 12uCqgMKKOJw-QT9kRYVJwr3_rY6KlsYsLD76q244h6c)"],
  "pace":"Standard track; items spread evenly over 39 teaching weeks (3-5 slots/week); weeks and dates are the pacing guides' own"},
  "grades":{}}
flat=[]
for g in GR:
    v=A[g]; items=[]
    for row,k in zip(v['rows'],v['keys']):
        typ=row[10]
        it={"seq":len(items)+1,"step_no":row[0] if row[0]!="" else None,
            "item":"exam" if typ=="EXAM" else "map_window" if typ=="MAP" else "step",
            "week":row[1],"quarter":row[2],"week_of":iso(row[3]),"semester":row[4],
            "domain":row[5] if typ!="MAP" else None,"lesson":row[7],"ccss":k['codes'],"power_standards":k['power'],
            "status":typ,"enrichment":str(typ).startswith("ENRICHMENT"),
            "enrichment_grade":(int(typ.split("Grade ")[1].split()[0]) if str(typ).startswith("ENRICHMENT") and "Grade " in typ else None),
            "build_lesson":k['is_build'],"copied_from_grade":k['copied_from'],
            "site_unit":k['site_unit'],"site_step":k['site_step'],
            "orig_pacing_week":k['orig_week'],"orig_pacing_block":k['orig_block'],
            "teaching_note":row[13] or ""}
        items.append(it)
        flat.append({"grade":g,**{x:(";".join(y) if isinstance(y,list) else y) for x,y in it.items()}})
    out["grades"][g]={"label":GRADE_LABEL[g],"wrm_year":WRMY[g],"domain_order":v['order'],
        "map_window_week":v['mapweek'],"last_domain_exam_week":v['lastexam'],
        "power_standards_by_exam_semester":{"S1":v['balance']['exam'][0],"S2":v['balance']['exam'][1]},
        "domain_exams":[{"domain":c['dom'],"name":c['name'],"steps":c['steps'],"exam_week":c['exam'],
            "exam_week_of":iso(c['exam_date']),"semester":c['sem'],"power_standards":c['power']} for c in v['cal'] if c['dom']!="EXT"],
        "ccss_coverage":[{"standard":s,"first_taught_week":w,"first_step":st} for s,w,st in cov[g]],
        "items":items}
json.dump(out,open("out/domain_sequence.json","w"),indent=1,ensure_ascii=False)
with open("out/domain_sequence.csv","w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(flat[0].keys())); w.writeheader(); w.writerows(flat)
print("items",len(flat),"| per grade",{g:len(out['grades'][g]['items']) for g in GR})
print(json.dumps(out['grades']['G5']['domain_exams'][:2],indent=0)[:400])
print(json.dumps([i for i in out['grades']['G4']['items'] if i['copied_from_grade']][0],indent=0))
