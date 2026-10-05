import json,collections,re
J=json.load(open('out/domain_sequence.json'))['grades']
W=json.load(open('inputs/site_weeks.json'))
for g,v in J.items():
    it=v['items']; steps=[i for i in it if i['item']=='step']
    names=collections.Counter(i['lesson'] for i in steps)
    dup=[n for n,c in names.items() if c>1]
    mapi=[k for k,i in enumerate(it) if i['item']=='map_window'][0]
    bad3=[i['lesson'] for k,i in enumerate(it) if i['item']=='step' and ((k>mapi)!=i['enrichment'])]
    # contiguity: grade-level domain runs
    order=[i['domain'] for i in it[:mapi] if i['item']=='step']
    runs=[d for k,d in enumerate(order) if k==0 or d!=order[k-1]]
    exams=[(i['domain'],i['week'],i['semester']) for i in it if i['item']=='exam']
    cov=v['ccss_coverage']; mapw=v['map_window_week']
    uncovered=[c['standard'] for c in cov if not c['first_taught_week'] or c['first_taught_week']>mapw]
    load=collections.Counter(i['week'] for i in it[:mapi] if i['item']=='step')
    out=[w for w in sorted(load) if not 3<=load[w]<=5]
    print(f"{g}: steps {len(steps)} dup {dup} | runs {runs} contiguous={len(runs)==len(set(runs))} | wrong side of MAP {bad3} | MAP W{mapw} last exam W{v['last_domain_exam_week']} | standards {len(cov)-len(uncovered)}/{len(cov)} | S1/S2 {v['power_standards_by_exam_semester']}")
    print('    exams',exams); print('    weeks outside 3-5:',{f'W{w:02d}({W[f"W{w:02d}"]["days"]}d)':load[w] for w in out})
