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
NAME_FIX = {'Mitsrurugi': 'Mitsurugi'}      # YuGiOh Meta misspells the engine label; the archetype and the cards are spelled Mitsurugi
MIN_SHARE, MIN_DECKS, MAX_ENGINES = 1.5, 5, 60
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
                                'pack': [[c, p, k, excerpt(text_of(c), 170)] for c, p, k in pack], 'central': central, 'txt': excerpt(text_of(central))})
    out.sort(key=lambda e: (-e['decks'], e['n']))
    return out[:MAX_ENGINES]


def label_rows(ed, cards, dts, pls, text_of, arch_of, trig, related, is_engine):
    """One row for EVERY engine the sources define (YuGiOh Meta / Duel Links Meta) that at least one deck plays. The package is the card(s) that identify it plus the cards of its
    archetype that most of its decks play. splash = decks that are not the engine's own archetype."""
    out = []
    for name, idx in ed.items():
        if not idx or not is_engine(name) or name in NOT_ENGINES:
            continue
        t = [c for c in trig.get(name, []) if c in arch_of or True]
        votes = collections.Counter(arch_of[c] for c in t if c in arch_of)
        arch = votes.most_common(1)[0][0] if votes else None
        members = {c for c, a in arch_of.items() if a == arch} if arch else set()
        row = engine_row(name, idx, cards, dts, pls, text_of, t, members)
        if len(row['pack']) < MIN_PACK:
            continue
        row['share'] = round(len(idx) / (len(cards) or 1) * 100, 1)
        row['splash'] = sum(1 for i in idx if not is_home(name, dts[i], (related or {}).get(name, ())))
        out.append(row)
    return out


CURATED = [   # engines asked for by name: the cards that identify them and the archetype their other cards come from; need = cards a deck must have to count
    {'n': 'The Fallen & The Virtuous', 'cards': ['The Fallen & The Virtuous', 'Albion the Branded Dragon', 'Ecclesia and the Dark Dragon'], 'need': 2},
    {'n': 'Bystial', 'arch': 'Bystial', 'cards': ['Bystial Magnamhut', 'Bystial Druiswurm', 'Bystial Baldrake'], 'need': 2},
    {'n': 'Ars Magna', 'arch': 'Ars Magna', 'cards': [], 'need': 1},
    {'n': 'K9', 'arch': 'K9', 'cards': [], 'need': 2},
    {'n': 'Kashtira', 'arch': 'Kashtira', 'cards': [], 'need': 2},
    {'n': 'Sinful Spoils', 'arch': 'Sinful Spoils', 'cards': ['Diabellstar the Black Witch', 'WANTED: Seeker of Sinful Spoils'], 'need': 2, 'replaces': ['Diabellestar', 'Diabellstar']},
]
NOT_ENGINES = {'Dominus Purge', 'Dominus Impulse', 'Dominus Spark', 'Dominusteer Rosepamela', 'Super Polymerization', 'Synchro Emergency', 'Fidraulis Harmonia'}   # single cards that every source labels as an engine but that are staples
MINE_STAPLE, MINE_MIN_DECKS, MINE_MIN_ARCH, MINE_TOP = 0.30, 5, 2, 0.75


def engine_row(name, idx, cards, dts, pls, text_of, order, members):
    """One engine: decks (indexes) that play it, with its cards (explicit ones first, then the measured ones of its archetype)."""
    n_in = len(idx) or 1
    c_in, copies = collections.Counter(), collections.Counter()
    for i in idx:
        for k, v in cards[i].items():
            c_in[k] += 1
            copies[k] += v
    pack = [k for k in order if c_in[k]]
    extra = sorted((k for k in members if k not in pack and c_in[k] / n_in >= PACK_IN), key=lambda k: (-c_in[k], k))
    pack = (pack + extra)[:MAX_PACK]
    a = collections.Counter(dts[i] for i in idx).most_common()
    central = next((c for c in pack if text_of(c)), pack[0] if pack else None)
    return {'n': name, 'decks': len(idx), 'wins': sum(1 for i in idx if pls[i] == 1), 'archN': len(a), 'archs': [[x, c] for x, c in a[:5]],
            'pack': [[c, round(c_in[c] / n_in * 100), round(copies[c] / c_in[c], 1), excerpt(text_of(c), 170)] for c in pack], 'central': central, 'txt': excerpt(text_of(central)) if central else ''}


def curated_engines(cards, dts, pls, text_of, arch_of):
    out = []
    for spec in CURATED:
        members = set(spec['cards']) | {c for c, a in arch_of.items() if a == spec.get('arch')}
        idx = [i for i, s in enumerate(cards) if sum(c in s for c in members) >= spec['need']]
        row = engine_row(spec['n'], idx, cards, dts, pls, text_of, spec['cards'], members)
        row['share'] = round(len(idx) / (len(cards) or 1) * 100, 1)
        row['replaces'] = spec.get('replaces', [])
        row['splash'] = len(idx)
        out.append(row)
    return out


def mined_engines(cards, dts, pls, text_of, arch_of, label_of):
    """Groups of 2-8 cards that appear together (each in 60%+ of the decks of the other) in many archetypes: engines nobody named yet."""
    n = len(cards) or 1
    cnt = collections.Counter(c for s in cards for c in s)
    staple = {c for c, v in cnt.items() if v / n >= MINE_STAPLE}
    where = collections.defaultdict(set)
    for i, s in enumerate(cards):
        for c in s:
            if c not in staple and cnt[c] >= MINE_MIN_DECKS:
                where[c].add(i)
    cs = sorted(where, key=lambda c: (-len(where[c]), c))
    adj = collections.defaultdict(set)
    for a in range(len(cs)):
        A = where[cs[a]]
        for b in range(a + 1, len(cs)):
            B = where[cs[b]]
            k = len(A & B)
            if k >= 4 and k / len(A) >= 0.6 and k / len(B) >= 0.6:
                adj[cs[a]].add(cs[b])
                adj[cs[b]].add(cs[a])
    seen, groups = set(), []
    for c in cs:
        if c in seen or c not in adj:
            continue
        stack, comp = [c], []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            comp.append(x)
            stack += sorted(adj[x] - seen)
        groups.append(sorted(comp, key=lambda c: (-len(where[c]), c))[:MAX_PACK])
    out = []
    for g in groups:
        arch = collections.Counter(arch_of[c] for c in g if c in arch_of)
        top = arch.most_common(1)
        name = top[0][0] if top and top[0][1] >= 2 and top[0][1] * 2 >= sum(arch.values()) else next((label_of[c] for c in g if c in label_of), None)
        if not name or name in NOT_ENGINES:
            continue
        need = max(2, round(len(g) * 0.6))
        idx = [i for i, s in enumerate(cards) if sum(c in s for c in g) >= need]
        row = engine_row(name, idx, cards, dts, pls, text_of, g, set())
        share_top = row['archs'][0][1] / len(idx) if idx else 1
        if len(idx) >= MINE_MIN_DECKS and row['archN'] >= MINE_MIN_ARCH and share_top <= MINE_TOP:
            row['share'] = round(len(idx) / n * 100, 1)
            row['splash'] = len(idx)
            out.append(row)
    return out


def merge(label_engines, curated, mined, limit=MAX_ENGINES):
    """Curated first, then every engine of the sources, then the mined groups; an engine that shares half its cards with one already kept is dropped.
    Returns (main list: 5+ decks and 1%+ of the mode, more: every other engine that at least one deck plays, with its real count)."""
    replaced = {r for c in curated for r in c.get('replaces', [])}
    kept = [c for c in curated if c['decks'] > 0]
    for e in sorted([e for e in label_engines if e['n'] not in replaced], key=lambda e: -e['decks']) + sorted(mined, key=lambda e: -e['decks']):
        cs = {c for c, *_ in e['pack']}
        if any(len(cs & {c for c, *_ in k['pack']}) * 2 >= min(len(cs), len(k['pack'])) for k in kept) or any(k['n'].lower() == e['n'].lower() for k in kept):
            continue
        kept.append(e)
    for e in kept:
        e.pop('replaces', None)
    kept.sort(key=lambda e: (-e['decks'], e['n']))
    main = [e for e in kept if e['decks'] >= MIN_DECKS and e['share'] >= 1.0][:limit]
    names = {e['n'] for e in main}
    more = [e for e in kept if e['n'] not in names]
    absent = [{'n': c['n'], 'decks': 0, 'share': 0.0, 'pack': [], 'archs': [], 'archN': 0, 'wins': 0, 'splash': 0} for c in curated if c['decks'] == 0]
    return main, more + absent

if __name__ == '__main__':
    os.chdir(ROOT)
    ygo = {c['name']: c['desc'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
    dltxt = {}
    for c in json.load(open('src/dl_text.json', encoding='utf-8')).values():
        dltxt.setdefault(c['name'], c.get('description'))
    text_of = lambda n: ygo.get(n) or dltxt.get(n) or ''
    arch_of = json.load(open('src/archetypes.json', encoding='utf-8'))
    ymeta = {e['_id']: e for e in json.load(open('src/engines_ygm.json', encoding='utf-8'))}
    for e in ymeta.values():
        e['name'] = NAME_FIX.get(e['name'], e['name'])
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
        pls = [d.get('tournamentPlacement') for d in pool]
        label_of = {r['name']: nm for nm in ym_by for r in ym_by[nm]['requiredCards']}
        trig = {nm: [r['name'] for r in ym_by[nm]['requiredCards']] for nm in ym_by}
        base = label_rows(ed, cards, dts, pls, text_of, arch_of, trig, {nm: [r['name'] for r in ym_by[nm]['relatedDeckTypes']] for nm in ym_by}, is_eng)
        eng, more = merge(base, curated_engines(cards, dts, pls, text_of, arch_of), mined_engines(cards, dts, pls, text_of, arch_of, label_of))
        modes[key] = {'total': len(pool), 'window': win, 'engines': eng, 'more': more, 'staples': staples(cards, text_of, lab)}
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
                if sum(x in cards[i] for x in r) >= max(1, -(-len(r) // 2)):   # at least half of the cards that identify it
                    ed[nm].append(i)
                    archs[nm][d['deckType']['name']] += 1
        dts = [d['deckType']['name'] for d in pool]
        rel = {e['name']: [r['name'] for r in e['relatedDeckTypes']] for e in dlm}
        pls = [None] * len(pool)
        base = label_rows(ed, cards, dts, pls, text_of, arch_of, req, rel, lambda nm: True)
        eng, more = merge(base, curated_engines(cards, dts, pls, text_of, arch_of), mined_engines(cards, dts, pls, text_of, arch_of, {}))
        modes[key] = {'total': len(pool), 'window': [start, end], 'engines': eng, 'more': more, 'staples': staples(cards, text_of)}
    open('data/engines.js', 'w', encoding='utf-8').write('__load("engines",' + json.dumps({'modes': modes}, ensure_ascii=False, separators=(',', ':')) + ');')
    for k, v in modes.items():
        print(k, v['total'], 'engines', len(v['engines']), [(e['n'], len(e['pack'])) for e in v['engines'][:4]], '· staples', [s['n'] for s in v['staples'][:4]])
