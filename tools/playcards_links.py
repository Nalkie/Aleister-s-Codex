"""Abre cada fuente de las fichas tácticas y guarda su estado y su título en src/playcards_links.json.   Run from the project root:  python tools/playcards_links.py

  python tools/playcards_links.py            baja solo las URLs que todavía no figuran (o que fallaron)
  python tools/playcards_links.py --refresh  vuelve a bajar todas
  python tools/playcards_links.py <archivo>  solo las fuentes de ese archivo de fichas (para un investigador que está terminando su archivo)

Una URL cuenta como verificada si responde 200 y la página tiene un título que no sea de error (404, Forbidden, «Just a moment…»).
tests/check_playcards.py exige que cada fuente de cada ficha figure acá como verificada; el test no usa la red, por eso este paso es aparte.
Yugipedia rechaza los clientes sin identificar (403): se manda un User-Agent con un contacto, como pide su política de uso de la API.
"""
import concurrent.futures, datetime, html, json, os, re, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, 'src/playcards_links.json')
UA = 'AleistersCodex/1.0 (link check; briloizzo5@gmail.com)'
BAD_TITLE = re.compile(r'not found|\b40[34]\b|^forbidden\s*$|just a moment|access denied|attention required|\berror\b|unavailable|captcha|are you a robot', re.I)


def extract_title(page):
    """El título de una página HTML: og:title si existe, si no <title>. Texto plano, sin espacios de más."""
    for pat in (r'<meta[^>]+property=["\']og:title["\'][^>]+content=(["\'])(.*?)\1', r'<meta[^>]+content=(["\'])(.*?)\1[^>]+property=["\']og:title["\']', r'<title[^>]*>()(.*?)</title>'):
        m = re.search(pat, page, re.I | re.S)
        if m:
            t = re.sub(r'\s+', ' ', html.unescape(m.group(2))).strip()
            if t:
                return t
    return ''


def verified(entry):
    return bool(entry) and entry.get('status') == 200 and len(entry.get('title', '')) >= 3 and not BAD_TITLE.search(entry['title'])


def _plain(t):
    import unicodedata
    return ''.join(c for c in unicodedata.normalize('NFKD', t.lower()) if not unicodedata.combining(c))


def topic_ok(name, url, title):
    """El nombre que la ficha le da a la fuente tiene que corresponder con la página que se abrió.
    Las palabras propias del nombre (4 letras o más, que no sean parte del dominio) deben aparecer en el título real: así una URL que
    devuelve 200 pero otra carta u otro mazo (YGOPRODeck ignora el texto antes del ID) no pasa como si respaldara la ficha."""
    host = _plain(url.split('/')[2])
    toks = [t for t in re.findall(r'[a-z0-9]{4,}', _plain(name)) if t not in host and host.replace('www.', '').find(t) < 0]
    return not toks or any(t in _plain(title) for t in toks)


def fetch(url):
    last = {'status': 0, 'title': '', 'final': url, 'error': ''}
    for i in range(5):
        if last['status'] == 429:   # Yugipedia limita las ráfagas: esperar y reintentar
            time.sleep(8 * i)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/xhtml+xml', 'Accept-Language': 'en,es;q=0.8'})
            with urllib.request.urlopen(req, timeout=45) as r:
                body = r.read(600000).decode(r.headers.get_content_charset() or 'utf-8', 'replace')
                last = {'status': r.status, 'title': extract_title(body), 'final': r.geturl(), 'error': ''}
                break
        except urllib.error.HTTPError as e:
            last = {'status': e.code, 'title': '', 'final': url, 'error': 'HTTP %d' % e.code}
        except Exception as e:
            last = {'status': 0, 'title': '', 'final': url, 'error': str(e)[:120]}
    last['at'] = datetime.date.today().isoformat()
    return last


def sheet_urls(only=None):
    import glob
    files = [only] if only else sorted(glob.glob(os.path.join(ROOT, 'src/playcards/*.json'))) + [os.path.join(ROOT, 'src/playcards.json')]
    urls = {}
    for f in files:
        for key, c in json.load(open(f, encoding='utf-8')).items():
            for s in c.get('sources', []):
                urls.setdefault(s['url'], []).append(key)
    return urls


def names(only=None):
    import glob
    files = [only] if only else sorted(glob.glob(os.path.join(ROOT, 'src/playcards/*.json'))) + [os.path.join(ROOT, 'src/playcards.json')]
    return [(s['url'], s['name']) for f in files for c in json.load(open(f, encoding='utf-8')).values() for s in c.get('sources', [])]


def main():
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(errors='replace')  # consola cp1252: títulos con kanji no deben tirar el verificador
    refresh = '--refresh' in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    urls = sheet_urls(args[0] if args else None)
    rep = json.load(open(REPORT, encoding='utf-8')) if os.path.exists(REPORT) else {}
    todo = [u for u in urls if refresh or not verified(rep.get(u))]
    print('%d fuentes, %d por abrir' % (len(urls), len(todo)))
    with concurrent.futures.ThreadPoolExecutor(3) as ex:
        for u, res in zip(todo, ex.map(fetch, todo)):
            rep[u] = res
            print(('ok   ' if verified(res) else 'FALLA'), res['status'], u[:90], '|', (res['title'] or res['error'])[:70])
    json.dump(dict(sorted(rep.items())), open(REPORT, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    bad = [u for u in urls if not verified(rep.get(u))]
    print('sin verificar:', len(bad))
    for u in bad:
        print('  ', u, '<-', ', '.join(urls[u][:3]))
    off = [(u, n, rep[u]['title']) for u, n in names(args[0] if args else None) if verified(rep.get(u)) and not topic_ok(n, u, rep[u]['title'])]
    print('con el nombre que no corresponde al título:', len(off))
    for u, n, t in off:
        print('  ', u, '| nombre:', n, '| título real:', t)
    bad += [u for u, _, _ in off]
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
