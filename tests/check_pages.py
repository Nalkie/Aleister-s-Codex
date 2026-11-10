"""Gate: páginas estáticas con vista previa (p/), sitemap.xml y robots.txt (tools/pages.py) y los botones «Copiar enlace».  Run from the project root:  python tests/check_pages.py

  1. cantidades: una página por arquetipo con cartas, serie, duelista (serie + personaje), término del glosario y entrada de Lore; nombres únicos y limpios
  2. cada página, vista como la ve un rastreador SIN JavaScript: título, descripción, canonical y og:url iguales, og:image absoluta que existe, twitter:card grande, <h1>, sin <meta refresh>
  3. cada página lleva a una vista real: el destino se interpreta con la misma regla de rutas de la página y apunta a algo que existe (arquetipo, serie, duelista, término, entrada)
  4. el contenido: lo que dice la página es lo que hay en los datos (cantidad de cartas, definición del glosario, fuentes y licencia en Lore), y todo texto sale escapado
  5. p/ en disco es exactamente lo que genera tools/pages.py; files.json los lista; sitemap.xml es XML válido, sin repetidos, con archivos que existen; robots.txt lo apunta
  6. los botones: pageShareUrl (node, con la función real de src.html) arma el mismo nombre que pages.py para cada tipo de vista, y cae al enlace común sin servidor
  7. cableado: refresh.py genera y lista todo, dist.py lo copia (por files.json)
"""
import html, json, os, re, subprocess, sys, tempfile, xml.etree.ElementTree as ET
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'tools')
import pages

fails = []


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


src = open('src.html', encoding='utf-8').read()
built = pages.all_pages(ROOT)
arch, series, gloss = pages._load('arch', ROOT), pages._load('series', ROOT), pages._load('glossary', ROOT)
lore, deckset = pages._load('lore', ROOT), pages._load('roulette', ROOT)['decks']
have = {c[0] for c in pages._load('index', ROOT)['cards']}

# 1. cantidades
kinds = {}
for k in built:
    kinds.setdefault(k.split('-')[0], []).append(k)
ok('index' in built and len(built) == sum(len(v) for v in kinds.values()), 'hay un índice de páginas (p/index.html) además de las de cada tipo')
by = {}
for i, n in enumerate(arch['n']):
    by[pages.archSlug(n)] = i
cards = {}
for c, i in arch['c'].items():
    if c in have:
        cards.setdefault(i, []).append(c)
want_arch = {s for s, i in by.items() if s and cards.get(i)}
ok(len(kinds.get('archetype', [])) == len(want_arch) and len(want_arch) > 400, 'una página por arquetipo con cartas (%d)' % len(want_arch))
ok(len(kinds.get('series', [])) == len(series['s']) == 6, 'una página por serie (6)')
duelists = {(d['series'], pages.archSlug(d['character'])) for d in deckset}
ok(len(kinds.get('duelist', [])) == len(duelists) and len(duelists) > 50, 'una página por duelista de cada serie (%d)' % len(duelists))
ok(len(kinds.get('glossary', [])) == len(gloss['t']) and len(gloss['t']) > 90, 'una página por término del glosario (%d)' % len(gloss['t']))
ok(len(kinds.get('lore', [])) == len(lore) and len(lore) >= 35, 'una página por entrada de Lore (%d)' % len(lore))
ok(all(re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', k) and len(k) < 100 for k in built), 'los nombres de archivo son minúsculas, números y guiones, y cortos')
ok(len({k.lower() for k in built}) == len(built), 'ningún nombre se repite (tampoco ignorando mayúsculas)')


class P(HTMLParser):
    def __init__(s):
        super().__init__()
        s.meta, s.link, s.h1, s.in_h1, s.title, s.in_t, s.text, s.script, s.in_s, s.a = [], [], '', False, '', False, '', '', False, []

    def handle_starttag(s, t, a):
        a = dict(a)
        if t == 'meta':
            s.meta.append(a)
        elif t == 'link':
            s.link.append(a)
        elif t == 'h1':
            s.in_h1 = True
        elif t == 'title':
            s.in_t = True
        elif t == 'script':
            s.in_s = True
        elif t == 'a':
            s.a.append(a)

    def handle_endtag(s, t):
        s.in_h1 = s.in_h1 and t != 'h1'
        s.in_t = s.in_t and t != 'title'
        s.in_s = s.in_s and t != 'script'

    def handle_data(s, d):
        if s.in_h1:
            s.h1 += d
        if s.in_t:
            s.title += d
        if s.in_s:
            s.script += d
        elif not s.in_t:
            s.text += d


def parse(h):
    p = P()
    p.feed(h)
    return p


def og(p, k):
    return [m.get('content') for m in p.meta if m.get('property') == k or m.get('name') == k]


# 2. vista de rastreador sin JavaScript
bad = {'head': [], 'noindex': [], 'long': [], 'tags': [], 'canon': [], 'img': [], 'refresh': [], 'h1': [], 'desc': []}
parsed = {}
for slug, (title, desc, go, body) in built.items():
    h = pages.page(slug, title, desc, go, body)
    p = parsed[slug] = parse(h)
    url = pages.url(slug)
    ok_head = '<html lang="es">' in h and any(m.get('name') == 'viewport' and 'width=device-width' in m.get('content', '') for m in p.meta) and og(p, 'og:image:width') == ['1200'] and og(p, 'og:image:height') == ['630']
    if not ok_head:
        bad['head'].append(slug)
    if (slug in pages.NOINDEX) != any(m.get('name') == 'robots' and 'noindex' in m.get('content', '') for m in p.meta):
        bad['noindex'].append(slug)
    if len(p.title.strip()) > 60 and pages.NAME in p.title:
        bad['long'].append(slug)
    can = [l['href'] for l in p.link if l.get('rel') == 'canonical']
    if not (p.title.strip() and og(p, 'og:title') == [p.title.strip()] and og(p, 'twitter:title') == [p.title.strip()] and og(p, 'og:description') == og(p, 'description') == og(p, 'twitter:description') and og(p, 'twitter:card') == ['summary_large_image']):
        bad['tags'].append(slug)
    if not (can == [url] and og(p, 'og:url') == [url]):
        bad['canon'].append(slug)
    if not (og(p, 'og:image') == [pages.IMG] == og(p, 'twitter:image') and pages.IMG.startswith('https://') and os.path.isfile('art/og.jpg')):
        bad['img'].append(slug)
    if any((m.get('http-equiv') or '').lower() == 'refresh' for m in p.meta):
        bad['refresh'].append(slug)
    if not p.h1.strip():
        bad['h1'].append(slug)
    d = og(p, 'description')[0]
    if not (30 <= len(d) <= 301):
        bad['desc'].append((slug, len(d)))
for k, v in [('head', 'lang="es", viewport y og:image:width/height 1200x630'), ('noindex', 'noindex solo en las páginas finas (menos de %d cartas)' % pages.MIN_CARDS), ('long', 'el título no pasa de 60 letras con el nombre del sitio'), ('tags', 'título, og:/twitter: y descripción coinciden y la tarjeta es grande'), ('canon', 'canonical y og:url son la propia página'), ('img', 'og:image absoluta (https) y art/og.jpg existe'),
             ('refresh', 'sin <meta refresh> (un rastreador sin JavaScript se queda con el texto)'), ('h1', 'toda página tiene <h1>'), ('desc', 'descripción de 30 a 300 letras')]:
    ok(not bad[k], '%d páginas: %s %s' % (len(built), v, bad[k][:3] if bad[k] else ''))
w, h_ = [int(x) for x in re.findall(r'(\d+)', subprocess.run([sys.executable, '-c', 'from PIL import Image;print(Image.open("art/og.jpg").size)'], capture_output=True, text=True).stdout)[:2]]
ok((w, h_) == (1200, 630), 'la imagen general mide 1200x630 como declaran las etiquetas')

# 3. destinos
sl = {x['id'] for x in series['s']}
chars = {(d['series'], pages.archSlug(d['character'])) for d in deckset}
terms = {t['s'] for t in gloss['t']}
entries = {e['slug'] for e in lore}
dest_bad = []
for slug, (title, desc, go, body) in built.items():
    p = parsed[slug]
    if slug == 'index':
        continue
    m = re.fullmatch(r'\.\./\?(.*)', go)
    q = dict(x.split('=', 1) for x in m.group(1).split('&')) if m else {}
    mode = q.get('mode')
    good = (mode == 'archetype' and q.get('name') in want_arch) or (mode == 'series' and q.get('name') in sl and (not q.get('char') or (q['name'], q['char']) in chars)) \
        or (mode == 'glossary' and q.get('term') in terms) or (mode == 'lore' and q.get('entry') in entries)
    js = re.search(r'location\.replace\((".*?")\+location\.hash\)', p.script)
    if not (good and js and json.loads(js.group(1)) == go and any(a.get('href') == go for a in p.a)):
        dest_bad.append(slug)
ok(not dest_bad, 'cada página lleva (location.replace y enlace visible) a una vista que existe %s' % dest_bad[:3])
ok(all(('href="duelist-%s-' % s) in built['series-' + s][3] for s in sl if any(c[0] == s for c in chars)) and all(('href="series-%s"' % k.split('-')[1]) in built[k][3] for k in built if k.startswith('duelist-')), 'las páginas se enlazan entre sí: serie a duelistas y duelista a su serie')
hrefs = {k: set(re.findall(r'href="([a-z0-9-]+)"', b)) for k, (t_, d_, g_, b) in built.items()}
linked = set().union(*hrefs.values())
orph = [k for k in built if k != 'index' and k not in linked and k not in pages.NOINDEX]
ok(not orph and all(k in hrefs['index'] for k in built if k != 'index' and k not in pages.NOINDEX), 'ninguna página indexable queda huérfana: todas salen en el índice %s' % orph[:3])
ok(all(a in built for hs in hrefs.values() for a in hs), 'todo enlace relativo entre páginas apunta a una página que existe')
ok(len(pages.NOINDEX) > 0 and all(k.startswith('archetype-') for k in pages.NOINDEX) and all(len(cards[by[k[10:]]]) < pages.MIN_CARDS for k in pages.NOINDEX), 'las páginas finas son solo arquetipos con menos de %d cartas (%d)' % (pages.MIN_CARDS, len(pages.NOINDEX)))
rjs = re.search(r'const ROUTE_MODES=.*?function routeBuild\(st\)\{.*?\n\}\n', open('index.html', encoding='utf-8').read(), re.S)
gos = sorted({g for k, (t_, d_, g, b) in built.items() if k != 'index'})
nodejs = (r"const slug=s=>String(s).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,'-');" + chr(10) + rjs.group(0) + chr(10) + 'const gos=' + json.dumps(gos) + ';' + chr(10)
          + 'const bad=gos.filter(g=>{ const r=routeParse(g.slice(3)); const m={archetype:r.arch,series:r.ser,glossary:r.term,lore:r.entry}[r.name]; return !(m&&r.mode); }); console.log(JSON.stringify({n:gos.length,bad}));')
fj = os.path.join(tempfile.mkdtemp(), 'route.js')
open(fj, 'w', encoding='utf-8').write(nodejs)
rr = subprocess.run(['node', fj], capture_output=True, text=True, encoding='utf-8')
ro = json.loads(rr.stdout) if rr.returncode == 0 else {'n': 0, 'bad': ['node: ' + rr.stderr[:200]]}
ok(ro['n'] > 600 and not ro['bad'], 'la rutas de la página (routeParse real de index.html) entienden el destino de las %d páginas %s' % (ro['n'], ro['bad'][:3]))

# 4. contenido
c_bad = []
for slug, (title, desc, go, body) in built.items():
    p = parsed[slug]
    if slug.startswith('archetype-'):
        name = arch['n'][by[slug[10:]]]
        n = len(cards[by[slug[10:]]])
        lis = len(re.findall(r'<li>', body))
        if not (p.h1.strip() == name and ('%d %s' % (n, 'carta' if n == 1 else 'cartas')) in desc and lis == min(n, pages.MAX_CARDS) and (n <= pages.MAX_CARDS or ('y %d más' % (n - pages.MAX_CARDS)) in body)):
            c_bad.append(slug)
    elif slug.startswith('glossary-'):
        t = next(x for x in gloss['t'] if x['s'] == slug[9:])
        if not (p.h1.strip() == t['n']['es'] and t['d']['es'] in p.text and desc.rstrip('…').rstrip() in t['d']['es'].replace('\n', ' ')):
            c_bad.append(slug)
    elif slug == 'index':
        continue
    elif slug.startswith('lore-'):
        e = next(x for x in lore if x['slug'] == slug[5:])
        if not (p.h1.strip() == e['name'] and e['badge']['es'] in p.text and 'se basa en Yugipedia y se comparte bajo la licencia CC BY-SA' in p.text and all(a.get('rel') == 'noopener' for a in p.a if a.get('href', '').startswith('http')) and all(any(a.get('href') == s['url'] for a in p.a) for s in e['sources'])):
            c_bad.append(slug)
    elif slug.startswith('series-'):
        x = next(y for y in series['s'] if y['id'] == slug[7:])
        if not (x['b']['es'] in p.text and str(x['y']) in p.text):
            c_bad.append(slug)
    elif slug.startswith('duelist-'):
        mine = [d for d in deckset if 'duelist-%s-%s' % (d['series'], pages.archSlug(d['character'])) == slug]
        if not (mine and p.h1.strip() == mine[0]['character'] and all(d['name'] in p.text for d in mine)):
            c_bad.append(slug)
ok(not c_bad, 'el texto de cada página sale de los datos (%d páginas) %s' % (len(built), c_bad[:3]))
raw = [s for s, (t, d, g, b) in built.items() if re.search(r'<[a-z]', re.sub(r'<(/?(h1|h2|p|ul|li|a|b)\b[^>]*)>', '', b)) or '&amp;amp;' in b]
ok(not raw, 'el cuerpo no deja etiquetas ni entidades sin escapar %s' % raw[:3])
amp = next(s for s, (t, d, g, b) in built.items() if '&' in html.unescape(b) and s.startswith('archetype-'))
ok('&amp;' in built[amp][3] or '&' not in built[amp][3].replace('&amp;', '').replace('&#x27;', '').replace('&quot;', '').replace('&lt;', '').replace('&gt;', ''), 'un nombre con & sale escapado (%s)' % amp)
tr = pages.page('x', 'A "B" <i>&', 'd "q" <b>', '../?mode=lore&entry=x', '<h1>A</h1>')
ok('<i>' not in tr and '<b>' not in tr and 'A &quot;B&quot; &lt;i&gt;&amp;' in tr, 'el título y la descripción con comillas, < y & salen escapados')
ok(not re.search(r'banish|banear', ' '.join(re.sub(r'<li>.*?</li>', '', b) for t, d, g, b in built.values()), re.I), 'ningún texto de página usa «banish» ni «banear» (en español: desterrar; los nombres de carta en inglés no cuentan)')
ok(pages.clip('a ' * 400, 300).endswith('…') and len(pages.clip('a ' * 400, 300)) <= 301 and pages.clip('corto') == 'corto', 'clip() corta en una palabra con … y deja el texto corto igual')

# 5. disco, files.json, sitemap, robots
disk = sorted(os.listdir('p'))
ok(disk == sorted(k + '.html' for k in built), 'p/ tiene exactamente las %d páginas que genera tools/pages.py (ni una de más ni de menos)' % len(built))
stale = [k for k, (t, d, g, b) in built.items() if open('p/%s.html' % k, encoding='utf-8', newline='').read() != pages.page(k, t, d, g, b)]
ok(not stale, 'cada archivo de p/ está al día con los datos %s' % stale[:3])
listed = {f['path'] for f in json.load(open('files.json', encoding='utf-8'))}
ok(all('p/' + f in listed for f in disk) and {'sitemap.xml', 'robots.txt'} <= listed and not [x for x in listed if x.startswith('p/') and x[2:] not in disk], 'files.json lista p/, sitemap.xml y robots.txt (y nada de p/ que no exista)')
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
tree = ET.parse('sitemap.xml').getroot()
locs = [u.find('s:loc', ns).text for u in tree.findall('s:url', ns)]
ok('Disallow' not in pages.robots() and 'Sitemap:' in pages.robots(), 'el robots.txt generado no bloquea nada')
ok(len(locs) == len(set(locs)) and locs[0] == pages.SITE + '/' and all(u.startswith(pages.SITE + '/') for u in locs), 'sitemap.xml es XML válido, empieza por la portada y no repite direcciones (%d)' % len(locs))
ok(all(os.path.isfile(u[len(pages.SITE) + 1:] + '.html') or u[len(pages.SITE) + 1:] in ('p/',) and os.path.isfile('p/index.html') for u in locs[1:]), 'cada dirección del sitemap (sin .html) es un archivo .html que existe')
ok(not [u for u in locs if u.endswith('.html')] and not tree.findall('.//s:lastmod', ns), 'el sitemap usa las direcciones finales (sin .html) y no inventa lastmod')
ok({u for u in locs if '/p/' in u} == {pages.url(f[:-5]) for f in disk if f[:-5] not in pages.NOINDEX} and {u for u in locs if '/r/' in u} == {'%s/r/%s' % (pages.SITE, f[:-5]) for f in os.listdir('r')}, 'el sitemap lista las páginas indexables de p/ y las de r/, y deja afuera las finas')
rb = open('robots.txt', encoding='utf-8').read()
ok(rb == pages.robots(), 'robots.txt en disco es el que genera tools/pages.py')
ok('User-agent: *' in rb and 'Allow: /' in rb and 'Sitemap: %s/sitemap.xml' % pages.SITE in rb and not re.search(r'^Disallow:\s*(/|/p/?|/r/?|/og/?|/art/?|/data/?)?\s*$', rb, re.M) or 'Disallow' not in rb, 'robots.txt deja pasar todo (ni /, ni /p/, /r/, /og/, /art/, /data/) y apunta al sitemap')
t = tempfile.mkdtemp()
os.makedirs(os.path.join(t, 'data'))
for n in ('arch', 'index', 'lore', 'roulette', 'series', 'glossary'):
    open(os.path.join(t, 'data', n + '.js'), 'wb').write(open('data/%s.js' % n, 'rb').read())
os.makedirs(os.path.join(t, 'p'))
open(os.path.join(t, 'p', 'viejo.html'), 'w').write('x')
n1 = pages.build(t, '2026-01-01')
a1 = open(os.path.join(t, 'sitemap.xml'), encoding='utf-8').read()
n2 = pages.build(t, '2026-01-01')
ok(n1 == n2 == len(built) and a1 == open(os.path.join(t, 'sitemap.xml'), encoding='utf-8').read() and not os.path.exists(os.path.join(t, 'p', 'viejo.html')) and len(os.listdir(os.path.join(t, 'p'))) == len(built),
   'build() es repetible y borra lo que ya no existe')

# 6. los botones (node, con la función real)
m = re.search(r'function pageShareUrl\(\)\{.*?\n(?=function pageCopy)', src, re.S)
ok(bool(m), 'src.html trae pageShareUrl')
if m:
    sample = {'archetype': 'archetype-' + sorted(want_arch)[5], 'series': 'series-dm', 'duelist': next(k for k in built if k.startswith('duelist-dm-')), 'glossary': 'glossary-' + gloss['t'][0]['s']}
    dm_char = sample['duelist'][len('duelist-dm-'):]
    js = '''let mode, ARCH={sel:''}, SER={sel:'',char:''}, GL={sel:''}, location={protocol:'https:',origin:'https://x.test',pathname:'/app/',href:'https://x.test/app/?mode=archetype'};
%s
const out={}, T=(k,m,a,s,g,proto)=>{ mode=m; ARCH.sel=a||''; SER.sel=s||''; SER.char=''; GL.sel=g||''; location.protocol=proto||'https:'; return pageShareUrl(); };
out.arch=T('a','arq','%s'); out.ser=T('s','ser','','dm'); mode='ser'; SER.sel='dm'; SER.char='%s'; location.protocol='https:'; out.duel=pageShareUrl();
out.glos=T('g','glos','','','%s'); out.none=T('n','arq',''); out.file=T('f','arq','%s','','','file:'); out.other=T('o','tcg','x');
console.log(JSON.stringify(out));''' % (m.group(0), sample['archetype'][10:], dm_char, sample['glossary'][9:], sample['archetype'][10:])
    f = os.path.join(tempfile.mkdtemp(), 'share.js')
    open(f, 'w', encoding='utf-8').write(js)
    r = subprocess.run(['node', f], capture_output=True, text=True, encoding='utf-8')
    o = json.loads(r.stdout) if r.returncode == 0 else {}
    ok(bool(o), 'pageShareUrl corre en node %s' % r.stderr[:200])
    base = 'https://x.test/app/p/'
    ok(o.get('arch') == base + sample['archetype'] and o.get('ser') == base + 'series-dm' and o.get('duel') == base + sample['duelist'] and o.get('glos') == base + sample['glossary'], 'cada vista arma el nombre de página que genera pages.py (arquetipo, serie, duelista, término)')
    ok(all(os.path.isfile('p/' + os.path.basename(o[k]) + '.html') for k in ('arch', 'ser', 'duel', 'glos')), 'y esas páginas existen en p/')
    ok(o.get('none') == o.get('file') == o.get('other') == 'https://x.test/app/?mode=archetype', 'sin vista elegida, sin servidor (file:) o en otro modo, comparte el enlace común')
ok(src.count('data-pcopy="1"') == 3 and 'd.pcopy!==undefined' in src and re.search(r'function pageCopy\(\).*?clipboard\.writeText\(url\)', src, re.S), 'tres botones «Copiar enlace» (arquetipo, serie/duelista, término) y su handler copian al portapapeles')
ok(re.search(r"GL\.sel===x\.s\?'<p><button class=\"abtn\" data-pcopy=\"1\">", src) and re.search(r"SER\.char&&!cs\.some\(y=>archSlug\(y\.name\)===SER\.char\)\?'':", src), 'el botón del duelista no aparece si el duelista no existe y el del término solo en el elegido')

# 7. cableado
ref = open('tools/refresh.py', encoding='utf-8').read()
ok("run('tools/pages.py')" in ref and "'p'," in ref and "'sitemap.xml', 'robots.txt'" in ref and 'tests/check_pages.py' in ref, 'refresh.py genera p/, lista p/, sitemap.xml y robots.txt y corre este test')
dist = open('tools/dist.py', encoding='utf-8').read()
ok('files.json' in dist, 'dist.py copia lo que lista files.json (incluidos p/, sitemap.xml y robots.txt)')
if os.path.isdir('dist'):
    ok(os.path.isfile('dist/sitemap.xml') and os.path.isfile('dist/robots.txt') and len(os.listdir('dist/p')) == len(built), 'dist/ ya trae p/, sitemap.xml y robots.txt')

print('failed:', len(fails))
sys.exit(1 if fails else 0)
