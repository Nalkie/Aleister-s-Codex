"""Valida la sección Lore (src/lore/*.json) y la escribe en data/lore.js.   Run from the project root:  python tools/lore.py

Una entrada por arquetipo.  El build falla (exit 1) si una entrada:
  * no tiene exactamente las claves del contrato, o le falta un idioma (es / en) en algún texto
  * tiene menos de 3 o más de 8 bloques, un párrafo fuera de 50-110 palabras, un título de más de 60 caracteres
  * ilustra un bloque con una carta que no existe en la base (src/ygo_all.json) o con menos de 1 / más de 3 cartas
  * trae más de 2 creadores, o uno sin autor, título, plataforma, fecha, o con una URL que no sea https directa
    (YouTube solo como https://www.youtube.com/watch?v=..., nada de reddit, X, discord, facebook, tiktok)
  * no trae de 1 a 12 fuentes https de lectura (wiki), o repite una URL
  * usa "banish" o "banear" en español (se dice desterrar), o una raya larga (—)
  * el slug no coincide con el nombre del archivo, o dos entradas comparten slug
El contrato está en contracts/lore.ts.
"""
import glob, json, os, re, sys
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYS = {'slug', 'kind', 'name', 'badge', 'origin', 'blocks', 'creators', 'sources', 'notes'}
KINDS = {'archetype', 'character'}
BLOCK_KEYS = {'h', 'p', 'cards'}
CREATOR_KEYS = {'author', 'title', 'url', 'platform', 'checked', 'why'}
SOURCE_KEYS = {'name', 'url', 'checked'}
BANNED_HOSTS = ('reddit.com', 'twitter.com', 'x.com', 'discord.com', 'discord.gg', 'facebook.com', 'tiktok.com')
DATE = re.compile(r'^\d{4}-\d{2}-\d{2}$')
P_MIN, P_MAX, H_MAX, BADGE_MAX, ORIGIN_MAX = 50, 110, 60, 90, 120


def words(t):
    return len(re.findall(r"[\wÀ-ÿ'’-]+", t))


def bi(o, path, out, maxlen=None, optional=False):
    """{es, en} with both texts; returns nothing, appends problems"""
    if not isinstance(o, dict) or set(o) != {'es', 'en'}:
        out.append('%s: tiene que ser {es, en}' % path)
        return
    for l in ('es', 'en'):
        v = o[l]
        if not isinstance(v, str) or (not v.strip() and not optional):
            out.append('%s.%s: vacío' % (path, l))
            continue
        if maxlen and len(v) > maxlen:
            out.append('%s.%s: %d caracteres, el máximo es %d' % (path, l, len(v), maxlen))
        if '—' in v:
            out.append('%s.%s: lleva una raya larga (—)' % (path, l))
    if isinstance(o.get('es'), str) and re.search(r'\bbanish|\bbanear|\bbanea', o['es'], re.I):
        out.append('%s.es: en español se dice desterrar, no banish ni banear' % path)


def check_url(u, path, out, creator=False):
    p = urlparse(u) if isinstance(u, str) else None
    if not p or p.scheme != 'https' or not p.netloc:
        out.append('%s: la URL tiene que ser https' % path)
        return
    host = p.netloc.lower().removeprefix('www.')
    if any(host == h or host.endswith('.' + h) for h in BANNED_HOSTS):
        out.append('%s: %s no se puede abrir ni verificar' % (path, host))
    yt = host in ('youtube.com', 'm.youtube.com', 'youtu.be')
    if yt and not creator:
        out.append('%s: YouTube solo vale como creador, no como fuente de lectura' % path)
    if yt and creator:
        ok = (host != 'youtu.be' and p.path == '/watch' and parse_qs(p.query).get('v')) or (host == 'youtu.be' and len(p.path) > 1)
        if not ok:
            out.append('%s: tiene que ser un enlace directo al video (watch?v=...)' % path)


def problems(entries, names):
    out, seen = [], set()
    for slug, e in entries.items():
        P = lambda s: '%s%s' % (slug, s)
        if not isinstance(e, dict) or set(e) != KEYS:
            out.append('%s: claves %s, tienen que ser %s' % (slug, sorted(e) if isinstance(e, dict) else e, sorted(KEYS)))
            continue
        if e['kind'] not in KINDS:
            out.append('%s: kind tiene que ser archetype o character' % slug)
        if e['slug'] != slug or not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', slug):
            out.append(P(': el slug no coincide con el archivo'))
        if slug in seen:
            out.append(P(': slug repetido'))
        seen.add(slug)
        if not isinstance(e['name'], str) or not e['name'].strip():
            out.append(P('.name: vacío'))
        bi(e['badge'], P('.badge'), out, BADGE_MAX)
        bi(e['origin'], P('.origin'), out, ORIGIN_MAX)
        bi(e['notes'], P('.notes'), out, None, optional=True)
        bl = e['blocks']
        if not isinstance(bl, list) or not 3 <= len(bl) <= 8:
            out.append(P('.blocks: tiene que haber de 3 a 8 bloques'))
            bl = bl if isinstance(bl, list) else []
        for i, b in enumerate(bl):
            B = lambda s: P('.blocks[%d]%s' % (i, s))
            if not isinstance(b, dict) or set(b) != BLOCK_KEYS:
                out.append(B(': claves, tienen que ser h, p, cards'))
                continue
            bi(b['h'], B('.h'), out, H_MAX)
            bi(b['p'], B('.p'), out)
            if isinstance(b['p'], dict):
                for l in ('es', 'en'):
                    n = words(b['p'].get(l, '')) if isinstance(b['p'].get(l), str) else 0
                    if not P_MIN <= n <= P_MAX:
                        out.append(B('.p.%s: %d palabras, tienen que ser de %d a %d' % (l, n, P_MIN, P_MAX)))
                if b['p'].get('es') and b['p'].get('es') == b['p'].get('en'):
                    out.append(B('.p: el texto en inglés es idéntico al español'))
            cs = b['cards']
            if not isinstance(cs, list) or not 1 <= len(cs) <= 3:
                out.append(B('.cards: de 1 a 3 cartas'))
                continue
            for c in cs:
                if c not in names:
                    out.append(B('.cards: la carta "%s" no existe en la base' % c))
            if len(set(cs)) != len(cs):
                out.append(B('.cards: carta repetida'))
        cr = e['creators']
        if not isinstance(cr, list) or len(cr) > 2:
            out.append(P('.creators: como máximo 2'))
            cr = cr if isinstance(cr, list) else []
        for i, c in enumerate(cr):
            C = lambda s: P('.creators[%d]%s' % (i, s))
            if not isinstance(c, dict) or set(c) != CREATOR_KEYS:
                out.append(C(': claves, tienen que ser %s' % sorted(CREATOR_KEYS)))
                continue
            for k in ('author', 'title', 'platform'):
                if not isinstance(c[k], str) or not c[k].strip():
                    out.append(C('.%s: vacío' % k))
            if not (isinstance(c['checked'], str) and DATE.match(c['checked'])):
                out.append(C('.checked: fecha AAAA-MM-DD'))
            check_url(c['url'], C('.url'), out, creator=True)
            bi(c['why'], C('.why'), out, 140)
        so = e['sources']
        if not isinstance(so, list) or not 1 <= len(so) <= 12:
            out.append(P('.sources: de 1 a 12 fuentes'))
            so = so if isinstance(so, list) else []
        urls = []
        for i, s in enumerate(so):
            S = lambda t: P('.sources[%d]%s' % (i, t))
            if not isinstance(s, dict) or set(s) != SOURCE_KEYS:
                out.append(S(': claves, tienen que ser %s' % sorted(SOURCE_KEYS)))
                continue
            if not isinstance(s['name'], str) or not s['name'].strip():
                out.append(S('.name: vacío'))
            if not (isinstance(s['checked'], str) and DATE.match(s['checked'])):
                out.append(S('.checked: fecha AAAA-MM-DD'))
            check_url(s['url'], S('.url'), out)
            urls.append(s['url'])
        urls += [c.get('url') for c in cr if isinstance(c, dict)]
        if len(set(urls)) != len(urls):
            out.append(P(': una URL se repite entre fuentes y creadores'))
    return out


def load_entries():
    entries = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'src/lore/*.json'))):
        slug = os.path.splitext(os.path.basename(f))[0]
        entries[slug] = json.load(open(f, encoding='utf-8'))
    return entries


def card_names():
    return {c['name'] for c in json.load(open(os.path.join(ROOT, 'src/ygo_all.json'), encoding='utf-8'))}


def main():
    os.chdir(ROOT)
    entries = load_entries()
    if not entries:
        sys.exit('ERROR: no hay entradas en src/lore/')
    bad = problems(entries, card_names())
    for b in bad:
        print('ERROR', b)
    if bad:
        sys.exit(1)
    items = sorted(entries.values(), key=lambda e: e['name'].lower())
    os.makedirs('data', exist_ok=True)
    open('data/lore.js', 'w', encoding='utf-8').write('__load("lore",' + json.dumps(items, ensure_ascii=False, separators=(',', ':')) + ');')
    print('data/lore.js: %d arquetipos' % len(items), [e['slug'] for e in items])


if __name__ == '__main__':
    main()
