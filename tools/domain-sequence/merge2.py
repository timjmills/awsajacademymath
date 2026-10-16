import json,sys
O=json.load(open('inputs/audit_fixes.json'))
for g in sys.argv[1:]:
    r=json.load(open(f'../audit3/result2_{g}.json'))
    rm={r_['lesson'] for r_ in O[g].get('remove',[])}
    for m in r.get('moves',[]):
        m={k:v for k,v in m.items() if v not in ('',None)}
        if m['lesson'] in rm or m['anchor'] in rm: print('SKIP (removed lesson)',g,m['lesson'],'|',m['anchor']); continue
        O[g]['moves'].append(m)
    O[g]['copies']+= [ {k:v for k,v in c.items() if v not in ('',None)} for c in r.get('copies',[])]
    O[g]['builds']+= [ {k:v for k,v in c.items() if v not in ('',None)} for c in r.get('builds',[])]
    O[g]['exam2']=r.get('exam'); O[g]['notes2']=r.get('notes',[])
    print(g,len(r.get('moves',[])),'moves',len(r.get('copies',[])),'copies',len(r.get('builds',[])),'builds',r.get('exam'))
json.dump(O,open('inputs/audit_fixes.json','w'),indent=1)
