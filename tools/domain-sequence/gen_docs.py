"""Printable Weekly Pacing Guide (landscape) and Teaching & Pacing Handbook (portrait)
for K-G5, built from the preview's data. Writes HTML to out/docs/; render_docs.js prints PDFs."""
import re, json, gzip, base64, os, html, sys

REPO = os.environ.get('AWSAJ_REPO', '/home/user/awsajacademymath')
OUT = 'out/docs'
os.makedirs(OUT, exist_ok=True)
H = open(os.path.join(REPO, 'preview', 'index.html')).read()
D = json.loads(gzip.decompress(base64.b64decode(re.search(r'<script id="__data"[^>]*>(.*?)</script>', H, re.S).group(1).strip())))
ADAPT = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else {'UK': {}, 'US': {}}
PAC, CUR, CMAP = D['PACING'], D['CURRICULUM'], D['CCSSMAP']
WD = PAC['weekDates']
GRADES = ['K', 'G1', 'G2', 'G3', 'G4', 'G5']
GNAME = {'K': 'Kindergarten', 'G1': 'Grade 1', 'G2': 'Grade 2', 'G3': 'Grade 3', 'G4': 'Grade 4', 'G5': 'Grade 5'}
YEAR = {'K': 1, 'G1': 2, 'G2': 3, 'G3': 4, 'G4': 5, 'G5': 6}
PREFIX = {'K': 'K.', 'G1': '1.', 'G2': '2.', 'G3': '3.', 'G4': '4.', 'G5': '5.'}
DOMC = {'CC': '#E8B23A', 'OA': '#E06C4F', 'NBT': '#5E9A72', 'NF': '#A866C2', 'MD': '#4A7FD0', 'G': '#7A5CCB', '': '#8C8C8C'}
DOMSHORT = {'CC': 'Counting & Cardinality', 'OA': 'Operations & Algebraic Thinking', 'NBT': 'Number & Operations in Base Ten',
            'NF': 'Number & Operations: Fractions', 'MD': 'Measurement & Data', 'G': 'Geometry'}
STRANDS = [('standard', 'Standard', '~4 new lessons a week'), ('priority', 'Priority', '~3'), ('intervention', 'Intervention', '~2')]
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
e = html.escape
wn = lambda w: int(str(w)[1:])
WEEKS = [w for w in sorted(WD, key=wn)]
TEACH_DAYS = sum(WD[w].get('days', 0) for w in WEEKS)


def norm(t):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'\s*\((?:US|UK)[^)]*\)\s*$', '', t or '').lower())


def dshort(iso):
    y, m, d = iso.split('-')
    return f"{int(d)} {MON[int(m) - 1]}"


def wdates(w):
    x = WD[w]
    a, b = x['start'].split('-'), x['end'].split('-')
    if a[1] == b[1]:
        return f"{int(a[2])}–{int(b[2])} {MON[int(b[1]) - 1]}"
    return f"{dshort(x['start'])} – {dshort(x['end'])}"


def lesson_kind(x):
    if x.get('f') in ('exam', 'map'): return x['f']
    if x.get('f') == 'committee': return 'build'
    if x.get('g'): return 'copy'
    if x.get('e') is not None: return 'enrich'
    return 'core'


def grade_model(g):
    P = PAC['grades'][g]
    units = P['units']
    order = sorted(units.items(), key=lambda kv: (kv[1]['kind'] == 'enrich', wn(kv[1]['a'])))
    dom_units = [b for b, u in order if u['kind'] == 'domain']
    tests = {t['dom']: t for t in D['DOMAIN_TESTS'].get(g, [])}
    mapwk = next((w['wk'] for w in P['weeks'] for x in w['t']['standard'].get('st', []) if x.get('f') == 'map'), None)
    # walk each strand: lessons belong to the current domain until its exam marker, then the next; after the last exam, enrichment
    per = {}
    for s, _, _ in STRANDS:
        i, rows = 0, []
        for w in P['weeks']:
            for x in (w['t'].get(s) or {}).get('st', []):
                k = lesson_kind(x)
                if k == 'exam':
                    i += 1; continue
                if k == 'map': continue
                ub = dom_units[i] if i < len(dom_units) else 'E'
                rows.append({**x, 'wk': w['wk'], 'unit': ub, 'kind': k})
        per[s] = rows
    return P, units, order, dom_units, tests, mapwk, per


def tag_html(x, g):
    k = lesson_kind(x)
    out = []
    if k == 'build': out.append('<span class="tg build">CCSS BUILD · TO BE MADE</span>')
    if k == 'copy': out.append(f'<span class="tg copy">COPIED IN · {e(x["g"])}</span>')
    if k == 'enrich': out.append('<span class="tg enr">ENRICHMENT</span>')
    src = x.get('g') or g
    if norm(x['n']) in ADAPT['UK'].get(src, {}) or '(US' in x['n']: out.append('<span class="tg adapt">ADAPT</span>')
    if norm(x['n']) in ADAPT['US'].get(src, {}): out.append('<span class="tg adapt">US VERSION TO MAKE</span>')
    return ''.join(out)


def lesson_html(x, g):
    k = lesson_kind(x)
    if k == 'exam':
        return f'<div class="ls exam">■ DOMAIN EXAM · {e(DOMSHORT.get(x.get("d"), x.get("d", "")))}</div>'
    if k == 'map':
        return '<div class="ls map">■ MAP GROWTH WINDOW (SPRING)</div>'
    cls = 'ls' + (' pw' if x.get('p') else '') + (' bld' if k == 'build' else '')
    codes = ' '.join(x.get('c') or [])
    return f'<div class="{cls}">{e(x["n"])} <span class="cc">{e(codes)}</span>{tag_html(x, g)}</div>'


CSS_BASE = """
@page{margin:9mm 9mm 11mm}
*{box-sizing:border-box}
body{font-family:'Liberation Sans','DejaVu Sans',Arial,sans-serif;color:#1C1916;margin:0;font-size:9pt;line-height:1.35}
.mono{font-family:'DejaVu Sans Mono','Liberation Mono',monospace;letter-spacing:.04em}
.tg{display:inline-block;font:700 6.2pt 'DejaVu Sans Mono',monospace;letter-spacing:.04em;border-radius:3px;padding:0 3px;margin-left:4px;vertical-align:1px;white-space:nowrap}
.tg.build{background:#E8720C;color:#fff}.tg.copy{background:#DDE8FA;color:#1D4E9E;border:1px solid #A8C1EC}
.tg.enr{background:#EEE3F7;color:#6A3A8C;border:1px solid #CDB2E3}.tg.adapt{background:#FFE8D2;color:#7C2D12;border:1px solid #E9A16B}
.cc{font:6.6pt 'DejaVu Sans Mono',monospace;color:#8A8077}
"""

# ---------------------------------------------------------------- weekly pacing guide
PG_CSS = CSS_BASE + """
@page{size:A4 landscape}
h1{font-size:17pt;margin:0;display:flex;align-items:center;gap:10px}
.gchip{font-size:9pt;color:#fff;border-radius:4px;padding:2px 8px}
.note{border:1px solid #9CC9A8;background:#EEF6F0;border-radius:6px;padding:6px 9px;font-size:7.6pt;margin:6px 0 4px}
.key{font-size:7.4pt;color:#5A524A;margin:3px 0 6px}
table{width:100%;border-collapse:collapse;table-layout:fixed}
thead th{background:#1C1916;color:#fff;font:700 7.4pt 'DejaVu Sans Mono',monospace;letter-spacing:.05em;text-align:left;padding:4px 6px}
thead{display:table-header-group}
tr{page-break-inside:avoid;break-inside:avoid}
td{vertical-align:top;border-bottom:1px solid #E4DCCF;padding:3px 5px}
td.wk{width:74px;font-size:7pt;color:#5A524A}td.wk b{font-size:9pt;color:#1C1916;display:block}
.ls{font-size:7.9pt;padding:1px 3px;margin:1px 0;border-radius:2px}
.ls.pw{background:#FFF1B8}.ls.bld{background:#FFE3C4}
.ls.exam{background:#B71C1C;color:#fff;font:700 7pt 'DejaVu Sans Mono',monospace;letter-spacing:.04em}
.ls.map{background:#5B2A86;color:#fff;font:700 7pt 'DejaVu Sans Mono',monospace;letter-spacing:.04em}
.ev{font-size:7pt;color:#7A7066;font-style:italic;margin-top:2px}
.sup{font-size:6.6pt;color:#7A7066;margin-top:3px}
tr.band td{font:700 8.4pt 'Liberation Sans',sans-serif;color:#fff;padding:4px 7px}
tr.band .sub{font:400 7pt 'DejaVu Sans Mono',monospace;opacity:.92;margin-left:8px}
tr.pills td{background:#FDEDF5;border-bottom:1px solid #E7B5CF;padding:3px 6px}
.ph{font:700 6.8pt 'DejaVu Sans Mono',monospace;color:#C2185B;margin-right:6px}
.pill{display:inline-block;font-size:6.6pt;border:1px solid #D9B3C7;background:#fff;border-radius:8px;padding:0 5px;margin:1px 2px}
.pill i{font-style:normal;font-weight:700;margin-right:3px}
tr.examrow td{background:#FFF6F5;border:1px solid #E9B8B3;font-size:7.8pt;padding:4px 7px}
tr.examrow b{color:#B71C1C}
a{color:#B71C1C}
.foot{font-size:7pt;color:#8A8077;margin-top:8px}
"""


def pacing_guide(g):
    P, units, order, dom_units, tests, mapwk, per = grade_model(g)
    starts = {}
    for b, u in order:
        starts.setdefault(u['a'], []).append((b, u))
    rows = []
    for w in P['weeks']:
        wk = w['wk']
        for b, u in starts.get(wk, []):
            col = DOMC.get(u['dom'], '#8C8C8C')
            if u['kind'] == 'domain':
                t = tests.get(u['dom'])
                sub = f"{u['a']}–{u['z']} · domain exam {t['wk'] if t else u['z']}" + (f" · power standards {', '.join(u['pw'])}" if u['pw'] else '')
                label = f"D{b} · {u['n']}"
            else:
                sub = f"{u['a']}–{u['z']} · after the spring MAP window · above grade level and consolidation"
                label = 'ENRICHMENT · ' + u['n']
            rows.append(f'<tr class="band"><td colspan="4" style="background:{col}">{e(label)}<span class="sub">{e(sub)}</span></td></tr>')
        x = WD[wk]
        cells = [f'<td class="wk"><b>{wk}</b>{x["q"]} · {wdates(wk)}<br>{x.get("days", 0)} teaching day{"s" if x.get("days", 0) != 1 else ""}</td>']
        for s, _, _ in STRANDS:
            t = w['t'].get(s) or {}
            inner = ''.join(lesson_html(y, g) for y in t.get('st', []))
            if t.get('ev'): inner += ''.join(f'<div class="ev">{e(v)}</div>' for v in t['ev'])
            if t.get('sup'): inner += f'<div class="sup">+ {t["sup"]} support block{"s" if t["sup"] > 1 else ""}</div>'
            if not inner: inner = '<div class="sup">no lessons this week</div>'
            cells.append(f'<td>{inner}</td>')
        rows.append('<tr>' + ''.join(cells) + '</tr>')
        pl = (w['t'].get('standard') or {}).get('pl') or []
        if pl:
            ps = ''.join(f'<span class="pill" style="border-color:{p.get("color", "#D9B3C7")}"><i style="color:{p.get("color", "#C2185B")}">{e(p.get("tag", ""))}</i>{e(p["name"])}</span>' for p in pl)
            rows.append(f'<tr class="pills"><td colspan="4"><span class="ph">SUPPORT BLOCK · PICK ONE</span>{ps}</td></tr>')
        for y in (w['t'].get('standard') or {}).get('st', []):
            if y.get('f') == 'exam':
                t = tests.get(y.get('d'))
                link = f' · <a href="https://drive.google.com/file/d/{t["t"][1]}/view">{e(t["t"][0])}</a>' if t and t.get('t') else ''
                sem = (' · counts for the ' + ('Semester 1' if t['sem'] == 'S1' else 'Semester 2') + ' report') if t else ''
                rows.append(f'<tr class="examrow"><td colspan="4"><b>DOMAIN EXAM · {e(DOMSHORT.get(y.get("d"), ""))}</b> · sat in {wk} on every strand{sem}{link}</td></tr>')
            if y.get('f') == 'map':
                rows.append(f'<tr class="examrow" style="background:#F3ECF9"><td colspan="4" style="background:#F3ECF9;border-color:#C9B3E0"><b style="color:#5B2A86">MAP GROWTH WINDOW · {wk}</b> · every grade-level standard has been taught and examined before this week; the enrichment lessons follow.</td></tr>')
    yn = f'WR Year {YEAR[g]}'
    col = DOMC.get(units[dom_units[0]]['dom'], '#555')
    body = f"""
<h1><span class="gchip" style="background:{col}">{GNAME[g]}</span>Weekly Pacing Guide · 2026–27 <span style="font-size:9pt;color:#8A8077;font-weight:400">CCSS domain sequence · {yn}</span></h1>
<div class="note"><b>ONE DOMAIN AT A TIME.</b> Each unit teaches one Common Core domain in one run and ends with its Awsaj domain exam (red rows), sat on every strand in the same week. Every grade-level standard is taught before the spring MAP window (purple row); the enrichment lessons come after it. <b>THE STRANDS ARE FLEXIBLE · MOVE BETWEEN THEM IN ANY WEEK.</b> Move a child or the class up towards Standard when they are secure and down to Priority or Intervention when they are struggling, as often as they need it. All three strands teach the same domain at the same time, so a change at a domain boundary is always clean; mid-domain a lighter strand may sit a lesson or two behind, so a child moving up picks those lessons up in a support block.</div>
<div class="key">Three strands, one map. <span class="ls pw" style="display:inline">Yellow</span> = power standard. <span class="tg build">CCSS BUILD · TO BE MADE</span> = Awsaj lesson for a standard White Rose does not teach; the lesson still has to be written. <span class="tg copy">COPIED IN · G3</span> = a lesson borrowed from another grade so every exam question is taught first; teach it from that grade's files. <span class="tg enr">ENRICHMENT</span> = after MAP. <span class="tg adapt">ADAPT</span> = UK content to adapt for the US. Pink = support block options (pick one). Daily fluency sits off this calendar.</div>
<table><thead><tr><th style="width:74px">WEEK</th>{''.join(f'<th>{n.upper()} · {d}</th>' for _, n, d in STRANDS)}</tr></thead><tbody>
{''.join(rows)}
</tbody></table>
<div class="foot">Generated from the curriculum site preview (CCSS domain sequence) · lesson files, MAP links and support-lesson files open from every lesson on the site · W39 is the wrap week.</div>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{GNAME[g]} Weekly Pacing Guide 2026-27</title><style>{PG_CSS}</style></head><body>{body}</body></html>'


# ---------------------------------------------------------------- handbook
HB_CSS = CSS_BASE + """
@page{size:A4 portrait;margin:14mm 14mm 16mm}
body{font-size:9.4pt}
.cover h1{font-size:12pt;letter-spacing:.18em;margin:0 0 4px;color:#5A524A}
.cover h2{font-size:22pt;margin:0;line-height:1.1}
.cover .sub{color:#5A524A;margin:6px 0 16px}
table{width:100%;border-collapse:collapse}
.facts td{padding:5px 6px;border-bottom:1px solid #E4DCCF;vertical-align:top}
.facts td:first-child{width:118px;font:700 7.6pt 'DejaVu Sans Mono',monospace;letter-spacing:.06em;color:#5A524A}
.box{border:1px solid #E4DCCF;border-left:4px solid #1565C0;border-radius:6px;padding:8px 11px;margin:10px 0;break-inside:avoid}
.box h3{font:700 8pt 'DejaVu Sans Mono',monospace;letter-spacing:.08em;margin:0 0 5px;color:#1565C0}
.box.green{border-left-color:#2E7D32;background:#F1F8F2}.box.green h3{color:#2E7D32}
.box.red{border-left-color:#B71C1C;background:#FFF8F7}.box.red h3{color:#B71C1C}
.box.orange{border-left-color:#E8720C;background:#FFF7EF}.box.orange h3{color:#B4530A}
.box p{margin:4px 0}
.sec{background:#1565C0;color:#fff;border-radius:5px;padding:6px 11px;font-size:13pt;font-weight:700;margin:0 0 10px}
.pb{break-before:page}
.qt td,.qt th{border-bottom:1px solid #E4DCCF;padding:5px 6px;text-align:left;vertical-align:top}
.qt th{font:700 7.4pt 'DejaVu Sans Mono',monospace;letter-spacing:.06em;color:#5A524A}
.dchip{display:inline-block;color:#fff;border-radius:3px;padding:1px 6px;font-size:8pt;font-weight:700;margin:1px 3px 1px 0}
.bars{margin:6px 0 2px}
.qrow{display:flex;align-items:flex-start;margin:14px 0 4px}
.qlab{width:86px;font-weight:700;font-size:10pt}.qlab small{display:block;font-weight:400;font-size:7.4pt;color:#8A8077}
.strip{flex:1;display:flex;height:38px;border-radius:3px;overflow:hidden}
.wcol{flex:1;display:flex;flex-direction:column;border-right:1px solid rgba(255,255,255,.6)}
.wcol div{flex:1}
.marks{display:flex;margin-left:86px;font:6.4pt 'DejaVu Sans Mono',monospace;color:#5A524A}
.marks div{flex:1;text-align:center;overflow:visible;white-space:nowrap}
.legend span{display:inline-block;margin:2px 8px 2px 0;font-size:7.6pt}
.legend i{display:inline-block;width:12px;height:9px;border-radius:2px;margin-right:4px;vertical-align:-1px}
ul{margin:4px 0 4px 16px;padding:0}li{margin:2px 0}
.small{font-size:8pt;color:#5A524A}
"""


def fluency_text(g):
    if g in ('G4', 'G5'):
        return (f"The Fluency Bee scheme itself runs Year 1 to Year 4 (KG to Grade 3), so there is no {GNAME[g]} book. The daily 10-15 minute "
                "fluency slot still runs every day: use the Fluency Bee sequence at whatever point your students actually need (number bonds, "
                "times-tables, whichever facts are not yet automatic) or the phase fluency diet where the facts are secure.")
    return (f"{GNAME[g]} uses the Fluency Bee Year {YEAR[g]} book: slides, oral practice, a mini worksheet and talk about the pattern, one scheme step a day. "
            "A class below level runs a lower year's Bee. Fluency is kept off the pacing calendar so support blocks stay for grade-level work.")


def handbook(g):
    P, units, order, dom_units, tests, mapwk, per = grade_model(g)
    gd = CUR['grades'][g]
    cm = CMAP['grades'][g]
    std = per['standard']
    cnt = {s: len(per[s]) for s, _, _ in STRANDS}
    kinds = {}
    for x in std: kinds[x['kind']] = kinds.get(x['kind'], 0) + 1
    builds = [x for x in std if x['kind'] == 'build']
    copies = [x for x in std if x['kind'] == 'copy']
    pw = sorted({c for b in dom_units for c in units[b]['pw']})
    # standards taught before MAP (any strand-standard lesson, before the enrichment unit)
    first = {}
    for x in std:
        if x['unit'] == 'E': continue
        for c in x.get('c') or []:
            first.setdefault(c, x['wk'])
    rowsg = [r for d in cm['domains'] for r in d['rows'] if r['c'].startswith(PREFIX[g])]
    before = [r for r in rowsg if r['c'] in first and wn(first[r['c']]) <= wn(mapwk)]
    missing = [r['c'] for r in rowsg if r not in before]
    s1 = [t for t in tests.values() if t['sem'] == 'S1']
    s2 = [t for t in tests.values() if t['sem'] == 'S2']
    supdays = {s: sum((w['t'].get(s) or {}).get('sup', 0) for w in P['weeks']) for s, _, _ in STRANDS}
    examq = {}
    try:
        for r in json.load(open('examcheck_rows.json')):
            if r[0].startswith(GNAME[g] if g != 'K' else 'Kindergarten'): examq[r[1]] = examq.get(r[1], 0) + 1
    except Exception:
        pass
    nq = sum(examq.values())

    def dchip(dom, text=None):
        return f'<span class="dchip" style="background:{DOMC.get(dom, "#8C8C8C")}">{e(text or dom or "E")}</span>'

    # quarters
    QS = ['Q1', 'Q2', 'Q3', 'Q4']
    QL = {'Q1': 'Sep–Oct', 'Q2': 'Nov–Dec', 'Q3': 'Jan–Mar', 'Q4': 'Apr–Jun'}
    qweeks = {q: [w for w in WEEKS if WD[w]['q'] == q] for q in QS}
    qrows = []
    for q in QS:
        ws = qweeks[q]
        items = []
        for b, u in order:
            qa, qz = WD[u['a']]['q'], WD[u['z']]['q']
            if QS.index(qa) <= QS.index(q) <= QS.index(qz):
                lab = (f"D{b} " if u['kind'] == 'domain' else '') + u['n']
                if QS.index(q) > QS.index(qa): lab += f' (continues from {qa})'
                items.append(dchip(u['dom'], lab) + f'<span class="small">{u["a"]}–{u["z"]}</span>')
        ev = [f"{t['n']} exam {t['wk']}" for t in tests.values() if WD[t['wk']]['q'] == q]
        if mapwk and WD[mapwk]['q'] == q: ev.append(f'MAP Growth {mapwk}')
        qrows.append(f'<tr><td><b>{q}</b><br><span class="small">{ws[0]}–{ws[-1]} · {QL[q]}</span></td><td>{"<br>".join(items)}<div class="small" style="margin-top:4px">{" · ".join(e(x) for x in ev)}</div></td></tr>')

    # bars: one column per week, coloured by the domain(s) taught that week on Standard
    def week_doms(wk):
        ds = []
        for x in std:
            if x['wk'] == wk:
                d = units[x['unit']]['dom'] if x['unit'] in units else ''
                if d not in ds: ds.append(d)
        return ds
    bars = []
    examwk = {t['wk']: t['dom'] for t in tests.values()}
    for q in QS:
        ws = [w for w in qweeks[q] if w != 'W39']
        cols = []
        for w in ws:
            ds = week_doms(w) or ['']
            cols.append('<div class="wcol">' + ''.join(f'<div style="background:{DOMC.get(d, "#8C8C8C")}"></div>' for d in ds) + '</div>')
        marks = []
        for w in ws:
            m = ''
            if w in examwk: m = f'▲ {examwk[w]} exam'
            if w == mapwk: m = (m + ' · ' if m else '▲ ') + 'MAP'
            marks.append(f'<div>{e(m)}</div>')
        nls = len([x for x in std if WD[x['wk']]['q'] == q])
        bars.append(f'<div class="qrow"><div class="qlab">{q} · {QL[q]}<small>{ws[0]}–{ws[-1]} · {nls} lessons</small></div><div class="strip">{"".join(cols)}</div></div><div class="marks">{"".join(marks)}</div>')
    legend = ''.join(f'<span><i style="background:{DOMC[units[b]["dom"]]}"></i>{e(units[b]["n"])}</span>' for b in dom_units) + f'<span><i style="background:{DOMC[""]}"></i>Enrichment</span>'

    # domain table
    drows = []
    for b, u in order:
        if u['kind'] == 'domain':
            t = tests.get(u['dom'])
            nl = {s: len([x for x in per[s] if x['unit'] == b]) for s, _, _ in STRANDS}
            bl = [x['n'] for x in std if x['unit'] == b and x['kind'] == 'build']
            cp = [f"{x['n']} ({x['g']})" for x in std if x['unit'] == b and x['kind'] == 'copy']
            notes = ''
            if bl: notes += '<div class="small"><b>To build:</b> ' + e('; '.join(bl)) + '</div>'
            if cp: notes += '<div class="small"><b>Copied in:</b> ' + e('; '.join(cp)) + '</div>'
            drows.append(f'<tr><td>{dchip(u["dom"], "D" + b)}</td><td><b>{e(u["n"])}</b>{notes}</td><td>{u["a"]}–{u["z"]}</td><td>{nl["standard"]} / {nl["priority"]} / {nl["intervention"]}</td><td class="small">{e(", ".join(u["pw"])) or "·"}</td><td>{t["wk"] if t else ""}<div class="small">{"S1" if t and t["sem"] == "S1" else "S2"} report</div></td></tr>')
        else:
            nl = {s: len([x for x in per[s] if x['unit'] == 'E']) for s, _, _ in STRANDS}
            drows.append(f'<tr><td>{dchip("", "E")}</td><td><b>Enrichment lessons</b><div class="small">After MAP: lessons White Rose teaches here that reach above grade level, plus end-of-year work.</div></td><td>{u["a"]}–{u["z"]}</td><td>{nl["standard"]} / {nl["priority"]} / {nl["intervention"]}</td><td>·</td><td>·</td></tr>')

    brow = ''.join(f'<tr><td>{x["wk"]}</td><td><b>{e(x["n"])}</b></td><td class="small">{e(", ".join(x.get("c") or []))}</td><td>{e(units[x["unit"]]["n"] if x["unit"] in units else "")}</td></tr>' for x in builds)
    crow = ''.join(f'<tr><td>{x["wk"]}</td><td><b>{e(x["n"])}</b></td><td>{e(x["g"])}</td><td class="small">{e(", ".join(x.get("c") or []))}</td></tr>' for x in copies)
    trow = ''.join(f'<tr><td>{t["wk"]}</td><td><b>{e(t["n"])}</b></td><td>{"Semester 1" if t["sem"] == "S1" else "Semester 2"}</td><td class="small">{examq.get(t["n"] + " Test", examq.get(t["n"].replace(": ", " - ") + " Test", "")) or ""}</td><td class="small"><a href="https://drive.google.com/file/d/{t["t"][1]}/view">{e(t["t"][0])}</a></td></tr>' for t in sorted(tests.values(), key=lambda t: wn(t['wk'])) if t.get('t'))

    title = f'{GNAME[g]} (Year {YEAR[g]}) Maths Teaching & Pacing Handbook · 2026–27'
    body = f"""
<div class="cover">
<h1>AWSAJ {GNAME[g].upper()} MATHEMATICS</h1>
<h2>White Rose (Year {YEAR[g]}) mapped to the Common Core<br>Teaching &amp; Pacing Handbook</h2>
<div class="sub">2026–2027 · taught one CCSS domain at a time · three pacing strands · for teachers and teaching assistants</div>
<table class="facts">
<tr><td>LESSONS</td><td>{len(std)} on the Standard strand: {kinds.get('core', 0)} White Rose lessons, {kinds.get('copy', 0)} copied in from other grades, {kinds.get('build', 0)} CCSS custom lessons still to be built, {kinds.get('enrich', 0)} enrichment lessons after MAP</td></tr>
<tr><td>CALENDAR</td><td>QFS 2026–2027 · W01 starts {dshort(WD['W01']['start'])} 2026 · 39 Sun–Thu weeks · {TEACH_DAYS} teaching days · Semester 1 is W01–W14</td></tr>
<tr><td>STRUCTURE</td><td>{len(dom_units)} domain units, each taught in one run and closed by its Awsaj domain exam · MAP Growth window {mapwk} · enrichment {units['E']['a']}–{units['E']['z']}</td></tr>
<tr><td>STANDARDS</td><td>Common Core {GNAME[g]} · {len(rowsg)} grade-level standards, {len(before)} taught before MAP · {len(pw)} power standards</td></tr>
<tr><td>STRANDS</td><td>Standard {cnt['standard']} lessons (~4 a week) · Priority {cnt['priority']} (~3) · Intervention {cnt['intervention']} (~2) · the other days are support blocks</td></tr>
<tr><td>ASSESSMENT</td><td>{len(tests)} Awsaj domain exams ({len(s1)} count for Semester 1, {len(s2)} for Semester 2), all in the {GNAME[g]} Math Assessments booklet · White Rose papers are optional practice</td></tr>
<tr><td>COMPANIONS</td><td>Weekly Pacing Guide (landscape, all 39 weeks) · K–5 pacing workbook (spreadsheet) · the curriculum site, where every lesson opens its slides, worksheets, MW4K sheets, teaching guide and support lessons</td></tr>
</table>
<div class="box"><h3>CHOOSING A STRAND · AND CHANGING IT WHENEVER YOUR STUDENTS NEED YOU TO</h3>
<p><b>Standard</b> · the class is broadly within a year of grade level: about 4 new lessons a week, every lesson. <b>Priority</b> · the class carries broad gaps: about 3 a week, the most important lessons for struggling learners, the rest support blocks. <b>Intervention</b> · the small-group class: about 2 a week, the essential lessons with support wrapped around them.</p>
<p><b>The strands are flexible.</b> Move a student, a group or the whole class up towards Standard as soon as the work is secure, and down to Priority or Intervention the moment it stops fitting, in any week and as often as they need it. All three strands teach the same domain at the same time and sit its exam in the same week, so a change at a domain boundary is always clean. Mid-domain a lighter strand may sit a lesson or two behind Standard: a student moving up picks those lessons up in a support block, and moving down never loses a lesson.</p></div>
<div class="box green"><h3>DAILY FLUENCY · 10–15 MINUTES, EVERY DAY</h3><p>{e(fluency_text(g))}</p>
<p><b>Daily is the part that is fixed.</b> Number facts become automatic through a little purposeful practice every day, and the main lesson assumes those facts are already there. Protect the slot even in a short week. <b>Where you start is flexible:</b> find where the facts actually break down and start there.</p></div>
</div>

<div class="pb"></div>
<div class="sec">◎ {GNAME[g]} on one page</div>
<table class="qt"><tr><th style="width:110px">QUARTER</th><th>DOMAINS IN TEACHING ORDER · EXAMS · MAP</th></tr>{''.join(qrows)}</table>
<div class="box red"><h3>THE RULES OF THE YEAR</h3><ul>
<li>Each domain is taught in <b>one run</b> and closed by its <b>Awsaj domain exam</b>, on every strand in the same week.</li>
<li>Every type of question on a domain exam is taught <b>before</b> that exam; where White Rose did not teach a skill here, a lesson is copied in from another grade or a CCSS lesson is listed to be built.</li>
<li>Every grade-level standard is taught and examined <b>before the spring MAP window ({mapwk})</b>; the enrichment lessons come after it.</li>
<li>A domain is not taught again once it is examined: Flashback 4 and the daily fluency slot keep earlier domains alive, and gaps from an exam go into the next support blocks.</li>
<li>Exams sat by W14 count for the Semester 1 report; the rest count for Semester 2.</li></ul></div>
<div class="sec" style="margin-top:14px">❖ The year at a glance</div>
<div class="small">One column is one teaching week, coloured by the domain the Standard strand teaches that week (a split column is a week where one domain ends and the next begins). ▲ marks a domain exam or the MAP window.</div>
<div class="legend" style="margin-top:6px">{legend}</div>
<div class="bars">{''.join(bars)}</div>

<div class="pb"></div>
<div class="sec">1 · The domains · lessons, power standards and exams</div>
<table class="qt"><tr><th style="width:34px">#</th><th>DOMAIN</th><th style="width:66px">WEEKS</th><th style="width:76px">LESSONS S / P / I</th><th style="width:110px">POWER STANDARDS</th><th style="width:62px">EXAM</th></tr>{''.join(drows)}</table>
<div class="box red"><h3>THE DOMAIN EXAMS · {GNAME[g].upper()} MATH ASSESSMENTS BOOKLET</h3>
<table class="qt"><tr><th style="width:44px">WEEK</th><th>EXAM</th><th style="width:76px">REPORT</th><th style="width:60px">QUESTIONS</th><th>BOOKLET</th></tr>{trow}</table>
<p class="small">All of a grade's exams are in one booklet in the shared 2025-2026 Math Assessments folder; each link opens it. Every question was checked against the lessons taught before its exam.</p></div>
{f'<div class="box orange"><h3>CCSS LESSONS STILL TO BE MADE · {len(builds)}</h3><p class="small">White Rose does not teach these standards in this grade, so an Awsaj lesson has to be written. Until it is, use the Twinkl search, the MW4K sheets and the prerequisite lessons on the lesson&#39;s paperclip on the site.</p><table class="qt"><tr><th style="width:44px">WEEK</th><th>LESSON</th><th style="width:120px">CCSS</th><th style="width:150px">DOMAIN</th></tr>{brow}</table></div>' if builds else ''}
{f'<div class="box"><h3>LESSONS COPIED IN FROM ANOTHER GRADE · {len(copies)}</h3><p class="small">Each one closes a gap between what the domain exam asks and what White Rose teaches in this grade. Teach it from the source grade&#39;s files (they open from the lesson on the site).</p><table class="qt"><tr><th style="width:44px">WEEK</th><th>LESSON</th><th style="width:50px">FROM</th><th style="width:140px">CCSS</th></tr>{crow}</table></div>' if copies else ''}

<div class="pb"></div>
<div class="sec">2 · How to read the Weekly Pacing Guide</div>
<p>The guide has one row per school week with the three strands side by side. A coloured band opens each domain, a red row marks its domain exam (with the link to the booklet), and a purple row marks the spring MAP window. Under each week, the pink row lists the support block options: real lower-grade lessons (Pre-K up to the grade below) that are the prerequisites for that week's lessons, nearest grade last. Pick one each time a strand has a support block.</p>
<p><b>Tags.</b> Yellow highlight = power standard. Orange CCSS BUILD = lesson still to be made. Blue COPIED IN = lesson from another grade. Lilac ENRICHMENT = after MAP. ADAPT = UK content to adapt for the US (money, units).</p>
<div class="box"><h3>ON A SUPPORT DAY, YOU CAN</h3><ul>
<li>Split a hard lesson across two days: concept first, then method.</li>
<li>Re-teach or review content that is still shaky, including gaps from the last domain exam.</li>
<li>Run the pre-teach pack (teacher or TA) for an upcoming lesson, or teach from it if the class is really struggling.</li>
<li>Teach one of the lower-grade prerequisite lessons listed for that week.</li></ul></div>
<div class="box green"><h3>PRE-TEACH PACKS · OPTIONAL, AND ONE OF THE MOST POWERFUL TOOLS YOU HAVE</h3>
<p>A pre-teach pack is a 15–20 minute session on the prerequisites a lesson assumes. Use it as extra prerequisite support, so a group walks into the lesson already holding the facts and vocabulary it depends on, or as a targeted intervention for the students you already know will struggle. It can fill any support block. Front-loading the prerequisite is far more effective than re-teaching after the lesson has gone wrong.</p></div>
<div class="box"><h3>THE TEACHING GUIDES · ONE PER LESSON</h3>
<p>Every White Rose lesson has a two-sided White Rose Teaching Guide for teachers and TAs of ELL and Tier 2 students: the front is teach the lesson (the lesson in one sentence, the prerequisites, the essential teaching points, a lesson map), the back is respond to thinking (misconceptions, what to say, vocabulary and sentence stems). Read it before you teach and keep it open while you teach. It opens from every lesson on the site.</p></div>
<div class="box"><h3>FLASHBACK 4 AND THE DOMAIN EXAM ROUTINE</h3>
<p>Review slots open with Flashback 4 (last lesson / last week / last unit / last term). Because a domain is not taught again after its exam, Flashback 4 is how earlier domains stay alive: pick the deck for the White Rose block a lesson came from (the lesson's paperclip names it). After each domain exam, mark it live where you can and feed the weakest skills into the next support blocks. White Rose materials show money as £/p: adapt to dollars and cents; the maths is unchanged.</p></div>

<div class="pb"></div>
<div class="sec">3 · Verification summary</div>
<table class="qt"><tr><th>STRAND</th><th>LESSONS</th><th>DOMAIN EXAMS</th><th>SUPPORT BLOCKS</th><th>CCSS BUILDS</th></tr>
{''.join(f'<tr><td><b>{n}</b></td><td>{cnt[s]}</td><td>{len(tests)}</td><td>{supdays[s]}</td><td>{len([x for x in per[s] if x["kind"] == "build"])}</td></tr>' for s, n, _ in STRANDS)}</table>
<ul style="margin-top:10px">
<li>Each domain is one unbroken run on every strand, closed by its exam; no domain is taught after its exam.</li>
<li>Grade-level standards taught before MAP ({mapwk}): {len(before)} of {len(rowsg)}{(' · not on the Standard strand before MAP: ' + ', '.join(missing)) if missing else ''}.</li>
<li>Domain exams: {', '.join(f"{t['dom']} {t['wk']}" for t in sorted(tests.values(), key=lambda t: wn(t['wk'])))}{f' · {nq} questions checked' if nq else ''}; every question's skill is taught before its exam.</li>
<li>Semester split: {len(s1)} exams by W14 (Semester 1) · {len(s2)} after (Semester 2).</li>
<li>Lessons are spread over the real QFS calendar by teaching days ({TEACH_DAYS} days; short weeks carry fewer lessons).</li>
<li>Every support block names real lower-grade lessons with files on the site.</li></ul>
"""
    foot = title
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{e(title)}</title><style>{HB_CSS}</style></head><body>{body}</body></html>', foot


# ---------------------------------------------------------------- year at a glance (one page)
YG_CSS = CSS_BASE + """
@page{size:A4 landscape;margin:7mm 8mm}
html{font-size:10px}
body{font-size:1rem;line-height:1.28}
.top{display:flex;align-items:baseline;gap:1.2rem;border-bottom:2px solid #1C1916;padding-bottom:.35rem}
.top h1{font-size:2.1rem;margin:0}.top .gchip{font-size:1.2rem;color:#fff;border-radius:4px;padding:.15rem .7rem;font-weight:700}
.top .sub{color:#5A524A;font-size:1.05rem}
.strip{display:flex;gap:.4rem;flex-wrap:wrap;margin:.45rem 0 .35rem}
.dm{border-radius:4px;padding:.25rem .55rem;color:#fff;font-size:1rem;line-height:1.2}
.dm b{font-size:1.05rem}.dm span{display:block;font:.85rem 'DejaVu Sans Mono',monospace;opacity:.95}
.cols{display:grid;grid-template-columns:repeat(4,1fr);gap:.55rem}
.q{border:1px solid #E4DCCF;border-radius:5px;overflow:hidden}
.qh{background:#1C1916;color:#fff;font:700 .95rem 'DejaVu Sans Mono',monospace;letter-spacing:.05em;padding:.25rem .5rem;display:flex;justify-content:space-between}
.wk{padding:.22rem .45rem;border-bottom:1px solid #EFE8DC;break-inside:avoid}
.wk .h{font:700 .82rem 'DejaVu Sans Mono',monospace;color:#5A524A;margin-bottom:.05rem}
.wk .h i{font-style:normal;font-weight:400;color:#8A8077}
.l{display:block;font-size:.98rem;padding-left:.55rem;border-left:3px solid #ccc;margin:.06rem 0}
.l.pw{background:#FFF1B8}.l.bld{background:#FFE3C4}
.t{font:700 .72rem 'DejaVu Sans Mono',monospace;border-radius:2px;padding:0 .2rem;margin-left:.25rem;white-space:nowrap}
.t.b{background:#E8720C;color:#fff}.t.c{background:#DDE8FA;color:#1D4E9E}.t.e{background:#EEE3F7;color:#6A3A8C}
.x{display:block;font:700 .82rem 'DejaVu Sans Mono',monospace;color:#fff;background:#B71C1C;border-radius:2px;padding:.08rem .35rem;margin:.1rem 0}
.x.map{background:#5B2A86}
.foot{display:flex;gap:1.2rem;justify-content:space-between;margin-top:.4rem;font-size:.9rem;color:#5A524A}
.foot b{color:#1C1916}
"""


def glance(g):
    P, units, order, dom_units, tests, mapwk, per = grade_model(g)
    byw = {}
    for x in per['standard']: byw.setdefault(x['wk'], []).append(x)
    QS = ['Q1', 'Q2', 'Q3', 'Q4']
    QL = {'Q1': 'SEP–OCT', 'Q2': 'NOV–DEC', 'Q3': 'JAN–MAR', 'Q4': 'APR–JUN'}
    strip = []
    for b, u in order:
        t = tests.get(u['dom']) if u['kind'] == 'domain' else None
        lab = (f'D{b} · ' if u['kind'] == 'domain' else '') + u['n']
        sub = f"{u['a']}–{u['z']}" + (f" · exam {t['wk']}" if t else ' · after MAP')
        strip.append(f'<div class="dm" style="background:{DOMC.get(u["dom"], "#8C8C8C")}"><b>{e(lab)}</b><span>{e(sub)}</span></div>')
    strip.append(f'<div class="dm" style="background:#5B2A86"><b>MAP Growth (spring)</b><span>{mapwk}</span></div>')
    cols = []
    for q in QS:
        ws = [w for w in P['weeks'] if WD[w['wk']]['q'] == q and w['wk'] != 'W39']
        items = []
        for w in ws:
            wk = w['wk']; it = iter(byw.get(wk, []))
            body = []
            for y in (w['t'].get('standard') or {}).get('st', []):
                k = lesson_kind(y)
                if k == 'exam':
                    body.append(f'<span class="x">■ {e(DOMSHORT.get(y.get("d"), ""))} EXAM</span>'); continue
                if k == 'map':
                    body.append('<span class="x map">■ MAP GROWTH WINDOW</span>'); continue
                x = next(it)
                col = DOMC.get(units[x['unit']]['dom'] if x['unit'] in units else '', '#8C8C8C')
                tg = '<span class="t b">BUILD</span>' if k == 'build' else f'<span class="t c">{e(x["g"])}</span>' if k == 'copy' else '<span class="t e">ENR</span>' if k == 'enrich' else ''
                cls = 'l' + (' pw' if x.get('p') else '') + (' bld' if k == 'build' else '')
                body.append(f'<span class="{cls}" style="border-left-color:{col}">{e(x["n"])}{tg}</span>')
            if not body: body.append('<span class="l" style="color:#8A8077">review and support</span>')
            items.append(f'<div class="wk"><div class="h">{wk} <i>{wdates(wk)}</i></div>{"".join(body)}</div>')
        cols.append(f'<div class="q"><div class="qh"><span>{q} · {QL[q]}</span><span>{ws[0]["wk"]}–{ws[-1]["wk"]}</span></div>{"".join(items)}</div>')
    pw = sorted({c for b in dom_units for c in units[b]['pw']})
    col = DOMC.get(units[dom_units[0]]['dom'], '#555')
    body = f"""<div class="top"><span class="gchip" style="background:{col}">{GNAME[g]}</span><h1>The year at a glance · 2026–27</h1>
<span class="sub">What we teach, week by week · one Common Core domain at a time · Standard strand (Priority and Intervention teach a subset in the same weeks)</span></div>
<div class="strip">{''.join(strip)}</div>
<div class="cols">{''.join(cols)}</div>
<div class="foot"><span><b>Key</b> · coloured edge = domain · <span style="background:#FFF1B8;padding:0 .2rem">yellow</span> = power standard · <span class="t b">BUILD</span> CCSS lesson still to be made · <span class="t c">G3</span> lesson copied in from that grade · <span class="t e">ENR</span> enrichment after MAP · red = domain exam (exams by W14 count for Semester 1)</span>
<span><b>Power standards</b> · {e(', '.join(pw))}</span></div>"""
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{GNAME[g]} Year at a Glance 2026-27</title><style>{YG_CSS}</style></head><body>{body}</body></html>'


FILES = {}
for g in GRADES:
    base = GNAME[g].replace(' ', '-')
    open(f'{OUT}/{base}-Weekly-Pacing-Guide-2026-27.html', 'w').write(pacing_guide(g))
    hb, foot = handbook(g)
    open(f'{OUT}/{base}-Teaching-and-Pacing-Handbook-2026-27.html', 'w').write(hb)
    open(f'{OUT}/{base}-Year-at-a-Glance-2026-27.html', 'w').write(glance(g))
    FILES[g] = {'yg': f'{base}-Year-at-a-Glance-2026-27', 'pg': f'{base}-Weekly-Pacing-Guide-2026-27', 'hb': f'{base}-Teaching-and-Pacing-Handbook-2026-27', 'hbfoot': foot,
                'pgfoot': f'{GNAME[g]} Weekly Pacing Guide · 2026–27 · CCSS domain sequence'}
json.dump(FILES, open(f'{OUT}/files.json', 'w'), indent=1)
print('ok', list(FILES))
