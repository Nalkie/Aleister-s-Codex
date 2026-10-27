"""TCG and Genesys meta step.

Reads src/ygm_topdecks.json (tournament decks from the YuGiOh Meta API, tail of the list = newest) and writes
dl/ygmdata.json with, for the TCG and for Genesys:
  * usage share, wins and top 4s per archetype over the last WINDOW_DAYS days of data,
  * a computed tier (share of placement points: T1 >= 8%, T2 >= 4%, T3 >= 2%),
  * a representative recipe: the real recent deck closest to the archetype average (YuGiOh Meta prices included),
  * "outside the meta": archetypes below the tier line that still won a tournament.
Run from build/:  python tools/ygm.py
"""
import collections, datetime, json

WINDOW_DAYS = 42
PLACE_PTS = {1: 8, 2: 5, 3.5: 3, 8: 2, 16: 1}
TIER_LINES = [(8.0, 'T1'), (4.0, 'T2'), (2.0, 'T3')]
OUTSIDE_SHARE = 2.5       # % of decks
MIN_DECKS = {'tcg': 8, 'gen': 5, 'ocg': 8}
MAX_OUTSIDE = 24
PLACE_ES = {1: '1.º puesto', 2: '2.º puesto', 3.5: 'Top 4', 8: 'Top 8', 16: 'Top 16', 32: 'Top 32', 64: 'Top 64'}
# hand-picked flagship cards that read better than the automatic pick
ART_PICK = {'Elfnote': 'Elfnote Lucina', 'Blitzclique': 'Crackle Blitzclique', 'Kewl Tune': 'Kewl Tune Cue', 'Branded': 'Albion the Branded Dragon',
            'Dark Magician Chaos Ritual': 'Magician of Dark Chaos - Black Chaos', 'Chaos Ritual': 'Magician of Dark Chaos - Black Chaos',
            'Sacred Beast': 'Hamon, Lord of Striking Thunder', 'Invoked': 'Aleister the Invoker', 'Sky Striker': 'Sky Striker Ace - Raye',
            'Artmage': 'Artmage Power Patron', 'Chimera': 'Chimera the King of Phantom Beasts', 'Mitsurugi': 'Ame no Murakumo no Mitsurugi',
            'Angelechy': 'Angelechy Castellan'}

_k = json.load(open('src/konami_current.json', encoding='utf-8'))['from']      # dd/mm/yyyy: when the current TCG banlist took effect
BAN_DATE = '-'.join(reversed(_k.split('/')))
MIN_POST = 2        # the recipe comes from lists played under the current rules only when an archetype has at least this many
# when each format's current rules took effect: TCG banlist (Konami), OCG banlist (1 Oct 2026, OCG list), Genesys points (1st anniversary update, 5 Oct 2026)
REF = {'tcg': BAN_DATE, 'ocg': '2026-10-01', 'gen': '2026-10-05'}
decks = json.load(open('src/ygm_topdecks.json', encoding='utf-8'))
decks = [d for d in decks if d.get('deckType') and not d.get('incomplete')]
asof = max(d['created'] for d in decks)[:10]
start = (datetime.date.fromisoformat(asof) - datetime.timedelta(days=WINDOW_DAYS)).isoformat()
recent_all = [d for d in decks if d['created'][:10] >= start]
recent = [d for d in recent_all if not d.get('ocg')]
print('recent non-OCG decks', len(recent), 'OCG decks', len(recent_all) - len(recent), 'window', start, '->', asof)


def counts(d):
    c = {}
    for sec in ('main', 'extra', 'side'):
        for e in d.get(sec, []):
            k = (sec, e['card']['name'])
            c[k] = c.get(k, 0) + e['amount']
    return c


def price(d):
    return round(sum(e['amount'] * (e['card'].get('usdPrice') or 0) for sec in ('main', 'extra', 'side') for e in d.get(sec, [])))


def author_of(d):
    a = d.get('author')
    if isinstance(a, dict):          # algunos decks traen el jugador como objeto {_id, roles, username}
        a = a.get('username')
    return a or 'Anónimo'


def event_of(d):
    t = (d.get('tournamentType') or {}).get('shortName') or 'torneo'
    where = (d.get('tournamentLocation') or '').strip()
    custom = d.get('customTournamentName')
    if custom:
        return custom
    return f'{t} {where}'.strip() if where else t


def is_gen(d):
    return (d.get('tournamentType') or {}).get('shortName') == 'Genesys'


out = {'asof': asof, 'window': [start, asof]}
for fmt in ('tcg', 'gen', 'ocg'):
    pool = [d for d in recent_all if d.get('ocg')] if fmt == 'ocg' else [d for d in recent if is_gen(d) == (fmt == 'gen')]
    by = collections.defaultdict(list)
    for d in pool:
        by[d['deckType']['name']].append(d)
    total_pts = sum(PLACE_PTS.get(d.get('tournamentPlacement'), 0) for d in pool) or 1
    # cards that nearly every deck plays are not flagship material
    all_pres = collections.Counter()
    for d in pool:
        for nm in {k[1] for k in counts(d)}:
            all_pres[nm] += 1
    generic = {nm for nm, c in all_pres.items() if c / len(pool) > 0.2}
    cands = []
    for tname, ds in by.items():
        wins = [d for d in ds if d.get('tournamentPlacement') == 1]
        top4 = [d for d in ds if (d.get('tournamentPlacement') or 99) <= 3.5]
        pts = sum(PLACE_PTS.get(d.get('tournamentPlacement'), 0) for d in ds) / total_pts * 100
        share = len(ds) / len(pool) * 100
        tier = next((t for line, t in TIER_LINES if pts >= line), None)
        out_meta = bool(wins) and tier is None and share < OUTSIDE_SHARE
        if len(ds) < MIN_DECKS[fmt] and not out_meta:
            continue
        full = [d for d in ds if sum(e['amount'] for e in d.get('main', [])) >= 40]
        if not full:
            continue
        cs = [counts(d) for d in full]
        keys = set().union(*cs)
        avg = {k: sum(c.get(k, 0) for c in cs) / len(cs) for k in keys}
        post = [i for i, d in enumerate(full) if d['created'][:10] >= REF[fmt]]
        use = post if len(post) >= MIN_POST else list(range(len(full)))
        pavg = {k: sum(cs[i].get(k, 0) for i in use) / len(use) for k in keys}
        best = min(use, key=lambda i: sum(abs(cs[i].get(k, 0) - pavg[k]) for k in keys))
        m = full[best]
        pres = collections.Counter()
        for c in cs:
            for nm in {k[1] for k in c}:
                pres[nm] += 1
        recipe = {sec: [[e['card']['name'], e['amount'], round(pres[e['card']['name']] / len(full) * 100)] for e in m.get(sec, [])]
                  for sec in ('main', 'extra', 'side')}
        ordered = sorted(pres.items(), key=lambda kv: (-kv[1], kv[0]))
        key_cards = [[nm, round(c / len(full) * 100)] for nm, c in ordered if c / len(full) >= 0.4][:40]
        thematic = [[nm, p] for nm, p in key_cards if nm not in generic]
        art = ART_PICK.get(tname)
        if not art:
            art = next((nm for nm, p in thematic if p >= 70), (thematic or key_cards or [[None]])[0][0])
        last = max((wins or top4), key=lambda d: d['created']) if (wins or top4) else None
        cands.append((tname, {
            'n': len(ds), 'share': round(share, 1), 'pts': round(pts, 1), 'tier': tier, 'out': out_meta,
            'wins': len(wins), 'top4': len(top4), 'art': art, 'cards': key_cards, 'sample': len(full),
            'last': ({'event': event_of(last), 'date': last['created'][:10], 'place': PLACE_ES.get(last['tournamentPlacement'], '')} if last else None),
            'npost': len([d for d in ds if d['created'][:10] >= REF[fmt]]),
            'who': {'post': m['created'][:10] >= REF[fmt], 'author': author_of(m), 'date': m['created'][:10], 'event': event_of(m), 'place': PLACE_ES.get(m.get('tournamentPlacement'), ''),
                    'price': price(m)},
            'recipe': recipe}))
    ranked = [c for c in cands if not c[1]['out']]
    outside = sorted([c for c in cands if c[1]['out']], key=lambda c: (-c[1]['wins'], -c[1]['top4'], -c[1]['n']))[:MAX_OUTSIDE]
    out[fmt] = {'total': len(pool), 'ref': REF[fmt], 'decks': dict(sorted(ranked + outside, key=lambda c: -c[1]['n']))}
    print(fmt, 'sample', len(pool), 'ranked', len(ranked), 'outside the meta', len(outside))
    print('  tiers', {t: [k for k, v in out[fmt]['decks'].items() if v['tier'] == t] for t in ('T1', 'T2', 'T3')})
# the OCG goes to its own file: the page loads it only when its tab is opened (src/ygm_ocg.json is read by tools/formats_meta.py)
json.dump(out.pop('ocg'), open('src/ygm_ocg.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
json.dump(out, open('dl/ygmdata.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
