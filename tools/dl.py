"""Duel Links meta step.

Reads dl/topdecks.json (latest top decks from the Duel Links Meta API) and src/dl_cards.json (every card
with its acquisition data) and writes dl/dldata.json:
  * per archetype: share of the recent sample, power ranking points and the tier of their band (dl/power.json,
    tools/dl_legal.py), wins and top 4s, a representative recipe and its cost. The recipe is the real recent deck
    closest to the average of the lists that are legal today: Forbidden and the shared Limited 1/2/3 groups of
    src/dl_bans.json are applied (the lists of the window were built under older banlists),
  * "outside the meta": archetypes without a tier and a small share that still won a tournament,
  * acquisition info (rarity, boxes, characters, other routes) for every card used.
Run from build/:  python tools/dl.py
"""
import collections, datetime, json, statistics

import dl_legal

WINDOW_DAYS = 36
MIN_DECKS = {'speed': 8, 'rush': 3}
OUTSIDE_SHARE = {'speed': 2.0, 'rush': 3.0}   # % of the sample below which a winner counts as "outside the meta"
PLACE_PTS = {'1st Place': 8, '2nd Place': 5, 'Top 4': 3, 'Top 8': 2}
WINS = {'1st Place'}
TOP4 = {'1st Place', '2nd Place', 'Top 4'}

decks = json.load(open('dl/topdecks.json', encoding='utf-8'))
BANS = dl_legal.load_bans()
POWER = json.load(open('dl/power.json', encoding='utf-8'))
dl_cards = json.load(open('src/dl_cards.json', encoding='utf-8'))
SET_REL = {x['name']: (x.get('release') or '')[:10] for x in json.load(open('src/dl_sets.json', encoding='utf-8'))}

asof = max(d['created'] for d in decks)[:10]
start = (datetime.date.fromisoformat(asof) - datetime.timedelta(days=WINDOW_DAYS)).isoformat()
recent = [d for d in decks if d['created'][:10] >= start and d.get('deckType')]
print('recent decks', len(recent), 'window', start, '->', asof)


def counts(d):
    c = {}
    for sec in ('main', 'extra', 'side'):
        for e in d.get(sec, []):
            k = (sec, e['card']['name'])
            c[k] = c.get(k, 0) + e['amount']
    return c


def event_of(d):
    t = (d.get('tournamentType') or {}).get('shortName') or (d.get('rankedType') or {}).get('shortName')
    name = d.get('customTournamentName')
    num = d.get('tournamentNumber')
    if name:
        return f'{name} #{num}' if num else name
    return t or 'torneo comunitario'


def author_of(d):
    a = d.get('author')
    return (a if isinstance(a, str) else (a or {}).get('username')) or 'Anónimo'


ART_PICK = {'Memento': 'Mementomictlan Tecuhtlica - Creation King', 'Centur-Ion': 'Centur-Ion Primera', 'Branded': 'Albion the Branded Dragon',
            'Vaalmonica': 'Vaalmonica, the Agathokakological Voice', 'Horus': 'Horus the Black Flame Deity', 'Snake-Eye': 'Snake-Eye Ash',
            'Shining Sarcophagus': 'Shining Sarcophagus', 'Dark Magician': 'Dark Magician', 'Stardust / Synchron': 'Stardust Dragon',
            'Mathmech': 'Mathmech Circular', 'HEROs': 'Elemental HERO Neos', 'Infernity': 'Infernity Launcher', 'Cyber Dragon': 'Cyber Dragon',
            'Destiny HEROs': 'Destiny HERO - Malicious', 'Rokket': 'Rokket Caliber', 'Swordsoul': 'Swordsoul of Mo Ye',
            'Marincess': 'Marincess Sea Horse', 'Labrynth': 'Lady Labrynth of the Silver Castle', 'Blackwings': 'Blackwing - Gale the Whirlwind',
            'Dark Magician: Rush!': 'Dark Magician'}
GENERIC = {'Droll & Lock Bird', 'Mulcharmy Fuwalos', 'Nibiru, the Primal Being', 'Forbidden Droplet', 'Hey, Trunade!', 'Lava Golem', 'Book of Eclipse',
           'Effect Veiler', 'D.D. Crow', 'I:P Masquerena', 'S:P Little Knight', 'Knightmare Phoenix', 'Underworld Goddess of the Closed World',
           'Super Starslayer TY-PHON - Sky Crisis', 'Photon Jumper', 'Soul Servant', 'Dark Magical Curtain', 'Infinite Impermanence',
           'Ghost Belle & Haunted Mansion', 'Number 90: Galaxy-Eyes Photon Lord', 'Lyrilusc - Assembled Nightingale', 'Powersink Stone',
           'Wightprincess', 'Bystial Druiswurm', 'Mulcharmy Purulia', 'Pot of Prosperity', 'Pot of Desires', 'Called by the Grave',
           'Crossout Designator', 'Nibiru, the Primal Being'}


def pick_art(tname, recipe):
    if tname in ART_PICK:
        return ART_PICK[tname]
    rows = [r for sec in ('main', 'extra') for r in recipe[sec] if r[0] not in GENERIC and r[2] >= 85]
    return rows[0][0] if rows else None


out = {'asof': asof, 'window': [start, asof], 'powerAsof': POWER['asof'], 'bands': {k: [list(b) for b in v] for k, v in dl_legal.POWER_BANDS.items()}, 'speed': {}, 'rush': {}}
names_used = set()
for fmt in ('speed', 'rush'):
    pool = [d for d in recent if bool(d.get('rush')) == (fmt == 'rush')]
    by = collections.defaultdict(list)
    for d in pool:
        by[d['deckType']['name']].append(d)
    total_pts = sum(PLACE_PTS.get(d.get('tournamentPlacement'), 0) for d in pool) or 1
    res = {'total': len(pool), 'decks': {}}
    for tname, ds in sorted(by.items(), key=lambda kv: -len(kv[1])):
        placed = [d for d in ds if d.get('tournamentPlacement')]
        wins = [d for d in placed if d['tournamentPlacement'] in WINS]
        top4 = [d for d in placed if d['tournamentPlacement'] in TOP4]
        share = len(ds) / len(pool) * 100
        power = POWER[fmt].get(tname)
        tier = dl_legal.tier_of(power, fmt)
        if len(ds) < MIN_DECKS[fmt] and not wins and tier is None:
            continue
        legal = [d for d in ds if not dl_legal.violations(dl_legal.api_deck_counts(d), BANS, fmt == 'rush')]
        if not legal:
            print('sin ninguna lista legal, se omite:', fmt, tname, len(ds))
            continue
        ds_all, ds = ds, legal   # the recipe and the card percentages come from the lists that are legal today
        cs = [counts(d) for d in ds]
        keys = set().union(*cs)
        avg = {k: sum(c.get(k, 0) for c in cs) / len(cs) for k in keys}
        best = min(range(len(ds)), key=lambda i: sum(abs(cs[i].get(k, 0) - avg[k]) for k in keys))
        m = ds[best]
        skills = collections.Counter((d.get('skill') or {}).get('name') for d in ds)
        sk, skn = skills.most_common(1)[0]
        pubs = collections.Counter(d['deckType'].get('tier') for d in ds_all if d['deckType'].get('tier'))
        pub_tier = pubs.most_common(1)[0][0] if pubs else None   # the editorial tier of Duel Links Meta, kept for reference
        pres = collections.Counter()
        for c in cs:
            for nm in {k[1] for k in c}:
                pres[nm] += 1
        recipe = {}
        for sec in ('main', 'extra', 'side'):
            rows = []
            for e in m.get(sec, []):
                nm = e['card']['name']
                rows.append([nm, e['amount'], round(pres[nm] / len(ds) * 100)])
                names_used.add(nm)
            recipe[sec] = rows
        gems = [d['gemsPrice'] for d in ds if d.get('gemsPrice') is not None]
        usd = [d['dollarsPrice'] for d in ds if d.get('dollarsPrice') is not None]
        last = max(wins, key=lambda d: d['created']) if wins else (max(top4, key=lambda d: d['created']) if top4 else None)
        res['decks'][tname] = {
            'n': len(ds_all), 'legal': len(ds), 'share': round(share, 1), 'tier': tier, 'power': power, 'pubTier': pub_tier,
            'wins': len(wins), 'top4': len(top4),
            'pts': round(sum(PLACE_PTS.get(d.get('tournamentPlacement'), 0) for d in ds_all) / total_pts * 100, 1),
            'last': ({'event': event_of(last), 'date': last['created'][:10], 'place': last['tournamentPlacement']} if last else None),
            'out': bool(wins) and tier is None and share < OUTSIDE_SHARE[fmt],
            'skill': sk, 'skillPct': round(skn / len(ds) * 100),
            'gemsMed': int(statistics.median(gems)) if gems else None,
            'usdMed': int(statistics.median(usd)) if usd else None,
            'who': {'author': author_of(m), 'date': m['created'][:10], 'event': event_of(m), 'place': m.get('tournamentPlacement'),
                    'url': m.get('url'), 'gems': m.get('gemsPrice'), 'usd': m.get('dollarsPrice'), 'skill': (m.get('skill') or {}).get('name')},
            'recipe': recipe, 'art': pick_art(tname, recipe),
        }
    out[fmt] = res

# acquisition info from the full Duel Links card list
by_name = {}
for c in dl_cards:
    if c['n'] not in by_name or (by_name[c['n']]['alt'] and not c['alt']):
        by_name[c['n']] = c
info = {}
for nm in sorted(names_used):
    c = by_name.get(nm)
    if not c:
        continue
    sets = [[o[1], o[2], o[3], SET_REL.get(o[1], '')] for o in c['ob'] if o[0] == 'sets']
    chars = [[o[1], o[3]] for o in c['ob'] if o[0] == 'characters']
    other = [[o[1], o[3]] for o in c['ob'] if o[0] == 'otherSources']
    info[nm] = {'r': c['r'], 'rel': c['rel'], 's': sets, 'c': chars, 'o': other}
out['cards'] = info
json.dump(out, open('dl/dldata.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
for fmt in ('speed', 'rush'):
    ds = out[fmt]['decks']
    print(fmt, 'sample', out[fmt]['total'], 'decks', len(ds), 'outside the meta:', [k for k, v in ds.items() if v['out']])
print('cards with info', len(info), 'of', len(names_used))
