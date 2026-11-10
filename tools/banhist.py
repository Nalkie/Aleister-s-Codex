"""Historial de la banlist del TCG -> data/banhist.js.   Run from the project root:  python tools/banhist.py  (sin red; usa src/banhist/lists.json)
python tools/banhist.py --fetch  vuelve a bajar las páginas de cada lista de Yugipedia (api.php; el HTML de la wiki da 403).

Fuente: las páginas «<Mes Año> Lists (TCG)» de Yugipedia (CC BY-SA), una por lista oficial, encadenadas con prev/next desde mayo de 2002.
Cada página trae la lista completa (forbidden, limited, semi_limited) y, en cada carta que cambió, una nota «// prev::Estado».
(La tabla «Historic TCG Limitations Chart» se descartó: va atrasada y tiene filas rotas.)
Salida (data/banhist.js, __load("banhist", {...})):
  l : listas en orden, cada una [año, mes, día de entrada en vigor]
  c : carta -> [[índice de lista, estado], ...] solo donde el estado cambia; estado 0 prohibida, 1 limitada, 2 semi-limitada,
      3 sin límite (salió de la lista). Una carta que no aparece en una lista tiene estado 3.
  t : título de la página de Yugipedia de cada lista (para enlazar la fuente)
  d : cartas que Yugipedia marca «prev::Not yet released» en su primera lista: eran cartas nuevas desde la lista anterior
  e : índices de las listas que rigieron solo en eventos de alto nivel
  f : [carta, índice de lista] donde la fuente omitía la carta en una lista ajustada y se mantuvo su estado (ver build)
  El estado vigente es el último de cada carta; tests/check_banhist.py lo compara con la banlist actual de Konami.
"""
import html, json, os, re, sys, urllib.parse, urllib.request, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join('src', 'banhist', 'lists.json')
MONTHS = {m: i + 1 for i, m in enumerate('January February March April May June July August September October November December'.split())}
# nombres de Yugipedia que difieren del nombre de la base de cartas del sitio (YGOPRODeck)
ALIAS = {'Maliss P Dormouse': 'Maliss <P> Dormouse', 'Maliss P White Rabbit': 'Maliss <P> White Rabbit', 'Maliss Q White Binder': 'Maliss <Q> White Binder', 'Morphing Jar 2': 'Morphing Jar #2'}
# listas que rigieron solo en eventos de alto nivel (Konami: «Adjusted Forbidden/Limited List», 8 feb a 10 abr de 2016, solo YCS, Regional Qualifier y UDS)
EVENT_ONLY = {'February 2016 Lists'}
KEY = {'forbidden': 0, 'limited': 1, 'semi_limited': 2}
PREV = {'forbidden': 0, 'limited': 1, 'semi-limited': 2, 'semi_limited': 2, 'unlimited': 3}


def _get(title):
    u = 'https://yugipedia.com/api.php?' + urllib.parse.urlencode({'format': 'json', 'action': 'query', 'titles': title, 'prop': 'revisions', 'rvprop': 'content', 'rvslots': 'main', 'redirects': 1})
    for k in range(5):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'AleistersCodex/1.0'}), timeout=60))
            p = list(r['query']['pages'].values())[0]
            return p['title'], (p['revisions'][0]['slots']['main']['*'] if 'revisions' in p else None)
        except Exception:
            time.sleep(3 * (k + 1))
    raise SystemExit('no pude bajar ' + title)


def fetch():
    out, t = {}, 'May 2002 Lists (TCG)'
    while t and t not in out:
        title, w = _get(t)
        if not w:
            raise SystemExit('falta la página ' + t)
        out[title] = w
        m = re.search(r'\|\s*next\s*=\s*([^\n|]+)', w)
        t = m.group(1).strip() if m else None
        time.sleep(.5)
    os.makedirs(os.path.dirname(os.path.join(ROOT, SRC)), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, SRC), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('bajadas %d listas (%s a %s)' % (len(out), list(out)[0], list(out)[-1]))


def parse_page(w):
    """-> (fecha (y, m, d), {carta: estado}, {carta: nota prev})"""
    blk = re.search(r'\{\{Limitation list(.*?)\n\}\}', w, re.S)
    if not blk:
        raise SystemExit('página sin {{Limitation list}}')
    blk = blk.group(1)
    sd = re.search(r'start_date\s*=\s*(\w+) (\d+), (\d{4})', blk)
    date = (int(sd.group(3)), MONTHS[sd.group(1)], int(sd.group(2)))
    state, prev = {}, {}
    parts = re.split(r'\n\|\s*(\w+)\s*=', '\n' + blk)
    for key, body in zip(parts[1::2], parts[2::2]):
        if key not in KEY:
            continue
        for ln in body.split('\n'):
            ln = ln.strip()
            if not ln:
                continue
            name, _, note = ln.partition('//')
            name = html.unescape(re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', name.strip()))
            name = ALIAS.get(name, name)
            if name in state:
                raise SystemExit('carta repetida en una lista: %s' % name)
            state[name] = KEY[key]
            m = re.search(r'prev::\s*([A-Za-z -]+)', note)
            if m:
                prev[name] = m.group(1).strip()
    return date, state, prev


def build():
    pages = json.load(open(os.path.join(ROOT, SRC), encoding='utf-8'))
    parsed = [parse_page(w) for w in pages.values()]
    dates = [p[0] for p in parsed]
    if dates != sorted(dates) or len(set(dates)) != len(dates):
        raise SystemExit('las listas no están en orden cronológico estricto')
    names = sorted({n for _, st, _ in parsed for n in st})
    cards, debut, bad, fixes = {}, [], [], []
    for n in names:
        seq = [st.get(n, 3) for _, st, _ in parsed]
        # Defecto de la fuente: las listas «ajustadas» de emergencia (sep/oct 2013, feb 2016) omiten a veces una carta que sigue en su estado.
        # Se detecta porque la lista donde la carta reaparece o no trae nota prev:: (Yugipedia anota toda carta que cambia, así que
        # sin nota «no cambió»), o trae la del estado de antes del hueco. En los dos casos el hueco se rellena con ese estado.
        # Hoy solo afecta a Return from the Different Dimension (oct 2013) y Trap Dustshoot (sep y oct 2013).
        for i in range(2, len(seq)):
            if seq[i] == 3 or seq[i - 1] != 3:
                continue
            k = i - 1
            while k > 0 and seq[k] == 3:
                k -= 1
            if seq[k] == 3:
                continue                    # la carta no estaba antes del hueco: es una entrada, no un hueco
            note = parsed[i][2].get(n)
            if note is None:
                if seq[k] != seq[i]:
                    raise SystemExit('%s: reaparece en la lista %d sin nota prev:: pero con otro estado que antes del hueco' % (n, i))
            elif PREV.get(note.lower()) != seq[k]:
                continue                    # sale de la lista de verdad y vuelve con una nota que lo dice
            for j in range(k + 1, i):
                seq[j] = seq[k]
                fixes.append([n, j])
        for i, (_, st, pv) in enumerate(parsed):
            note = pv.get(n)
            if note and note.lower() != 'not yet released' and i > 0:
                # La nota compara con la lista anterior, salvo tras una lista «ajustada» de emergencia (oct 2013, feb 2016):
                # ahí compara con la regular de antes. Por eso vale que coincida con cualquiera de las dos listas previas.
                exp = PREV.get(note.lower())
                near = {seq[i - 1], seq[i - 2] if i > 1 else seq[i - 1]}
                if exp is not None and exp not in near:
                    bad.append('%s en lista %d: la nota dice %s y los estados anteriores calculados son %s' % (n, i, note, sorted(near)))
        tr, last = [], None
        for i, v in enumerate(seq):
            if v != last and not (last is None and v == 3):
                tr.append([i, v])
            last = v
        first = next((i for i, v in enumerate(seq) if v != 3), None)
        if first is not None and first > 0 and parsed[first][2].get(n, '').lower() == 'not yet released':
            debut.append(n)
        cards[n] = tr
    if bad:
        raise SystemExit('las notas prev:: de Yugipedia no cuadran con el estado calculado (%d): %s' % (len(bad), bad[:5]))
    return {'l': [list(d) for d in dates], 't': list(pages), 'c': cards, 'd': debut, 'f': fixes, 'e': [i for i, t in enumerate(pages) if t in EVENT_ONLY]}


def konami_current():
    """-> ((año, mes, día), {carta: 0|1|2}) de la banlist vigente de Konami, o None si el archivo no está."""
    f = os.path.join(ROOT, 'src', 'konami_current.json')
    if not os.path.exists(f):
        return None
    k = json.load(open(f, encoding='utf-8'))
    dd, mm, yy = k['from'].split('/')
    st = {}
    for g in '012':
        for x in k.get(g, []):
            n = html.unescape(x['nameeng'])
            st[ALIAS.get(n, n)] = int(g)
    return (int(yy), int(mm), int(dd)), st


def main():
    os.chdir(ROOT)
    if '--fetch' in sys.argv:
        fetch()
    d = build()
    open('data/banhist.js', 'w', encoding='utf-8').write(
        '/* Historial de la banlist del TCG. Fuente: páginas «Forbidden and Limited Lists» de Yugipedia (https://yugipedia.com), licencia CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/). '
        'Modificado: se convirtió cada lista en transiciones de estado por carta. Esta obra derivada se comparte con la misma licencia. */\n'
        '__load("banhist",' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ');')
    print('data/banhist.js: %d listas (%d-%02d a %d-%02d), %d cartas con historial, %d debutan con límite' % (len(d['l']), d['l'][0][0], d['l'][0][1], d['l'][-1][0], d['l'][-1][1], len(d['c']), len(d['d'])))


if __name__ == '__main__':
    main()
