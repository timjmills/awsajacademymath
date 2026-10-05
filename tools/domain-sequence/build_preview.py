# Build preview/index.html: the live site with K-G5 Weekly Pacing re-sequenced by CCSS domain.
# Inputs: ../../../../home/user/awsajacademymath/index.html (live), out/domain_sequence.json, inputs/*.json
import re, json, gzip, base64, sys, collections, math, os
from core import SITEWEEKS, dkey

REPO = os.environ.get('AWSAJ_REPO', os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
live_html = open(os.path.join(REPO, 'index.html')).read()
m = re.search(r'(<script id="__data"[^>]*>)(.*?)(</script>)', live_html, re.S)
D = json.loads(gzip.decompress(base64.b64decode(m.group(2).strip())))
SEQ = json.load(open('out/domain_sequence.json'))['grades']
PILLS = json.load(open('inputs/live_pills.json'))
TESTS = json.load(open('inputs/domain_tests.json'))
RES = D['RESOURCES']
PAC = D['PACING']
GR = ['K', 'G1', 'G2', 'G3', 'G4', 'G5']
DOMNAME = {"CC": "Counting & Cardinality", "OA": "Operations & Algebraic Thinking", "NBT": "Number & Operations in Base Ten",
           "NF": "Number & Operations: Fractions", "MD": "Measurement & Data", "G": "Geometry"}
WEEKS = [f"W{i:02d}" for i in range(1, 40)]
DAYS = {w: SITEWEEKS[w]['days'] for w in WEEKS}
TAG = {"K": "Y1/KG", "G1": "Y2/Gr.1", "G2": "Y3/Gr.2", "G3": "Y4/Gr.3", "G4": "Y5/Gr.4", "G5": "Y6/Gr.5"}
GLABEL = {0: "Kindergarten", 1: "Grade 1", 2: "Grade 2", 3: "Grade 3", 4: "Grade 4", 5: "Grade 5", 6: "Grade 6"}


def wn(w): return int(w[1:])


def live_index(g):
    """Live Standard-track records by title key (in teaching order), and Priority / Intervention membership."""
    recs = collections.defaultdict(list); mem = {'priority': collections.Counter(), 'intervention': collections.Counter()}
    for w in PAC['grades'][g]['weeks']:
        for st in w['t']['standard']['st']:
            if st.get('f') == 'supportOpt': continue
            recs[dkey(st['n'])].append((w['wk'], st))
        for tr in mem:
            for st in w['t'][tr]['st']:
                if st.get('f') != 'supportOpt': mem[tr][dkey(st['n'])] += 1
    return recs, mem


def res_lookup(g, title):
    """(block, step) of a title in a grade's White Rose Drive index."""
    hits = (RES.get(g, {}).get('n') or {}).get(dkey(title)) or []
    return (str(hits[0][0]), str(hits[0][1])) if hits else (None, None)


def spread(items, weeks):
    """Assign items to the given weeks in proportion to teaching days (same rule as the Standard track)."""
    wl = [w for w in weeks if DAYS[w] > 0] or weeks
    tot = sum(DAYS[w] for w in wl) or len(wl)
    edges = []; cum = 0
    for w in wl: cum += DAYS[w] or 1; edges.append((cum / tot, w))
    out = collections.defaultdict(list)
    for i, it in enumerate(items):
        f = (i + 0.5) / max(1, len(items))
        out[next(w for e, w in edges if f <= e + 1e-9)].append(it)
    return out


report = {}
for g in GR:
    seq = SEQ[g]; recs, mem = live_index(g); used = collections.Counter()
    # ---- one record per sequence item
    items = []
    for it in seq['items']:
        if it['item'] != 'step':
            items.append(dict(kind=it['item'], dom=it['domain'], week=f"W{it['week']:02d}", sem=it['semester'])); continue
        k = dkey(it['lesson']); st = None
        if it['copied_from_grade']:
            src = it['copied_from_grade']; b, s = res_lookup(src, it['lesson'])
            st = {"s": int(s) if s else None, "b": int(b) if b else None, "g": src}
        elif recs.get(k) and used[k] < len(recs[k]):
            wk, live = recs[k][used[k]]; used[k] += 1
            st = {kk: live[kk] for kk in ('s', 'b', 'f') if kk in live}
        elif it['build_lesson']:
            st = {"s": "SUP", "b": None, "f": "committee"}
        else:
            b, s = res_lookup(g, it['lesson'])
            st = {"s": int(s) if s else None, "b": int(b) if b else None}
        if it['build_lesson']: st.update(s="SUP", f="committee")
        st.update(n=it['lesson'], c=it['ccss'], p=1 if it['power_standards'] else 0)
        if it['enrichment']: st['e'] = it['enrichment_grade'] or 0
        items.append(dict(kind='step', dom=it['domain'], week=f"W{it['week']:02d}", st=st, key=k,
                          pri=bool(mem['priority'][k]) or bool(it['build_lesson']) or bool(it['copied_from_grade']),
                          inv=bool(mem['intervention'][k]) or bool(it['build_lesson']) or bool(it['copied_from_grade']),
                          enr=it['enrichment']))
    # ---- runs: each grade-level domain run ends with its exam; the enrichment block follows the MAP row
    runs = []; cur = []
    for x in items:
        if x['kind'] == 'map_window':
            runs.append(('map', [x])); continue
        cur.append(x)
        if x['kind'] == 'exam': runs.append(('dom', cur)); cur = []
    if cur: runs.append(('enr', cur))
    weeks = {w: {"wk": w, "t": {t: {"st": [], "sup": 0, "ev": [], "pl": []} for t in ('standard', 'priority', 'intervention')}} for w in WEEKS}
    units = {}; exams = {}; mapwk = None; ui = 0
    for kind, run in runs:
        if kind == 'map':
            mapwk = run[0]['week']
            for tr in weeks[mapwk]['t']: weeks[mapwk]['t'][tr]['st'].append({'st': {"f": "map", "n": "MAP Growth window (spring)"}})
            continue
        steps = [x for x in run if x['kind'] == 'step']
        rw = [x['week'] for x in run]
        span = [w for w in WEEKS if wn(min(rw)) <= wn(w) <= wn(max(rw))]
        for x in steps: weeks[x['week']]['t']['standard']['st'].append(x)
        for tr, flag in (('priority', 'pri'), ('intervention', 'inv')):
            for w, lst in spread([x for x in steps if x[flag]], span).items(): weeks[w]['t'][tr]['st'] += lst
        if kind == 'dom':
            ex = run[-1]; d = ex['dom']; ui += 1
            for tr in weeks[ex['week']]['t']: weeks[ex['week']]['t'][tr]['st'].append({'st': {"f": "exam", "n": "Domain exam · " + DOMNAME[d], "d": d}})
            exams[ex['week']] = {"dom": d, "n": DOMNAME[d], "sem": ex['sem'], "t": TESTS[g].get(d)}
            units[str(ui)] = {"n": DOMNAME[d], "a": span[0], "z": span[-1], "dom": d, "kind": "domain",
                              "pw": sorted({p for x in steps for p in (x['st']['c'] if x['st']['p'] else []) if p in {q for it in seq['items'] if it['item'] == 'step' for q in it['power_standards']}}),
                              "pills": [], "test": TESTS[g].get(d)}
        else:
            units['E'] = {"n": "Enrichment lessons", "a": span[0], "z": span[-1], "dom": "", "kind": "enrich", "pw": [], "pills": []}
    # ---- pills follow the lessons: a lesson brings the support lessons of the live week it was taught in
    step_pills = {}
    for k, lst in recs.items():
        step_pills[k] = [p for wk, _ in lst for p in PILLS[g].get(wk, [])]
    for w in WEEKS:
        cnt = collections.Counter(); first = {}
        for x in weeks[w]['t']['standard']['st']:
            for p in step_pills.get(x.get('key'), []):
                pk = dkey(p['name']) + p.get('tag', '')
                cnt[pk] += 1; first.setdefault(pk, p)
        pl = [first[pk] for pk, _ in cnt.most_common(10)]
        for tr in weeks[w]['t']:
            cell = weeks[w]['t'][tr]
            cell['st'] = [x['st'] for x in cell['st']]
            cell['pl'] = pl if tr == 'standard' else []
            busy = len([x for x in cell['st'] if x.get('f') not in ('exam', 'map')]) + (1 if w in exams else 0)
            cell['sup'] = max(0, DAYS[w] - busy)
            if w == 'W01': cell['ev'].append("Baseline entry task · number & calculation snapshot")
    wl = []
    for w in WEEKS:
        o = weeks[w]
        if w in exams: o['exam'] = exams[w]
        if w == mapwk: o['map'] = 1
        wl.append(o)
    PAC['grades'][g] = {"weeks": wl, "units": units}
    report[g] = dict(map=mapwk, exams={w: e['dom'] for w, e in exams.items()},
                     load={tr: round(sum(len(weeks[w]['t'][tr]['st']) for w in WEEKS if wn(w) < wn(mapwk)) / max(1, len([w for w in WEEKS if wn(w) < wn(mapwk) and DAYS[w]])), 2) for tr in ('standard', 'priority', 'intervention')},
                     nofiles=[x['st']['n'] for x in items if x['kind'] == 'step' and x['st'].get('f') != 'committee' and x['st'].get('b') is None])
PAC['domainSeq'] = True

# ---- app patches (preview only)
app_m = re.search(r'(<script id="__app" type="text/plain">)(.*?)(</script>)', live_html, re.S)
app = app_m.group(2)


def sub(a, b, count=1):
    global app
    n = app.count(a)
    assert n == count, (a[:80], n)
    app = app.replace(a, b)


# 1. separate browser storage; tracking is read-only in the preview
app = app.replace('localStorage.', '__pvLS.')
sub('fetch(TRACKER_API+path,{...opts,headers:h})',
    '(opts&&opts.method&&opts.method!=="GET"?Promise.reject(new Error("Preview: tracking is read-only")):fetch(TRACKER_API+path,{...opts,headers:h}))')
# 2. support panel comes from the week's own lessons; no block-based pull-ups
sub('function pulledUpByWeek(gradeId){', 'function pulledUpByWeek(gradeId){if((window.PACING||{}).domainSeq&&gradeId!=="PK")return{};')
# 3. lesson files: copied-in steps open their source grade
sub('React.createElement(ResBadge,{gradeId:grade.id,block:st.b,step:st.s,title:st.n,compact:true})',
    'React.createElement(ResBadge,{gradeId:st.g||grade.id,block:st.b,step:st.s,title:st.n,compact:true}),st.g&&React.createElement("span",{className:"mono",title:"Copied in from "+(GRADE_BY_ID[st.g]?GRADE_BY_ID[st.g].name:st.g)+" so this standard is taught in its own grade. The files are in that grade\'s folder.",style:{fontSize:8,fontWeight:700,letterSpacing:"0.06em",color:"#1565C0",background:"#E3EEFB",border:"1px solid #9DBFE8",borderRadius:4,padding:"1px 4px",marginLeft:4}},"COPIED IN · "+(GRADE_BY_ID[st.g]?GRADE_BY_ID[st.g].name.toUpperCase():st.g)),st.e!=null&&React.createElement("span",{className:"mono",title:"Enrichment lesson: above grade level",style:{fontSize:8,fontWeight:700,letterSpacing:"0.06em",color:"#5B2A86",background:"#EFE6F8",border:"1px solid #C6A9E3",borderRadius:4,padding:"1px 4px",marginLeft:4}},st.e?"ENRICHMENT · GRADE "+st.e+" STANDARD":"ENRICHMENT")')
# lessons with no White Rose step and no BUILD flag fall back to a title search
sub('!isSup&&st.f!=="committee"&&React.createElement(ResBadge,{gradeId:st.g||grade.id,block:st.b',
    '!isSup&&st.f!=="committee"&&React.createElement(ResBadge,{gradeId:st.g||grade.id,block:st.b==null?undefined:st.b,unitName:st.b==null?" ":undefined')
# 3b. exam / MAP markers sit inside each strand at the point they happen
sub('steps.map((st,j)=>{const isSup=st.s==="SUP";',
    'steps.map((st,j)=>{if(st.f==="exam"||st.f==="map")return React.createElement("div",{key:j,className:"mono",style:{marginTop:j?6:0,padding:"4px 6px",borderRadius:4,fontSize:9,fontWeight:700,letterSpacing:"0.06em",color:"#FFFFFF",background:st.f==="exam"?"#B71C1C":"#5B2A86"}},st.f==="exam"?"★ "+st.n.toUpperCase():"◆ MAP GROWTH WINDOW (SPRING)");const isSup=st.s==="SUP";')
# 4. unit band: domain runs show their test; the enrichment block has its own label
sub('"▶ NEW UNIT · B",ub," ",uu.n.toUpperCase()," ",React.createElement("span",{style:{opacity:0.6}},uu.a,"–",uu.z)),React.createElement(BlockBand,{gid:grade.id,block:ub})',
    'uu.kind==="domain"?"▶ DOMAIN "+ub+" · ":uu.kind==="enrich"?"▶ ":"▶ NEW UNIT · B"+ub+" ",uu.n.toUpperCase()," ",React.createElement("span",{style:{opacity:0.6}},uu.a,"–",uu.z)),uu.kind?(uu.kind==="enrich"?React.createElement("span",{className:"mono",style:{fontSize:9.5,color:"#1A1614"}},"ABOVE GRADE LEVEL · AFTER THE MAP WINDOW"):null):React.createElement(BlockBand,{gid:grade.id,block:ub})')
sub('React.createElement("span",{style:{fontWeight:700}},"B",ub)," ",uu.n',
    'React.createElement("span",{style:{fontWeight:700}},uu.kind==="domain"?"D"+ub:uu.kind==="enrich"?"":"B"+ub)," ",uu.n')
# 5. exam and MAP rows after the week they fall in
EXAM_ROW = ('w.exam&&React.createElement("div",{style:{background:"#B71C1C",color:"#FFFFFF",padding:"8px 12px",display:"flex",gap:14,alignItems:"center",flexWrap:"wrap",borderTop:"2px solid #7F0000"}},'
            'React.createElement("span",{className:"mono",style:{fontSize:11,fontWeight:700,letterSpacing:"0.08em"}},"★ DOMAIN EXAM · "+w.exam.n.toUpperCase()),'
            'React.createElement("span",{className:"mono",style:{fontSize:9.5,opacity:0.85}},w.wk+" · "+(w.exam.sem==="S1"?"SEMESTER 1 REPORT":"SEMESTER 2 REPORT")),'
            'w.exam.t&&React.createElement("a",{href:"https://drive.google.com/file/d/"+w.exam.t[1]+"/view",target:"_blank",rel:"noopener noreferrer",className:"mono",title:w.exam.t[0],style:{fontSize:9.5,fontWeight:700,letterSpacing:"0.06em",color:"#B71C1C",background:"#FFFFFF",borderRadius:5,padding:"3px 8px",textDecoration:"none"}},"OPEN THE TEST ↗")),'
            'w.map&&React.createElement("div",{style:{background:"#5B2A86",color:"#FFFFFF",padding:"9px 12px",borderTop:"2px solid #3A1660"}},'
            'React.createElement("span",{className:"mono",style:{fontSize:11,fontWeight:700,letterSpacing:"0.08em"}},"◆ MAP GROWTH WINDOW (SPRING) · "+w.wk),'
            'React.createElement("span",{className:"mono",style:{fontSize:9.5,opacity:0.85,marginLeft:12}},"EVERY GRADE-LEVEL STANDARD IS TAUGHT AND EXAMINED ABOVE THIS LINE · ENRICHMENT LESSONS FOLLOW")),')
sub('pills.map((p,x)=>React.createElement(SupportPill,{key:x,p:p}))));})());})),React.createElement(CCModal,{code:cc,onClose:()=>setCc(null)}));}',
    'pills.map((p,x)=>React.createElement(SupportPill,{key:x,p:p}))));})(),' + EXAM_ROW[:-1] + ');})),React.createElement(CCModal,{code:cc,onClose:()=>setCc(null)}));}')
# 5b. unit labels: D1, D2 ... for domain runs, E for the enrichment block
sub('fontWeight:700}},"B",b),React.createElement("span",{style:{flex:1}},u.n)',
    'fontWeight:700}},u.kind==="domain"?"D":u.kind==="enrich"?"":"B",b),React.createElement("span",{style:{flex:1}},u.n)')
sub('style:{fontSize:11,fontWeight:700}},"B",b)', 'style:{fontSize:11,fontWeight:700}},(pg.units[b]||{}).kind==="domain"?"D":(pg.units[b]||{}).kind==="enrich"?"":"B",b)')
sub('Every strand finishes each unit together and each ends with Assessment A plus a Flashback spiral.',
    'Every strand finishes each unit together. Each unit is one CCSS domain and ends with its domain exam; the enrichment lessons come after the spring MAP window.')
# 6. Units directory lists each domain run's lessons
sub('if(String(st.b)===String(b))out.push({...st,wk:w.wk});return out;}',
    'if(pg.units[b]&&pg.units[b].kind?(wknum(pg.units[b].a)<=wknum(w.wk)&&wknum(w.wk)<=wknum(pg.units[b].z)&&(pg.units[b].kind==="enrich")===(st.e!=null)):String(st.b)===String(b))out.push({...st,wk:w.wk});return out;}')
if 'const wknum=' not in app[app.index('function GradeUnits'):app.index('function GradeUnits') + 400]:
    sub('function GradeUnits({grade}){const pg=PAC.grades[grade.id];', 'function GradeUnits({grade}){const pg=PAC.grades[grade.id];const wknum=x=>parseInt(String(x).slice(1),10);')

LS = ('<script>window.__pvLS={getItem:function(k){try{return localStorage.getItem("preview_"+k)}catch(e){return null}},'
      'setItem:function(k,v){try{localStorage.setItem("preview_"+k,v)}catch(e){}},removeItem:function(k){try{localStorage.removeItem("preview_"+k)}catch(e){}}};</script>')
BANNER = ('<div id="pvbar" style="position:sticky;top:0;z-index:9990;background:#5B2A86;color:#fff;font:600 12px/1.4 system-ui,sans-serif;padding:7px 14px;text-align:center">'
          'PREVIEW · K to Grade 5 re-sequenced by CCSS domain · not the live site · lesson tracking is read-only here '
          '<a href="../" style="color:#FFD84D;margin-left:10px">open the live site</a></div>')

data = base64.b64encode(gzip.compress(json.dumps(D, separators=(',', ':'), ensure_ascii=False).encode(), 9)).decode()
html = live_html[:m.start(2)] + data + live_html[m.end(2):]
am = re.search(r'(<script id="__app" type="text/plain">)(.*?)(</script>)', html, re.S)
html = html[:am.start(2)] + app + html[am.end(2):]
html = html.replace('<title>Awsaj Math Curriculum</title>', '<title>PREVIEW · Awsaj Math Curriculum</title><meta name="robots" content="noindex">', 1)
html = html.replace('<body>', '<body>' + LS + BANNER, 1)
os.makedirs(os.path.join(REPO, 'preview'), exist_ok=True)
open(os.path.join(REPO, 'preview', 'index.html'), 'w').write(html)
json.dump(report, open('out/preview_report.json', 'w'), indent=1)
for g, r in report.items(): print(g, r)
