"""Engines (paquetes de cartas que se splashean en mazos) per game mode, with the cards that make each one up, and the staples apart -> data/engines.js.
Run from the project root after tools/ygm.py and tools/fetch_engines.py:  python tools/engines.py
  * Which decks play an engine: TCG, OCG and Genesys use the engine labels of YuGiOh Meta on each tournament deck (src/ygm_topdecks.json, same window as the meta lists);
    Duel Links uses Duel Links Meta's engines (src/engines_dlm.json) over the last 42 days of decks: a deck has the engine when it has at least half of the cards that identify it.
  * Which cards make it up: the sources only name the card that triggers each engine, so the package is measured. A card belongs to an engine when at least PACK_IN of the
    decks that play it include the card and it is at least PACK_LIFT points more common there than in the decks that do not (so a card every deck plays is not part of it).
    An engine needs at least 3 such cards: a label with a single card (Dominus Purge, Super Polymerization...) is a staple, not an engine.
  * A label that names a single card and belongs to no archetype (Dominus Purge, Super Polymerization, The Fallen & The Virtuous...) is a staple, not an engine: an engine
    needs two or more identifying cards or an archetype of its own (relatedDeckTypes). Those labels go to the staples.
  * Staples: cards that PLAY at least STAPLE_IN of the decks of the mode. They are listed apart so they are not mistaken for an engine.
Everything is counted; the only prose is each card's own text."""
import collections, datetime, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_SHARE, MIN_DECKS, MAX_ENGINES = 1.5, 5, 28
DL_MIN_SHARE, DL_MIN_DECKS = 0.8, 3
PACK_IN, PACK_LIFT, MIN_PACK, MAX_PACK = 0.55, 0.40, 3, 12
STAPLE_IN, MAX_STAPLES = 0.22, 14


def excerpt(text, limit=230):
    t = re.sub(r'\s+', ' ', (text or '').replace('●', '·')).strip()
    if len(t) <= limit:
        return t
    cut = t[:limit]
    i = max(cut.rfind('. '), cut.rfind('; '))
    return (cut[:i + 1] if i > 80 else cut.rsplit(' ', 1)[0] + '…')


def deck_cards(d):
    """{card name: copies} of a tournament deck, any section."""
    out = collections.Counter()
    for sec in ('main', 'extra', 'side'):
        for c in d.get(sec, []) or []:
            card = c.get('card')
            if isinstance(card, dict) and card.get('name'):
                out[card['name']] += c.get('amount', 1)
    return out


def package(inside, outside):
    """Cards that define an engine. inside / outside: lists of {card: copies} of the decks that play it and of the ones that do not.
    Returns [(card, share of the engine decks that include it, average copies)], strongest first."""
    n_in, n_out = len(inside), max(len(outside), 1)
    c_in, c_out, copies = collections.Counter(), collections.Counter(), collections.Counter()
    for d in inside:
        for k, v in d.items():
            c_in[k] += 1
            copies[k] += v
    for d in outside:
        for k in d:
            c_out[k] += 1
    rows = []
    for k, n in c_in.items():
        p_in, p_out = n / n_in, c_out[k] / n_out
        if p_in >= PACK_IN and p_in - p_out >= PACK_LIFT:
            rows.append((k, round(p_in * 100), round(copies[k] / n, 1), p_in - p_out))
    rows.sort(key=lambda r: (-r[3], -r[1], r[0]))
    return [r[:3] for r in rows[:MAX_PACK]]


def staples(decks, text_of, labels=()):
    """labels: (card, share %) of single-card engine labels that are staples."""
    n, c = len(decks) or 1, collections.Counter()
    for d in decks:
        for k in d:
            c[k] += 1
    pct = {k: round(v / n * 100) for k, v in c.items() if v / n >= STAPLE_IN}
    for k, p in labels:
        if p >= 5:
            pct[k] = max(pct.get(k, 0), p)
    return [{'n': k, 'pct': p, 'txt': excerpt(text_of(k), 150)} for k, p in sorted(pct.items(), key=lambda kv: (-kv[1], kv[0]))[:MAX_STAPLES]]


def summarize(engine_decks, wins, archs, decks, text_of, min_share=MIN_SHARE, min_decks=MIN_DECKS, is_engine=lambda name: True):
    """engine_decks: {engine name: [deck index]}; decks: list of {card: copies}."""
    total = len(decks) or 1
    out = []
    for name, idx in sorted(engine_decks.items(), key=lambda kv: -len(kv[1])):
        n = len(idx)
        share = n / total * 100
        if n < min_decks or share < min_share:
            continue
        if not is_engine(name):
            continue
        inside = [decks[i] for i in idx]
        have = set(idx)
        pack = package(inside, [d for i, d in enumerate(decks) if i not in have])
        if len(pack) < MIN_PACK:
            continue
        central = next((c for c, *_ in pack if text_of(c)), pack[0][0])
        a = archs[name].most_common()
        out.append({'n': name, 'decks': n, 'share': round(share, 1), 'wins': wins[name], 'archN': len(a), 'archs': [[x, c] for x, c in a[:5]],
                    'pack': [[c, p, k] for c, p, k in pack], 'central': central, 'txt': excerpt(text_of(central))})
        if len(out) >= MAX_ENGINES:
            break
    return out


if __name__ == '__main__':
    os.chdir(ROOT)
    ygo = {c['name']: c['desc'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
    dltxt = {}
    for c in json.load(open('src/dl_text.json', encoding='utf-8')).values():
        dltxt.setdefault(c['name'], c.get('description'))
    text_of = lambda n: ygo.get(n) or dltxt.get(n) or ''
    ymeta = {e['_id']: e for e in json.load(open('src/engines_ygm.json', encoding='utf-8'))}
    ym_by = {e['name']: e for e in ymeta.values()}
    win = json.load(open('dl/ygmdata.json', encoding='utf-8'))['window']
    all_decks = [d for d in json.load(open('src/ygm_topdecks.json', encoding='utf-8')) if d.get('deckType') and not d.get('incomplete') and win[0] <= d['created'][:10] <= win[1]]
    modes = {}
    for key, flt in (('tcg', lambda d: not d.get('ocg') and not d.get('genesys')), ('ocg', lambda d: bool(d.get('ocg'))), ('gen', lambda d: bool(d.get('genesys')))):
        pool = [d for d in all_decks if flt(d)]
        cards = [deck_cards(d) for d in pool]
        ed, wins, archs = collections.defaultdict(list), collections.Counter(), collections.defaultdict(collections.Counter)
        for i, d in enumerate(pool):
            for e in d.get('engines') or []:
                if e in ymeta:
                    nm = ymeta[e]['name']
                    ed[nm].append(i)
                    wins[nm] += d.get('tournamentPlacement') == 1
                    archs[nm][d['deckType']['name']] += 1
        is_eng = lambda nm: len(ym_by[nm]['requiredCards']) >= 2 or bool(ym_by[nm]['relatedDeckTypes'])
        lab = [(ym_by[nm]['requiredCards'][0]['name'], round(len(ix) / (len(pool) or 1) * 100)) for nm, ix in ed.items() if not is_eng(nm) and ym_by[nm]['requiredCards']]
        modes[key] = {'total': len(pool), 'window': win, 'engines': summarize(ed, wins, archs, cards, text_of, is_engine=is_eng), 'staples': staples(cards, text_of, lab)}
    dlm = [e for e in json.load(open('src/engines_dlm.json', encoding='utf-8')) if e['requiredCards']]
    req = {e['name']: [c['name'] for c in e['requiredCards']] for e in dlm}
    dl = json.load(open('dl/topdecks.json', encoding='utf-8'))
    end = max(d['created'][:10] for d in dl)
    start = (datetime.date.fromisoformat(end) - datetime.timedelta(days=42)).isoformat()
    for key, rush in (('speed', False), ('rush', True)):
        pool = [d for d in dl if bool(d.get('rush')) == rush and d['created'][:10] >= start and d.get('deckType')]
        cards = [deck_cards(d) for d in pool]
        ed, wins, archs = collections.defaultdict(list), collections.Counter(), collections.defaultdict(collections.Counter)
        for i, d in enumerate(pool):
            for nm, r in req.items():
                if sum(x in cards[i] for x in r) >= max(1, -(-len(r) // 2)):
                    ed[nm].append(i)
                    archs[nm][d['deckType']['name']] += 1
        modes[key] = {'total': len(pool), 'window': [start, end], 'engines': summarize(ed, wins, archs, cards, text_of, DL_MIN_SHARE, DL_MIN_DECKS), 'staples': staples(cards, text_of)}
    open('data/engines.js', 'w', encoding='utf-8').write('__load("engines",' + json.dumps({'modes': modes}, ensure_ascii=False, separators=(',', ':')) + ');')
    for k, v in modes.items():
        print(k, v['total'], 'engines', len(v['engines']), [(e['n'], len(e['pack'])) for e in v['engines'][:4]], '· staples', [s['n'] for s in v['staples'][:4]])
