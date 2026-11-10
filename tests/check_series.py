"""Gate: series y personajes (data/series.js + la vista de src.html).  Run from the project root:  python tests/check_series.py

  1. datos: src/series/series.json cumple el contrato (tools/series.py) y data/series.js lo refleja
  2. cobertura: cada duelista de la ruleta cae en una sola serie y tiene un slug único dentro de ella (es su URL)
  3. el Lore enlazado existe, y el protagonista de cada serie tiene duelista y mazos
  4. cableado: pestaña, MODES, rutas, clics, títulos, dist/
  5. rutas en node: ?mode=series&name=gx&char=jaden-yuki, saneo, y los ids av y vr de la ruleta (antes se perdían)
"""
import glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'tools')
import series as S

fails = []


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


slug = lambda n: re.sub(r'[^a-z0-9]+', '-', n.lower()).strip('-')

# 1. datos
items = json.load(open('src/series/series.json', encoding='utf-8'))
bad = S.check(items)
ok(not bad, 'series.json cumple el contrato %s' % bad[:3])
raw = open('data/series.js', encoding='utf-8').read()
D = json.loads(re.search(r'__load\("series",(.*)\);\s*$', raw, re.S).group(1))
ok([x['id'] for x in D['s']] == S.IDS and len(D['s']) == 6, 'data/series.js trae las 6 series en orden')
ok(all(x['m']['es'] != x['m']['en'] and x['b']['es'] != x['b']['en'] for x in D['s']), 'cada texto está en español e inglés y son distintos')
ok([x['b'] for x in D['s']] == [x['blurb'] for x in items], 'data/series.js está al día con src/series/series.json')

# 2. cobertura contra la ruleta
r = open('data/roulette.js', encoding='utf-8').read()
decks = json.loads(r[r.index('{'):r.rindex('}') + 1])['decks']
by = {}
for d in decks:
    by.setdefault(d['series'], {}).setdefault(d['character'], []).append(d)
ok(set(by) == set(S.IDS), 'la ruleta tiene duelistas en las 6 series (%s)' % sorted(by))
for sid, cs in by.items():
    slugs = [slug(n) for n in cs]
    ok(len(set(slugs)) == len(slugs), '%s: no hay dos duelistas con el mismo slug (la URL chocaría)' % sid)
    ok(all(re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', x) for x in slugs), '%s: todos los slugs son válidos' % sid)
total = sum(len(v) for v in by.values())
ok(total >= 80, 'duelistas en total: %d' % total)

# 3. protagonista y Lore
for x in D['s']:
    ok(x['p'] in by.get(x['id'], {}), '%s: el protagonista %r tiene mazos en la ruleta' % (x['id'], x['p']))
lore_slugs = {json.load(open(f, encoding='utf-8'))['slug'] for f in glob.glob('src/lore/*.json')}
ok(bool(D['l']) and all(sl in lore_slugs for sl in D['l'].values()), 'todo el Lore enlazado existe: %s' % D['l'])
ok(all(any(n in cs for cs in by.values()) for n in D['l']), 'el Lore enlazado es de un duelista de la ruleta')

# 4. cableado
src = open('src.html', encoding='utf-8').read()
for pat, why in [
    (r'id="tab-ser" data-mode="ser"', 'pestaña Series'), (r"ser:\['Series',viewSeries\]", 'MODES.ser'), (r'function viewSeries\(', 'vista'),
    (r"series:\['ser',''\]", 'ruta ?mode=series'), (r"ser:'series'", 'ROUTE_OLD'), (r'data-serpick', 'enlaces reales a series y duelistas'),
    (r'a\[data-serpick\],a\[data-goqs\]', 'clic de los enlaces'), (r'd\.serpick!==undefined', 'handler de series'), (r'serTitle\(\)', 'título de la pestaña'),
    (r"loadData\('series'\)", 'carga lazy de data/series.js'), (r"mode==='rou'\|\|mode==='ser'", 'redibuja al llegar la ruleta'),
    (r"'zx','av','vr'\]\.includes\(sr\)", 'la ruleta acepta av y vr en la URL'), (r'body\.glos,body\.ser(,body\.fnd)?\{--accent', 'color de la pestaña'),
]:
    ok(re.search(pat, src), 'src.html: ' + why)
ok('data/series.js' in open('files.json', encoding='utf-8').read(), 'files.json lista data/series.js')
rf = open('tools/refresh.py', encoding='utf-8').read()
ok("'tools/series.py'" in rf and "'tests/check_series.py'" in rf, 'refresh.py corre el generador y este gate')
ok(os.path.exists('dist/data/series.js') or not os.path.isdir('dist'), 'dist/ tiene data/series.js')

# 5. rutas en node
page = open('index.html', encoding='utf-8').read()
core = re.search(r'const ROUTE_MODES=.*?function routeBuild\(st\)\{.*?\n\}\n', page, re.S)
ok(bool(core), 'index.html: helpers de ruta')
if core:
    harness = r"""
const slug = s => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-');
%s
const t = [];
let r = routeParse('?mode=series&name=gx&char=Jaden-Yuki');  t.push(r.mode==='ser' && r.name==='series' && r.ser==='gx' && r.char==='jaden-yuki');
r = routeParse('?mode=series');  t.push(r.mode==='ser' && r.ser==='' && r.char==='');
r = routeParse('?mode=series&name=zz&char=x');  t.push(r.ser==='' && r.char==='');
r = routeParse('?mode=series&name=gx&char=%%3Cb%%3E');  t.push(/^[a-z0-9-]*$/.test(r.char));
r = routeParse('?mode=tcg&name=gx&char=x');  t.push(r.ser==='' && r.char==='');
t.push(routeBuild({mode:'ser',tcgf:'',view:'meta',deck:'',ser:'5d',char:'yusei-fudo'})==='?mode=series&name=5d&char=yusei-fudo');
t.push(routeBuild({mode:'ser',tcgf:'',view:'meta',deck:'',ser:'vr',char:''})==='?mode=series&name=vr');
t.push(routeBuild({mode:'ser',tcgf:'',view:'meta',deck:'',ser:'',char:'x'})==='?mode=series');
t.push(routeName('ser','')==='series');
r = routeParse('?mode=roulette&series=av');  t.push(r.series==='av');
r = routeParse('?mode=roulette&series=vr');  t.push(r.series==='vr');
r = routeParse('?mode=roulette&series=zz');  t.push(r.series==='');
console.log(JSON.stringify(t));
""" % core.group(0)
    p = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(p.stdout.strip())
    except Exception:
        res = []
    labels = ['URL de duelista', 'URL de índice', 'serie inválida se descarta', 'char saneado', 'name y char solo valen en Series', 'URL de duelista al escribir', 'URL de serie', 'sin serie no hay char', 'routeName', 'ruleta acepta av', 'ruleta acepta vr', 'ruleta descarta ids raros']
    ok(len(res) == len(labels), 'el arnés de rutas corrió (%s)' % p.stderr.strip()[:140])
    for g, l in zip(res, labels):
        ok(g, 'ruta: ' + l)

# 6. render real de viewSeries en node (ES y EN) con los datos reales
def grab(pat, flags=re.S):
    m = re.search(pat, page, flags)
    return m.group(0) if m else ''


pieces = [grab(r"const EN = [^\n]*\n"), grab(r"function __t\(a\)\{.*?\n\}\n"), grab(r"const esc = [^\n]*\n"),grab(r"const ROU_MAX=[^\n]*\n"), grab(r"const ROU_SER=[^\n]*\n"), grab(r"function rouChars\(.*?\n\}\n"),
          grab(r"function archA\([^\n]*\n"), grab(r"const FMT_RETRO=[^\n]*\n"),
          grab(r"const SER=\{.*?(?=function linkCards)"), core.group(0) if core else '']
ok(all(pieces), 'index.html: piezas de la vista de series encontradas')
if all(pieces):
    arch = open('data/arch.js', encoding='utf-8').read()
    js = r"""
const slug = x => x.toLowerCase().replace(/[^a-z0-9]+/g,'-');
let LANG='%(lang)s', mode='ser';
const how=(h,t)=>'<how>'+t+'</how>', pageHead=(t,l,h='')=>'<h2>'+t+'</h2><p class="lede">'+l+'</p>'+h;
const rouFace=(c,cls)=>'<face '+cls+'>', loreHref=k=>'?lore='+k, archHref=k=>'?arch='+k, loadData=()=>new Promise(()=>{}), render=()=>{}, archLoad=()=>{}, rouLoad=()=>{};
const ARCH={data:null,by:null}; const ROU={data:null,err:false};
%(pieces)s
const J=%(arch)s; ARCH.data=J; ARCH.by={}; J.n.forEach((a,i)=>{ ARCH.by[archSlug(a)]=i; });
const R=%(rou)s; ROU.data=R;
const S=%(ser)s; SER.data=S;
const out={};
function at(sel,ch){ SER.sel=sel; SER.char=ch; return viewSeries(); }
out.idx=at('','');
out.gx=at('gx','');
out.char=at('gx','jaden-yuki');
out.vr=at('vr','playmaker');
out.bad=at('gx','nadie');
out.badtitle=(SER.sel='gx',SER.char='nadie',serTitle());
out.title=(SER.sel='gx',SER.char='jaden-yuki',serTitle());
out.noshow=at('zz','');
out.all={};
for (const c of rouChars(R.decks,'all')) out.all[c.series+'/'+archSlug(c.name)]=at(c.series,archSlug(c.name));
console.log(JSON.stringify(out));
"""
    for lang in ('es', 'en'):
        def lit(path):
            t = open(path, encoding='utf-8').read()
            return t[t.index('{'):t.rindex('}') + 1]
        src_js = js % dict(lang=lang, pieces='\n'.join(pieces), arch=lit('data/arch.js'), rou=lit('data/roulette.js'), ser=lit('data/series.js'))
        import tempfile
        with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tf:
            tf.write(src_js)
        p = subprocess.run(['node', tf.name], capture_output=True, text=True, encoding='utf-8')
        os.unlink(tf.name)
        try:
            o = json.loads(p.stdout.strip().splitlines()[-1])
        except Exception:
            o = None
        ok(o is not None, 'render %s: el arnés corrió %s' % (lang, p.stderr.strip()[:200]))
        if not o:
            continue
        sv = {x['id']: x for x in D['s']}
        ok(o['idx'].count('class="sercard"') == 6, 'render %s: el índice tiene 6 tarjetas' % lang)
        ok(all(sv[i]['b'][lang] in o['gx'] for i in ['gx']) and sv['gx']['m'][lang] in o['gx'], 'render %s: la serie GX muestra su texto en el idioma (%s)' % (lang, lang))
        ok(lang == 'es' or not re.search(r'Girar la ruleta|Duelistas ·|Estreno|Protagonista|Mecánica', o['gx'] + o['char'] + o['idx']), 'render %s: el inglés no deja títulos en español' % lang)
        ok(lang == 'es' or not re.search(r'Girar la ruleta|Duelistas ·|Estreno|Protagonista|Mecánica|Mazos<|Arquetipos de sus', o['gx'] + o['char'] + o['idx'] + o['bad']), 'render %s: el inglés no deja textos en español' % lang)
        ok('Jaden Yuki' in o['gx'] and 'data-serchar="jaden-yuki"' in o['gx'] and '2004' in o['gx'], 'render %s: GX lista a Jaden y su año' % lang)
        ok('data-gobfmt="goat"' in o['gx'], 'render %s: GX enlaza el formato Goat' % lang)
        ok('Elemental HERO' in o['char'] and 'data-arch="elemental-hero"' in o['char'], 'render %s: Jaden enlaza al hub Elemental HERO' % lang)
        ok(('protagonista' if lang == 'es' else 'protagonist') in o['char'] and 'data-goqs="?mode=roulette' in o['char'] and ('Carta clave' if lang == 'es' else 'Key card') in o['char'], 'render %s: Jaden es protagonista, con mazos de la ruleta y carta clave' % lang)
        ok('data-lorego=' in o['char'], 'render %s: Jaden enlaza su Lore' % lang)
        ok('Playmaker' in o['vr'] and 'data-card=' in o['vr'], 'render %s: Playmaker tiene página con cartas' % lang)
        ok(('No encontré a ese duelista' if lang == 'es' else 'I could not find that duelist') in o['bad'] and 'data-serpick="gx"' in o['bad'] and '<how>' not in o['bad'], 'render %s: duelista inexistente da un aviso con salida y sin caja Fuentes vacía' % lang)
        allp = o['all']
        ok(len(allp) == total, 'render %s: se dibujaron las %d páginas de duelista' % (lang, total))
        ok(all(len(h) > 400 and not re.search(r'undefined|NaN|\[object', h) for h in allp.values()), 'render %s: ninguna página trae undefined, NaN ni [object' % lang)
        ok(all(h.count('class="serdecks"') == 1 and '<li>' in h for h in allp.values()), 'render %s: toda página de duelista lista sus mazos' % lang)
        ok(len({h for h in allp.values()}) == len(allp), 'render %s: no hay dos páginas de duelista idénticas' % lang)
        if lang == 'en':
            leak = [k for k, h in allp.items() if re.search(r'Temático|mazo temático|Temporada|Carta clave|Arquetipos de|Mazos<|También aparece|En el Lore', h)]
            ok(not leak, 'render en: ninguna página de duelista deja textos en español %s' % leak[:3])
        thm = [k for k, h in allp.items() if re.search(r'Tem[aá]tico ·|(Themed|themed deck)[^<]*(Themed|themed deck)', h)]
        ok(not thm, 'render %s: los mazos temáticos no repiten la etiqueta %s' % (lang, thm[:3]))
        hubs = lambda k: set(re.findall(r'data-arch="([^"]+)"', allp[k]))
        want = {'gx/jaden-yuki': {'elemental-hero'}, 'gx/chazz-princeton': {'ojama'}, '5d/yusei-fudo': {'junk'}, 'dm/alister': {'toon'}, '5d/sherry-leblanc': {'noble-knight'}}
        for k, w in want.items():
            ok(w <= hubs(k), 'render %s: %s enlaza a %s (tiene %s)' % (lang, k, sorted(w), sorted(hubs(k))))
        nope = {'dm/yami-bakura': {'underworld'}, 'dm/joey-wheeler': {'virtual-world'}, 'dm/seto-kaiba': {'virtual-world'}, '5d/yusei-fudo': {'warrior'}}
        for k, w in nope.items():
            ok(not (w & hubs(k)), 'render %s: %s no enlaza al hub equivocado %s' % (lang, k, sorted(w)))
        AR = json.loads(lit('data/arch.js'))
        def want_hubs(sid, nm):
            cnt = {}
            for d in by[sid][nm]:
                per = {}
                for r_ in d['main'] + d['extra']:
                    i = AR['c'].get(r_[0])
                    if i is not None:
                        per[i] = per.get(i, 0) + 1
                for i, n in per.items():
                    if n >= 3:
                        cnt[i] = cnt.get(i, 0) + 1
            order = sorted(cnt, key=lambda i: (-cnt[i], AR['n'][i]))
            return [slug(AR['n'][i]) for i in order][:6]
        bad_h = []
        for sid, cs_ in by.items():
            for nm in cs_:
                got = re.findall(r'data-arch="([^"]+)"', allp[sid + '/' + slug(nm)])
                if got != want_hubs(sid, nm):
                    bad_h.append((nm, got, want_hubs(sid, nm)))
        ok(not bad_h, 'render %s: los hubs de los %d duelistas coinciden, en orden, con la regla (3+ cartas, main y extra, máx. 6) %s' % (lang, total, bad_h[:2]))
        ok(any(len(want_hubs(s_, n_)) == 6 for s_, c_ in by.items() for n_ in c_), 'el tope de 6 hubs se ejerce con datos reales')
        seasons = [k for k, h in allp.items() if re.search(r'Season \d', ''.join(d['arc'] for d in by[k.split('/')[0]][next(n for n in by[k.split('/')[0]] if slug(n) == k.split('/')[1])]))]
        ok(len(seasons) >= 5, 'hay duelistas con arcos "Season N" para vigilar la traducción (%d)' % len(seasons))
        ok(all(('Temporada' in allp[k] and 'Season' not in allp[k]) if lang == 'es' else ('Season' in allp[k] and 'Temporada' not in allp[k]) for k in seasons), 'render %s: "Season N" sale como %s' % (lang, 'Temporada N' if lang == 'es' else 'Season N'))
        ok(all(len(hubs(k)) <= 6 for k in allp),'render %s: como mucho 6 hubs por duelista' % lang)
        ok(o['badtitle'] == 'GX' and o['title'] == 'Jaden Yuki', 'render %s: título de pestaña (duelista, o la serie si no existe)' % lang)
        ok('data-gobfmt' not in o['noshow'] and o['noshow'].count('class="sercard"') == 6, 'render %s: serie desconocida cae al índice' % lang)
    ok(all(re.fullmatch(r'[A-Za-z0-9 .\'-]+', n) for cs in by.values() for n in cs), 'los nombres de duelistas son ASCII (archSlug no quita acentos)')
    zx = next(x for x in items if x['id'] == 'zx')
    ok(zx['era'] == '', 'ZEXAL no enlaza HAT (HAT es de 2014, ya de ARC-V)')
    ok(all(not re.search(r'serie original|original series', x['blurb']['es'] + x['blurb']['en'], re.I) for x in items), 'ningún texto llama "original" a una serie (hubo un anime anterior, de 1998)')

if fails:
    print('\nFALLA check_series: %d' % len(fails))
    sys.exit(1)
print('\nok check_series')
