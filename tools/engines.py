"""Engines (paquetes de cartas que se splashean en mazos) per game mode, with the cards that make each one up, and the staples apart -> data/engines.js.
Run from the project root after tools/ygm.py and tools/fetch_engines.py:  python tools/engines.py
  * Which decks play an engine: TCG, OCG and Genesys use the engine labels of YuGiOh Meta on each tournament deck (src/ygm_topdecks.json, same window as the meta lists);
    Duel Links uses Duel Links Meta's engines (src/engines_dlm.json) over the last 42 days of decks: a deck has the engine when it has at least half of the cards that identify it.
  * Which cards make it up: the sources only name the card that triggers each engine, so the package is measured. A card belongs to an engine when at least PACK_IN of the
    decks that play it include the card and it is at least PACK_LIFT points more common there than in the decks that do not (so a card every deck plays is not part of it).
    An engine is the small group of cards of an archetype that OTHER decks splash (Bystial, Horus, Sky Striker's Engage and Widow Anchor...), so the package is measured only in the
    decks that are not that archetype's own (home decks: the archetypes Meta relates to the engine, or whose name contains it). It needs at least 2 such cards and 5 splashing decks.
  * A label that names a single card and belongs to no archetype (Dominus Purge, Super Polymerization, The Fallen & The Virtuous...) is a staple, not an engine: an engine
    needs two or more identifying cards or an archetype of its own (relatedDeckTypes). Those labels go to the staples.
  * Staples: cards that PLAY at least STAPLE_IN of the decks of the mode. They are listed apart so they are not mistaken for an engine.
Everything is counted; the only prose is each card's own text."""
import collections, datetime, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_SHARE, MIN_DECKS, MAX_ENGINES = 1.5, 5, 28
DL_MIN_SHARE, DL_MIN_DECKS = 0.8, 3
PACK_IN, PACK_LIFT, MIN_PACK, MAX_PACK = 0.35, 0.25, 2, 8
LOOSE_IN, LOOSE_LIFT, MAX_LOOSE = 0.70, 0.50, 2   # a card with no archetype (King's Sarcophagus) has to be more specific to enter
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


def package(inside, outside, arch=None, arch_of=None, outside_host=None):
    """Cards that define an engine. inside / outside: lists of {card: copies} of the decks that splash it and of the ones that do not.
    arch / arch_of: the archetype of the engine and the archetype of each card: only the cards of that archetype enter (Bystial, Sky Striker...), plus cards with no archetype
    at all that are very specific to the engine (a Horus deck always has King's Sarcophagus): those are compared with the decks of the same host archetypes that do NOT play
    the engine, so what the host plays anyway (Pre-Preparation of Rites in a Mitsurugi deck) does not count. Cards of another archetype are the host deck's, not the engine's.
    Returns [(card, share of the engine decks that include it, average copies)], strongest first."""
    n_in, n_out = len(inside), max(len(outside), 1)
    c_in, c_out, c_host, copies = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter()
    n_host = len(outside_host or [])
    for d in inside:
        for k, v in d.items():
            c_in[k] += 1
            copies[k] += v
    for d in outside:
        for k in d:
            c_out[k] += 1
    for d in outside_host or []:
        for k in d:
            c_host[k] += 1
    rows = []
    for k, n in c_in.items():
        p_in, p_out = n / n_in, c_out[k] / n_out
        if arch_of is None:
            ok = p_in >= 0.5 and p_in - p_out >= 0.35
        else:
            a = arch_of.get(k)
            p_ref = c_host[k] / n_host if n_host >= 3 else p_out
            ok = (a == arch and p_in >= PACK_IN and p_in - p_out >= PACK_LIFT) or (a is None and p_in >= LOOSE_IN and p_in - max(p_out, p_ref) >= LOOSE_LIFT)
        if ok:
            rows.append((k, round(p_in * 100), round(copies[k] / n, 1), p_in - p_out, arch_of is not None and arch_of.get(k) is None))
    rows.sort(key=lambda r: (-r[3], -r[1], r[0]))
    out, loose = [], 0
    for r in rows:   # at most MAX_LOOSE cards with no archetype: they are the likeliest to belong to the host deck
        if r[4]:
            loose += 1
            if loose > MAX_LOOSE:
                continue
        out.append(r[:3])
    return out[:MAX_PACK]


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


def is_home(engine, deck_type, related=()):
    e, d = engine.lower(), deck_type.lower()
    return deck_type in related or e in d or d in e


def summarize(engine_decks, wins, archs, decks, text_of, min_share=MIN_SHARE, min_decks=MIN_DECKS, is_engine=lambda name: True, dtypes=None, related=None, arch_of=None, trig=None):
    """engine_decks: {engine name: [deck index]}; decks: list of {card: copies}; dtypes: archetype name of each deck; related: {engine: home archetypes}.
    Only the decks that splash the engine (not its home archetype) count."""
    total = len(decks) or 1
    out = []
    for name, idx in sorted(engine_decks.items(), key=lambda kv: -len(kv[1])):
        if dtypes is not None:
            idx = [i for i in idx if not is_home(name, dtypes[i], (related or {}).get(name, ()))]
        n = len(idx)
        share = n / total * 100
        if n < min_decks or share < min_share:
            continue
        if not is_engine(name):
            continue
        inside = [decks[i] for i in idx]
        have = set(idx)
        arch = None
        if arch_of is not None:
            votes = collections.Counter(arch_of[c] for c in (trig or {}).get(name, []) if c in arch_of)
            if not votes:
                continue
            arch = votes.most_common(1)[0][0]
        hosts = {dtypes[i] for i in idx} if dtypes is not None else set()
        pack = package(inside, [d for i, d in enumerate(decks) if i not in have], arch, arch_of,
                       [d for i, d in enumerate(decks) if i not in have and dtypes is not None and dtypes[i] in hosts])
        if len(pack) < MIN_PACK:
            continue
        central = next((c for c, *_ in pack if text_of(c)), pack[0][0])
        a = collections.Counter(dtypes[i] for i in idx).most_common() if dtypes is not None else archs[name].most_common()
        out.append({'n': name, 'decks': n, 'share': round(share, 1), 'wins': wins[name], 'archN': len(a), 'archs': [[x, c] for x, c in a[:5]],
                    'pack': [[c, p, k] for c, p, k in pack], 'central': central, 'txt': excerpt(text_of(central))})
    out.sort(key=lambda e: (-e['decks'], e['n']))
    return out[:MAX_ENGINES]


if __name__ == '__main__':
    os.chdir(ROOT)
    ygo = {c['name']: c['desc'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
    dltxt = {}
    for c in json.load(open('src/dl_text.json', encoding='utf-8')).values():
        dltxt.setdefault(c['name'], c.get('description'))
    text_of = lambda n: ygo.get(n) or dltxt.get(n) or ''
    arch_of = json.load(open('src/archetypes.json', encoding='utf-8'))
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
        dts = [d['deckType']['name'] for d in pool]
        rel = {nm: [r['name'] for r in ym_by[nm]['relatedDeckTypes']] for nm in ed}
        modes[key] = {'total': len(pool), 'window': win, 'engines': summarize(ed, wins, archs, cards, text_of, is_engine=is_eng, dtypes=dts, related=rel, arch_of=arch_of, trig={nm: [r['name'] for r in ym_by[nm]['requiredCards']] for nm in ed}), 'staples': staples(cards, text_of, lab)}
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
        dts = [d['deckType']['name'] for d in pool]
        rel = {e['name']: [r['name'] for r in e['relatedDeckTypes']] for e in dlm}
        modes[key] = {'total': len(pool), 'window': [start, end], 'engines': summarize(ed, wins, archs, cards, text_of, DL_MIN_SHARE, DL_MIN_DECKS, dtypes=dts, related=rel, arch_of=arch_of, trig=req), 'staples': staples(cards, text_of)}
    open('data/engines.js', 'w', encoding='utf-8').write('__load("engines",' + json.dumps({'modes': modes}, ensure_ascii=False, separators=(',', ':')) + ');')
    for k, v in modes.items():
        print(k, v['total'], 'engines', len(v['engines']), [(e['n'], len(e['pack'])) for e in v['engines'][:4]], '· staples', [s['n'] for s in v['staples'][:4]])
