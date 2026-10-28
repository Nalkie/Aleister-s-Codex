"""Valida las fichas tácticas (src/playcards.json) contra las cartas y los mazos reales y las escribe en data/play.js.   Run from the project root:  python tools/playcards.py

El contrato está en contracts/playcard.ts.  El build falla (exit 1) si una ficha:
  * no tiene exactamente las 4 secciones, o le faltan los dos idiomas (es / en) en algún texto
  * nombra una carta que no existe, o que no es legal en el formato (p. ej. Ash Blossom en Edison)
  * pone como iniciador una carta que no está en la lista (principal o extra) del mazo
  * no trae de 2 a 6 fuentes https (sin YouTube, Reddit, X ni Discord) o tiene más de 3 avisos en limits
  * en Duel Links, deja una lista que rompe la banlist (3 copias, Prohibidas, límites compartidos 1/2/3) tras aplicar sus ajustes
  * saca del side una carta que no está en el Main Deck, o mete una que no está en el Side de la lista
  * no corresponde a ningún mazo del ranking de ese formato
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import dl_legal
FORMATS = ('adv', 'ocg', 'edison', 'goat', 'hat', 'gen', 'dl')
PLANS = ('control', 'otk', 'grind', 'tempo', 'combo', 'burn', 'stun')
PACES = ('fast', 'medium', 'slow')
SOURCE_KINDS = ('cards', 'guide', 'results', 'rules', 'list')
BANNED_HOSTS = ('youtube.com', 'youtu.be', 'reddit.com', 'twitter.com', 'x.com', 'discord.com', 'discord.gg', 'facebook.com', 'tiktok.com')   # no se pueden abrir ni verificar
STEPS = ('summon', 'activation', 'resolution', 'attack', 'main', 'end')
SLUG = lambda x: re.sub(r'[^a-z0-9]+', '-', x.lower())
DECK_SLUG = lambda n: SLUG(n).strip('-')


def load_js(path):
    t = open(path, encoding='utf-8').read()
    return json.loads(t[t.index(',') + 1:-2])


def card_name(n):
    """El nombre de una carta como lo guarda la base (ygo_all.json). Las listas de torneo vienen de otras fuentes y escriben distinto:
    «Maliss P Chessy Cat» (lista) es «Maliss <P> Chessy Cat» (base); «Empire of Endymion» es «Endymion Empire»."""
    n = re.sub(r'^Maliss ([PCQ]) ', r'Maliss <\1> ', n)
    return {'Empire of Endymion': 'Endymion Empire'}.get(n, n)


def recipes():
    """{formato: {slug del mazo: {'main': {carta: copias}, 'extra': {...}, 'side': {...}}}}"""
    out = {}
    x = load_js(os.path.join(ROOT, 'data/ygmx.js'))
    for f in ('ocg', 'edison', 'goat', 'hat'):
        out[f] = x.get(f, {}).get('decks', {})
    y = json.load(open(os.path.join(ROOT, 'dl/ygmdata.json'), encoding='utf-8'))
    out['adv'] = y.get('tcg', {}).get('decks', {})
    out['gen'] = y.get('gen', {}).get('decks', {})
    dl = json.load(open(os.path.join(ROOT, 'dl/dldata.json'), encoding='utf-8'))
    out['dl'] = {}
    for mode in ('speed', 'rush'):
        for n, d in dl.get(mode, {}).get('decks', {}).items():
            out['dl'][n.replace(' : Rush!', ' (Rush)').replace(': Rush!', ' (Rush)')] = d      # mismo nombre que muestra la página
    res = {}
    for f, decks in out.items():
        res[f] = {}
        for n, d in decks.items():
            r = d.get('recipe') or {}
            res[f][DECK_SLUG(n)] = {s: {card_name(c[0]): c[1] for c in r.get(s, [])} for s in ('main', 'extra', 'side')}
    return res


def pools():
    f = json.load(open(os.path.join(ROOT, 'src/formats.json'), encoding='utf-8'))
    out = {k: set(v['pool']) for k, v in f.items() if isinstance(v, dict) and 'pool' in v}
    for k, v in recipes().items():      # el pool de YGOPRODeck tiene huecos (le falta Blade Knight en Goat): una carta que juega un mazo real de ese formato es legal por definición
        if k in ('goat', 'edison'):
            out[k] |= {c for d in v.values() for s in d.values() for c in s}
    out['dl'] = set(json.load(open(os.path.join(ROOT, 'dl/cards.json'), encoding='utf-8')))     # las cartas que existen en Duel Links
    if 'hat' in f and 'hat' not in out:     # formats.json no trae el pool de HAT: las cartas ya salidas en el TCG a la fecha del formato, menos las prohibidas
        cards = json.load(open(os.path.join(ROOT, 'src/ygo_all.json'), encoding='utf-8'))
        cut, ban = f['hat']['date'], set(f['hat']['banlist'].get('forbidden', []))
        out['hat'] = {c['name'] for c in cards if c.get('tcg_date') and c['tcg_date'] <= cut and c['name'] not in ban}
    return out


def l10n_ok(v):
    return isinstance(v, dict) and set(v) == {'es', 'en'} and all(isinstance(v[k], str) and 3 <= len(v[k].strip()) <= 400 for k in v)


_BANS = None


def dl_bans():
    global _BANS
    if _BANS is None:
        _BANS = dl_legal.load_bans(os.path.join(ROOT, 'src/dl_bans.json'))
    return _BANS


def problems(cards, names, rec, pool):
    """Devuelve la lista de errores de todas las fichas. cards: {clave: ficha}; names: nombres de cartas reales; rec / pool: ver recipes() y pools()."""
    bad = []
    for key, c in cards.items():
        m = re.fullmatch(r'(%s)/([a-z0-9-]+)' % '|'.join(FORMATS), key)
        if not m:
            bad.append('%s: la clave debe ser formato/slug-del-mazo' % key)
            continue
        fmt, slug = m.groups()
        e = lambda msg: bad.append('%s: %s' % (key, msg))
        want = {'win', 'starters', 'chokepoints', 'side', 'updated', 'sources'} | ({'skills'} if key.startswith('dl/') else set())
        if set(c) - {'limits'} != want:
            e('los campos deben ser exactamente %s, más limits si hace falta (hay %s)' % (sorted(want), sorted(c)))
            continue
        deck = rec.get(fmt, {}).get(slug)
        if deck is None:
            e('no hay un mazo "%s" en el ranking de %s' % (slug, fmt))
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(c['updated'])):
            e('updated debe ser AAAA-MM-DD')

        def card(n, where, need=None):
            if n not in (pool['dl'] if fmt == 'dl' else names):      # Duel Links tiene sus propias cartas (Rush Duel incluido): no están en la base del TCG
                e('%s: la carta "%s" no existe' % (where, n))
            elif fmt in pool and n not in pool[fmt]:
                e('%s: "%s" no es legal en %s' % (where, n, fmt))
            elif need and deck is not None and not any(n in deck[s] for s in need):
                e('%s: "%s" no está en la lista del mazo (%s)' % (where, n, '/'.join(need)))

        srcs = c['sources']
        if not isinstance(srcs, list) or not (2 <= len(srcs) <= 6):
            e('sources: de 2 a 6 fuentes')
        else:
            seen = set()
            for i, x in enumerate(srcs):
                if not isinstance(x, dict) or set(x) != {'name', 'url', 'kind', 'checked'}:
                    e('sources[%d]: name, url, kind y checked' % i)
                    continue
                if x['kind'] not in SOURCE_KINDS:
                    e('sources[%d]: kind debe ser %s' % (i, SOURCE_KINDS))
                if not (isinstance(x['name'], str) and 3 <= len(x['name'].strip()) <= 70):
                    e('sources[%d]: name de 3 a 70 caracteres' % i)
                u = x['url']
                if not (isinstance(u, str) and re.fullmatch(r'https://[^\s"<>]+', u)) or any(h in u.split('/')[2].lower() for h in BANNED_HOSTS) or re.search(r'[?&](utm_|fbclid|gclid)', u):
                    e('sources[%d]: url https, sin seguimiento y que no sea de %s' % (i, '/'.join(BANNED_HOSTS)))
                elif u in seen:
                    e('sources[%d]: url repetida' % i)
                seen.add(u)
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(x['checked'])):
                    e('sources[%d]: checked debe ser AAAA-MM-DD' % i)
        lim = c.get('limits', [])
        if not isinstance(lim, list) or len(lim) > 3 or not all(l10n_ok(x) for x in lim):
            e('limits: de 0 a 3 avisos con es y en')

        w = c['win']
        if set(w) != {'plan', 'pace', 'bullets'} or w['plan'] not in PLANS or w['pace'] not in PACES:
            e('win: plan %s y pace %s, con bullets' % (PLANS, PACES))
        elif not (2 <= len(w['bullets']) <= 4) or not all(l10n_ok(b) for b in w['bullets']):
            e('win: de 2 a 4 viñetas con es y en')
        if not (1 <= len(c['starters']) <= 3):
            e('starters: de 1 a 3 rutas')
        for i, s in enumerate(c['starters']):
            if set(s) != {'cards', 'route'} or not (1 <= len(s['cards']) <= 2) or not l10n_ok(s['route']):
                e('starters[%d]: 1 o 2 cartas y la ruta en es y en' % i)
                continue
            for n in s['cards']:
                card(n, 'starters[%d]' % i, ('main', 'extra'))
        if not (1 <= len(c['chokepoints']) <= 5):
            e('chokepoints: de 1 a 5')
        for i, k in enumerate(c['chokepoints']):
            if set(k) != {'card', 'step', 'stepText', 'loss'} or k['step'] not in STEPS or not l10n_ok(k['stepText']) or not l10n_ok(k['loss']):
                e('chokepoints[%d]: card, step %s, stepText y loss en es y en' % (i, STEPS))
                continue
            card(k['card'], 'chokepoints[%d]' % i)
        if key.startswith('dl/'):          # Duel Links no tiene Side Deck: el cuarto bloque lleva el Skill y los ajustes de cartas
            sk = c['skills']
            if not (1 <= len(sk) <= 3) or not all(set(x) == {'name', 'why'} and isinstance(x['name'], str) and l10n_ok(x['why']) for x in sk):
                e('skills: de 1 a 3, cada uno con name (inglés, como en el juego) y why en es y en')
        sd = c['side']
        if set(sd) != {'first', 'second', 'basis'} or sd['basis'] not in ('editorial', 'tournament'):
            e('side: first, second y basis (editorial | tournament)')
            continue
        for when in ('first', 'second'):
            sw = sd[when]
            if set(sw) != {'in', 'out'} or not sw['in'] or not sw['out']:
                e('side.%s: in y out no pueden estar vacíos' % when)
                continue
            nin, nout = sum(x['qty'] for x in sw['in']), sum(x['qty'] for x in sw['out'])
            if nin != nout:
                e('side.%s: entran %d y salen %d (deben ser las mismas)' % (when, nin, nout))
            for d_, need in (('in', ('side',)), ('out', ('main', 'extra'))):
                for x in sw[d_]:
                    if set(x) != {'card', 'qty', 'why'} or not (1 <= x['qty'] <= 3) or not l10n_ok(x['why']):
                        e('side.%s.%s: card, qty (1 a 3) y why en es y en' % (when, d_))
                        continue
                    card(x['card'], 'side.%s.%s' % (when, d_), (('main', 'extra') if d_ == 'out' else None) if key.startswith('dl/') else need)
                    if deck is not None and d_ == 'out' and deck['main'].get(x['card'], 0) + deck['extra'].get(x['card'], 0) < x['qty']:
                        e('side.%s.out: "%s" x%d, el mazo solo juega %d' % (when, x['card'], x['qty'], deck['main'].get(x['card'], 0)))
                    if deck is not None and d_ == 'in' and not key.startswith('dl/') and deck['side'].get(x['card'], 0) < x['qty']:
                        e('side.%s.in: "%s" x%d, el Side de la lista solo tiene %d' % (when, x['card'], x['qty'], deck['side'].get(x['card'], 0)))
            if key.startswith('dl/') and deck is not None:      # la lista que queda tras el ajuste también tiene que cumplir la banlist de Duel Links
                left = {}
                for sec in ('main', 'extra', 'side'):
                    for nm, n in deck[sec].items():
                        left[nm] = left.get(nm, 0) + n
                for x in sw['out']:
                    left[x['card']] = left.get(x['card'], 0) - x['qty']
                for x in sw['in']:
                    left[x['card']] = left.get(x['card'], 0) + x['qty']
                for v in dl_legal.violations(left, dl_bans(), key.endswith('-rush')):
                    e('side.%s: tras el ajuste la lista rompe la banlist de Duel Links: %s' % (when, v))
    return bad


def load_cards():
    """src/playcards.json más cada archivo de src/playcards/*.json (uno por formato, para que varias personas o sesiones escriban sin pisarse)."""
    import glob
    cards = json.load(open(os.path.join(ROOT, 'src/playcards.json'), encoding='utf-8'))
    for f in sorted(glob.glob(os.path.join(ROOT, 'src/playcards/*.json'))):
        for k, v in json.load(open(f, encoding='utf-8')).items():
            if k in cards:
                sys.exit('ERROR %s: la ficha %s ya existe en otro archivo' % (os.path.basename(f), k))
            cards[k] = v
    return cards


def main():
    os.chdir(ROOT)
    if len(sys.argv) > 1:          # python tools/playcards.py src/playcards/edison.json : valida solo ese archivo, no escribe nada
        only = json.load(open(sys.argv[1], encoding='utf-8'))
        nm = {c['name'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
        bad = problems(only, nm, recipes(), pools())
        for b in bad:
            print('ERROR', b)
        print('' if bad else 'OK: %d fichas válidas' % len(only))
        sys.exit(1 if bad else 0)
    cards = load_cards()
    names = {c['name'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
    bad = problems(cards, names, recipes(), pools())
    for b in bad:
        print('ERROR', b)
    if bad:
        sys.exit(1)
    open('data/play.js', 'w', encoding='utf-8').write('__load("play",' + json.dumps(cards, ensure_ascii=False, separators=(',', ':')) + ');')
    print('data/play.js: %d fichas tácticas' % len(cards), sorted(cards))


if __name__ == '__main__':
    main()
