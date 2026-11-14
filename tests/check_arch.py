"""Gate test de los arquetipos (hub por arquetipo, enlaces entre cartas, Lore, engines y mazos).  Sin red.  Run from the project root:  python tests/check_arch.py

Outcome: cada carta puede decir de qué arquetipo es y en qué historia del Lore aparece, y cada arquetipo tiene su página.
  * tools/arch.py: el archivo data/arch.js coincide con lo que genera hoy; las cartas existen; ningún arquetipo repite slug; cada entrada de Lore
    mapeada apunta a arquetipos que existen; los índices de cartas del Lore coinciden con las entradas
  * La página: pestaña, modo, ruta (?mode=archetype&name=...), vista, enlaces en la ficha de la carta, el Lore, los engines y los mazos, todo en diferido
  * data/arch.js está en files.json y en dist/ (si dist/ existe)
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import arch

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


d = arch.build()
names = {c['name'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
slug = lambda s: re.sub(r'^-+|-+$', '', re.sub(r'[^a-z0-9]+', '-', s.lower()))

txt = open('data/arch.js', encoding='utf-8').read() if os.path.isfile('data/arch.js') else ''
check(txt == '__load("arch",' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ');', 'data/arch.js is what tools/arch.py makes today (run it after changing the Lore or the archetypes)')
check(len(d['n']) > 300 and len(d['c']) > 5000, 'the archetype list is not empty (%d archetypes, %d cards)' % (len(d['n']), len(d['c'])))
check(all(c in names for c in d['c']) and all(c in names for c in d['l']), 'every card in the index exists in the database')
check(all(0 <= i < len(d['n']) for i in d['c'].values()), 'every card points to an archetype that exists')
slugs = [slug(a) for a in d['n']]
check(len(set(slugs)) == len(slugs) and all(slugs), 'no two archetypes share a URL slug')
missing = [(s, a) for s, aa in arch.LORE_ARCH.items() for a in aa if a not in d['n']]
check(not missing, 'every archetype named for a Lore entry exists (%s)' % missing[:3])
lore = {os.path.splitext(f)[0] for f in os.listdir('src/lore') if f.endswith('.json')}
check(set(arch.LORE_ARCH) <= lore, 'the Lore entries named in LORE_ARCH exist')
check(set(d['ln']) == lore, 'every Lore entry has its name in the index (%d)' % len(lore))
check(all(s in d['ln'] for ss in d['l'].values() for s in ss), 'every card-to-Lore link points to an entry that exists')
nm = {}
for f in lore:
    e = json.load(open('src/lore/%s.json' % f, encoding='utf-8'))
    nm[f] = e['name']
same = [f for f, n in nm.items() if n in d['n'] and f not in d['la']]
check(not same, 'a Lore entry named like an archetype links to its hub (%s)' % same[:3])
junk = [a for a in d['n'] if a in arch.DENY]
check(not junk, 'fragment archetypes (-Eyes Dragon, Gem-...) are not listed')
check(all(c not in d['c'] for c in ('Snake-Eyes Doomed Dragon',)) is False and d['n'][d['c']['Snake-Eyes Doomed Dragon']] == 'Snake-Eye', 'Snake-Eyes dragons are in the Snake-Eye hub')
check(all(set(d['la']) <= lore for _ in [0]), 'the Lore-to-archetype table only has entries that exist')

src = open('src.html', encoding='utf-8').read()
check('id="tab-arq" data-mode="arq"' in src and "arq:['Arquetipos',viewArch]" in src and "archetype:['arq','']" in src, 'the Archetypes tab, its mode and its route are wired')
check('items.sort((x,y)=>sc(x)-sc(y)||(y.n-x.n)||x.a.localeCompare(y.a));' in src and '(y.l-x.l)' not in src, 'the archetype index sorts by number of cards, most to fewest (the lore flag no longer jumps the queue); search relevance still wins while typing')
check('function archHub(' in src and 'function archIndexView(' in src and "loadData('arch')" in src, 'the hub and the index views exist and load their data lazily')
check('id="dx-links"' in src and 'cardLinks(n)' in src, 'the card page shows its archetype and Lore links')
check("data-lorego" in src and 'function lorePend(' in src and "d.lorego" in src, 'a Lore link opens that entry')
check('function linkCards(' in src and 'linkCards(t(b.p),allCards)' in src, 'card names in a Lore paragraph link to the card')
check('archA(a[0])' in src and 'function archFor(' in src and 'Arquetipos de la misma historia' in src and 'data-arretry' in src, 'the engine page links its archetypes to the hub')
check('function archDecorate(' in src and "d.ardeck" in src, 'decks link to their archetype and the hub links back to decks')
check("out.arch=archSlug(q.get('name')||'')" in src and "q.set('name',st.arch)" in src, 'the route carries the archetype name')

check('<a class="lnk" href="${archHref(k)}" data-arch=' in src and '<a class="lnk" href="${loreHref(s)}" data-lorego=' in src and "a[data-arch],a[data-lorego],a[data-ardeck],a[data-serpick],a[data-goqs],a[data-card]" in src and '<a class="cc" href="${archHref(' in src and '<a class="cc" href="${routeBuild({mode:r.f' in src, 'hub, index, deck and card links are real anchors (open in new tab, copy link)')
check('function deckIn(' in src and 'const r=deckIn(st,i)' in src and 'deckIn(st,i); if(r) out.push' in src and '(b.exact-a.exact)' in src, 'one rule (deckIn) decides which decks a hub lists and which hubs a deck links to; a deck named after a longer archetype is not listed (fairy vs Fairy Tail)')
check('scroll-margin-top:120px' in src and 'const sc=x=>' in src, 'the hub heading clears the sticky dock and exact search matches come first')
check('data-goeng' in src and 'd.goeng' in src and 'Arquetipos: ${hub.map(a=>archA(a[0]))' in src, 'hub engines open the engine page and engine rows link to the hubs')
check("Object.keys(D.la).filter(s=>D.la[s].includes(i))" in src, 'a card page links the Lore of its archetype even when the card is not quoted in it')
check("const b=MODES[mode]?MODES[mode][0]:''; return b&&mode==='tcg'&&RETRO_ES[TCGF]?b+' '+RETRO_ES[TCGF].n:b&&mode==='dl'&&DL_FMT[dlFormat]?b+' '+DL_FMT[dlFormat]:b;" in src and "tb.textContent.trim()" not in src and 'function toApp' in src.replace('const toApp=','function toApp') , 'every tab sets document.title and hub navigation scrolls to the content')

check('const archKey=' in src and 'K.has(archKey(x[0]))' in src, 'deck cards match archetype cards ignoring symbols (Maliss <P> Chessy Cat)')
check('ARCH.deep=!!r.arch' in src and 'setTimeout(toApp,150)' in src, 'a hub deep link and a click from a card page scroll to the hub content')
check('metaKeys.has(archKey(c))' in src, 'the in-meta count also matches names with symbols')

check('function archFor(sl,fm)' in src and 'archFor(sl,mode)' in src and "insertAdjacentHTML('afterbegin',`<p class=\"archlinks\">" in src and 'details.deck,.einsp,.engcard,#app .detail{scroll-margin-top:140px}' in src, 'a deck panel looks up its own format, shows its hub link first, and hub deck/engine jumps clear the dock')

check("out.eng=archSlug(q.get('engine')||'')" in src and "q.set('engine',st.eng)" in src and 'ENG.want' in src and 'a[data-goeng]' in src, 'an engine has its own URL (?mode=engines&engine=...) and the hub links to it with a real anchor')
check('Otros mazos:' in src and 'function archLev(' in src and 'x.n>1||x.l' in src and 'tr(a)-tr(b)' in src, 'engine rows separate archetypes from other decks; hubs show tier; search tolerates a typo; one-card noise is hidden')

files = [f['path'] for f in json.load(open('files.json', encoding='utf-8'))]
check('data/arch.js' in files, 'data/arch.js is listed in files.json')
if os.path.isdir('dist'):
    check(os.path.isfile('dist/data/arch.js'), 'dist/ has data/arch.js')

# la ruta, ejecutada en node
page = open('index.html', encoding='utf-8').read()
core = re.search(r'const ROUTE_MODES=.*?function routeBuild\(st\)\{.*?\n\}\n', page, re.S)
check(bool(core), 'the route helpers are in index.html')
if core:
    harness = r'''
const slug = s => String(s).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'').replace(/[^a-z0-9]+/g,'-');
%s
const t = [];
let r = routeParse('?mode=archetype&name=Snake-Eye');  t.push(r.mode==='arq' && r.name==='archetype' && r.arch==='snake-eye');
r = routeParse('?mode=archetype&name=%%3Cscript%%3E');  t.push(/^[a-z0-9-]*$/.test(r.arch));
r = routeParse('?mode=tcg&name=x');                    t.push(r.arch==='');
r = routeParse('?mode=lore&entry=Shaddoll');           t.push(r.mode==='lore' && r.entry==='shaddoll');
t.push(routeBuild({mode:'arq',tcgf:'',view:'meta',deck:'',arch:'branded'})==='?mode=archetype&name=branded');
t.push(routeBuild({mode:'arq',tcgf:'',view:'meta',deck:'',arch:''})==='?mode=archetype');
t.push(routeName('arq','')==='archetype');
r = routeParse('?mode=engines&engine=Fiendsmith&em=gen');  t.push(r.mode==='eng' && r.eng==='fiendsmith' && r.em==='gen');
r = routeParse('?mode=engines&engine=%%3Cb%%3E&em=zz');  t.push(/^[a-z0-9-]*$/.test(r.eng) && r.em==='');
t.push(routeBuild({mode:'eng',tcgf:'',view:'meta',deck:'',eng:'bystial',em:''})==='?mode=engines&engine=bystial');
console.log(JSON.stringify(t));
''' % core.group(0)
    r = subprocess.run(['node', '-e', harness], capture_output=True, text=True, encoding='utf-8')
    try:
        res = json.loads(r.stdout.strip())
    except Exception:
        res = []
    labels = ['archetype URL gives the slug', 'archetype slug is sanitised (no markup)', 'name= is ignored outside the archetypes', 'lore entry= is read',
              'archetype URL is written back', 'index URL has no name', 'routeName for the archetypes', 'engine URL gives engine and mode', 'engine slug is sanitised', 'engine URL is written back']
    check(len(res) == len(labels), 'the route harness ran (%s)' % (r.stderr.strip()[:120] if r.stderr else 'ok'))
    for ok, l in zip(res, labels):
        check(ok, l)

print('\nfailed: %d' % len(fails))
sys.exit(1 if fails else 0)
