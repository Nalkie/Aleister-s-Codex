"""Páginas estáticas para buscadores y vistas previas: una página HTML por arquetipo, serie, duelista, término del glosario y entrada de Lore, más sitemap.xml y robots.txt.
Desde la raíz del proyecto:  python tools/pages.py        (sin red; lee data/*.js, que deja tools/refresh.py)

El sitio es una sola página que arma todo con JavaScript, y los rastreadores de enlaces (Discord, WhatsApp, Telegram, X) no lo ejecutan: cualquier ?mode=... mostraría la tarjeta general.
Cada página de p/ trae su propio título, descripción y etiquetas og:/twitter: más el texto principal (para quien no corre JavaScript) y manda al navegador a la vista real con location.replace.
No hay <meta refresh>: así un rastreador que no ejecuta JavaScript se queda con el texto y con el canonical de esta página.  La imagen es la general del sitio (art/og.jpg); los mazos de la ruleta ya tienen la suya (tools/og.py).
sitemap.xml lista la portada, las páginas de p/ y las de r/; robots.txt lo apunta.  Mismo insumo, mismo resultado.  Salida: p/, sitemap.xml y robots.txt (los lista files.json y los sube dist.py)."""
import html, json, os, re, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = 'https://aleisters-codex.pages.dev'
IMG = SITE + '/art/og.jpg'
NAME = "Aleister's Codex"
SERIES = {'dm': 'Yu-Gi-Oh! Duel Monsters', 'gx': 'Yu-Gi-Oh! GX', '5d': "Yu-Gi-Oh! 5D's", 'zx': 'Yu-Gi-Oh! ZEXAL', 'av': 'Yu-Gi-Oh! ARC-V', 'vr': 'Yu-Gi-Oh! VRAINS'}
MIN_CARDS = 3        # un arquetipo con menos cartas tiene página (para compartir) pero va con noindex y fuera del sitemap: es contenido fino
NOINDEX = set()
MAX_CARDS = 400     # nombres de carta listados en la página de un arquetipo


def archSlug(n):                        # igual que archSlug de src.html
    return re.sub(r'^-+|-+$', '', re.sub(r'[^a-z0-9]+', '-', str(n).lower()))


def _load(name, root):
    s = open(os.path.join(root, 'data', name + '.js'), encoding='utf-8').read()
    a = min(i for i in (s.find('{'), s.find('[')) if i >= 0)
    return json.loads(s[a:s.rindex('}' if s[a] == '{' else ']') + 1])


def clip(t, n=300):
    t = re.sub(r'\s+', ' ', t or '').strip()
    if len(t) <= n:
        return t
    cut = t[:n].rsplit(' ', 1)[0].rstrip(',;:.')
    return cut + '…'


def url(slug):
    """Dirección pública sin .html: Cloudflare Pages redirige /p/x.html a /p/x, y el canonical tiene que ser la dirección final."""
    return SITE + '/p/' + ('' if slug == 'index' else slug)


def page(slug, title, desc, go, body, kind='website'):
    """Una página: <slug> es la ruta bajo p/ (sin .html), <go> la vista real (relativa a p/), <body> el HTML del texto principal."""
    e = html.escape
    u = url(slug)
    full = '%s · %s' % (title, NAME)
    if len(full) > 60:
        full = title        # Google corta cerca de 60 letras: el nombre del sitio sobra
    robots = '<meta name="robots" content="noindex,follow">' if slug in NOINDEX else ''
    return f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(full)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(u)}">{robots}
<meta property="og:type" content="{kind}"><meta property="og:site_name" content="{e(NAME)}"><meta property="og:locale" content="es_AR">
<meta property="og:url" content="{e(u)}"><meta property="og:title" content="{e(full)}"><meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(IMG)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{e(full)}"><meta name="twitter:description" content="{e(desc)}"><meta name="twitter:image" content="{e(IMG)}">
<style>body{{margin:0;padding:24px 16px;background:#070a1c;color:#eef1ff;font:16px/1.55 system-ui,sans-serif}}main{{max-width:46rem;margin:0 auto}}a{{color:#4ee1ff}}h1{{font-size:1.6rem;margin:.2em 0}}.k{{color:#9aa4d6;font-size:.85rem;text-transform:uppercase;letter-spacing:.06em}}ul{{columns:2;padding-left:1.2em}}@media(max-width:560px){{ul{{columns:1}}}}</style>
</head><body><main><p class="k">{e(NAME)}</p>
{body}
<p><a href="{e(go)}">Abrir en {e(NAME)}</a></p></main>
<script>location.replace({json.dumps(go)}+location.hash)</script></body></html>
'''


def _q(**kw):
    return '../?' + urllib.parse.urlencode(kw)


def arch_pages(root):
    a = _load('arch', root)
    have = {c[0] for c in _load('index', root)['cards']}
    by, cards = {}, [[] for _ in a['n']]
    for i, n in enumerate(a['n']):
        by[archSlug(n)] = i             # si dos nombres dan el mismo slug gana el último, como en la página (archIndex)
    for c, i in a['c'].items():
        if c in have:
            cards[i].append(c)
    lore = {e['slug']: e for e in _load('lore', root)}
    lore_of = {}
    for s, idx in a['la'].items():
        for i in idx:
            lore_of.setdefault(i, []).append(s)
    out = {}
    for slug, i in sorted(by.items()):
        name, cs = a['n'][i], sorted(cards[i], key=str.lower)
        if not slug or not cs:
            continue
        n = len(cs)
        hist = [lore[s]['badge']['es'] for s in lore_of.get(i, []) if s in lore]
        desc = '%s: %d %s del TCG de Yu-Gi-Oh!%s' % (name, n, 'carta' if n == 1 else 'cartas', ('. ' + hist[0]) if hist else '. Lista de cartas del arquetipo.')
        e = html.escape
        body = '<h1>%s</h1><p>%s</p>' % (e(name), e(hist[0] + '.' if hist else '%d %s del TCG de Yu-Gi-Oh!' % (n, 'carta' if n == 1 else 'cartas')))
        for ls in lore_of.get(i, []):
            if ls in lore:
                body += '<p>Su historia: <a href="lore-%s">%s</a>.</p>' % (e(ls), e(lore[ls]['name']))
        if n < MIN_CARDS:
            NOINDEX.add('archetype-' + slug)
        body += '<ul>%s</ul>' % ''.join('<li>%s</li>' % e(c) for c in cs[:MAX_CARDS])
        if n > MAX_CARDS:
            body += '<p>y %d más.</p>' % (n - MAX_CARDS)
        out['archetype-' + slug] = (name + ' · Arquetipo', clip(desc), _q(mode='archetype', name=slug), body)
    return out


def series_pages(root):
    s = _load('series', root)
    decks = _load('roulette', root)['decks']
    out, e = {}, html.escape
    for x in s['s']:
        name = SERIES[x['id']]
        blurb = x['b']['es']
        chars = sorted({d['character'] for d in decks if d['series'] == x['id']})
        body = '<h1>%s</h1><p>%s</p><p>Año: %d. Protagonista: %s.</p>' % (e(name), e(blurb), x['y'], e(x['p']))
        if chars:
            body += '<p>Duelistas con mazo armado:</p><ul>%s</ul>' % ''.join('<li><a href="duelist-%s-%s">%s</a></li>' % (x['id'], archSlug(c), e(c)) for c in chars)
        out['series-' + x['id']] = (name, clip(blurb), _q(mode='series', name=x['id']), body)
    sd = {x['id']: x for x in s['s']}
    seen = set()
    for d in decks:
        key = (d['series'], archSlug(d['character']))
        if key in seen or not key[1]:
            continue
        seen.add(key)
        mine = [k for k in decks if (k['series'], archSlug(k['character'])) == key]
        sname = SERIES[d['series']]
        names = [k['name'] for k in mine]
        desc = '%s, duelista de %s. %s' % (d['character'], sname, ('Mazos armados con cartas reales: ' + ', '.join(names) + '.') if names else '')
        body = '<h1>%s</h1><p>Duelista de <a href="series-%s">%s</a>.</p><ul>%s</ul>' % (e(d['character']), d['series'], e(sname), ''.join('<li><b>%s</b>: %s</li>' % (e(k['name']), e(clip(k.get('blurb'), 200))) for k in mine))
        out['duelist-%s-%s' % (d['series'], key[1])] = ('%s · %s' % (d['character'], sname), clip(desc), _q(mode='series', name=d['series'], char=key[1]), body)
    return out


def glossary_pages(root):
    g = _load('glossary', root)
    cat = {c['id']: c['es'] for c in g['cats']}
    out, e = {}, html.escape
    for t in g['t']:
        n, d = t['n']['es'], t['d']['es']
        body = '<h1>%s</h1><p class="k">%s</p><p>%s</p>' % (e(n), e(cat.get(t['c'], '')), e(d))
        out['glossary-' + t['s']] = ('%s · Glosario' % n, clip(d), _q(mode='glossary', term=t['s']), body)
    return out


def lore_pages(root):
    out, e = {}, html.escape
    for x in _load('lore', root):
        n, badge, origin = x['name'], x['badge']['es'], x['origin']['es']
        body = '<h1>%s</h1><p>%s</p><p>Origen: %s.</p>' % (e(n), e(badge), e(origin.rstrip('.')))
        if x.get('sources'):
            body += '<p>Fuentes: %s. Parte del texto del sitio se basa en Yugipedia y se comparte bajo la licencia CC BY-SA.</p>' % ', '.join('<a href="%s" rel="noopener">%s</a>' % (e(s['url']), e(s['name'])) for s in x['sources'])
        out['lore-' + x['slug']] = ('%s · Historia' % n, clip('%s. Origen: %s.' % (badge.rstrip('.'), origin.rstrip('.'))), _q(mode='lore', entry=x['slug']), body)
    return out


def all_pages(root=None):
    root = root or ROOT
    out = {}
    NOINDEX.clear()
    for f in (arch_pages, series_pages, glossary_pages, lore_pages):
        for k, v in f(root).items():
            assert k not in out, k
            out[k] = v
    e = html.escape
    sec = lambda t, pre: '<h2>%s</h2><ul>%s</ul>' % (t, ''.join('<li><a href="%s">%s</a></li>' % (e(k), e(v[0].split(' · ')[0])) for k, v in sorted(out.items()) if k.startswith(pre) and k not in NOINDEX))
    body = '<h1>Series, duelistas, glosario, historias y arquetipos</h1>' + sec('Series', 'series-') + sec('Duelistas', 'duelist-') + sec('Glosario', 'glossary-') + sec('Historias', 'lore-') + sec('Arquetipos', 'archetype-')
    out['index'] = ('Índice de páginas', "Todas las series, duelistas, términos del glosario, historias y arquetipos de Aleister's Codex.", '../', body)
    return out


def sitemap(slugs, root, today=None):
    urls = [SITE + '/'] + [url(s) for s in sorted(slugs) if s not in NOINDEX]
    rdir = os.path.join(root, 'r')
    if os.path.isdir(rdir):
        urls += ['%s/r/%s' % (SITE, f[:-5]) for f in sorted(os.listdir(rdir)) if f.endswith('.html')]
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % ''.join('<url><loc>%s</loc></url>\n' % html.escape(u) for u in urls)


def robots():
    return 'User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE


def build(root=None, today=None):
    import datetime
    root = root or ROOT
    today = today or datetime.date.today().isoformat()
    pages = all_pages(root)
    pdir = os.path.join(root, 'p')
    os.makedirs(pdir, exist_ok=True)
    for slug, (title, desc, go, body) in pages.items():
        open(os.path.join(pdir, slug + '.html'), 'w', encoding='utf-8', newline='\n').write(page(slug, title, desc, go, body))
    for f in os.listdir(pdir):          # lo que ya no existe no deja página
        if f[:-5] not in pages and f.endswith('.html'):
            os.remove(os.path.join(pdir, f))
    open(os.path.join(root, 'sitemap.xml'), 'w', encoding='utf-8', newline='\n').write(sitemap(pages, root, today))
    open(os.path.join(root, 'robots.txt'), 'w', encoding='utf-8', newline='\n').write(robots())
    return len(pages)


if __name__ == '__main__':
    os.chdir(ROOT)
    print('p/: %d páginas + sitemap.xml + robots.txt' % build())
