"""Master Duel: banlist, card pool and metagame -> the same shapes the OCG and the retro formats use (data/formats.js and data/ygmx.js).
Reads src/md.json (tools/fetch_md.py, Master Duel Meta). Pure functions, no network; tools/formats.py and tools/formats_meta.py call them.

Names: Master Duel Meta spells Maliss cards "Maliss P Chessy Cat" and the card database "Maliss <P> Chessy Cat"; resolve() maps one to the other.
A card the database does not have yet (a Master Duel exclusive, or a card newer than ygo_all.json) cannot be drawn by the page, so it is left out
of the pool and of the lists, and counted in `dropped` (tests/check_md.py fails if that is more than 1% of the copies).

Metagame (sample = decks that count for the stats, last 42 days):
  * ranked ladder decks whose rank counts in the stats (includeInStats) weigh 1 point each
  * tournament decks weigh by placement: 1st 8, 2nd 5, Top 4 3, Top 8 and Top 10 2, Top 16 1.5, Top 100 1; tournaments Master Duel Meta gives weight 0 are out
  * tier = share of the points: T1 >= 8%, T2 >= 4%, T3 >= 2% (the same lines as every other format); "outside the meta" = won a tournament
    but under the tier line and under 2.5% of the decks. The list shown for a deck type is the real list closest to the type's average."""
import collections, re

TIER_LINES = [(8.0, 'T1'), (4.0, 'T2'), (2.0, 'T3')]
OUTSIDE_SHARE = 2.5
MIN_DECKS = 5
MAX_OUTSIDE = 12
PLACE_PTS = {'1st Place': 8, '2nd Place': 5, 'Top 4': 3, 'Top 8': 2, 'Top 10': 2, 'Top 16': 1.5, 'Top 100': 1}
PLACE_ES = {'1st Place': '1.º puesto', '2nd Place': '2.º puesto', 'Top 4': 'Top 4', 'Top 8': 'Top 8', 'Top 10': 'Top 10', 'Top 16': 'Top 16', 'Top 100': 'Top 100'}
BRACKETS = re.compile(r'[<>]')


def resolver(names):
    """names: card names of the database -> function(md_name) -> database name or None."""
    have = set(names)
    canon = {BRACKETS.sub('', n): n for n in have if BRACKETS.search(n)}
    return lambda n: n if n in have else canon.get(n)


def counted(d):
    """Does this deck count for the stats, and how many points is it worth?  -> points or None."""
    if d['tour']:
        w = d['tour'].get('statsWeight')
        return None if w == 0 else PLACE_PTS.get(d['place'])
    r = d['ranked']
    return 1 if r and r.get('includeInStats') and (r.get('statsWeight') or 0) > 0 else None


def lists(d, res):
    """The deck as {section: Counter of database names} and how many copies had no database card."""
    out, drop = {}, 0
    for s in ('main', 'extra', 'side'):
        c = collections.Counter()
        for n, k in d[s]:
            r = res(n)
            if r:
                c[r] += k
            else:
                drop += k
        out[s] = c
    return out, drop


def where(d):
    return d['tour']['name'] if d['tour'] else 'Ladder · ' + d['ranked']['name']


def meta(md, res):
    """The metagame of Master Duel in the shape of data/ygmx.js entries: {total, window, decks: {type: {...}}}, plus `dropped` copies."""
    sample = [(d, counted(d)) for d in md['decks'] if d['type']]
    sample = [(d, p) for d, p in sample if p is not None]
    count, pts, wins, top4, bytype = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), collections.defaultdict(list)
    for d, p in sample:
        count[d['type']] += 1
        pts[d['type']] += p
        if d['place'] == '1st Place':
            wins[d['type']] += 1
        if d['place'] in ('1st Place', '2nd Place', 'Top 4'):
            top4[d['type']] += 1
        bytype[d['type']].append((d, p))
    total, total_pts = sum(count.values()) or 1, sum(pts.values()) or 1
    parsed_by, gpres = {}, collections.Counter()
    dropped = copies = 0
    for tp in count:
        parsed_by[tp] = []
        for d, _ in sorted(bytype[tp], key=lambda x: (x[0]['d'], x[1]), reverse=True):
            c, drop = lists(d, res)
            dropped += drop
            copies += sum(k for s in ('main', 'extra', 'side') for _, k in d[s])
            if sum(c['main'].values()) >= 40:
                parsed_by[tp].append((d, c))
                for nm in set(c['main']) | set(c['extra']) | set(c['side']):
                    gpres[nm] += 1
    n_parsed = sum(len(v) for v in parsed_by.values()) or 1
    decks = {}
    for tp, n in count.items():
        share, p_share = n / total * 100, pts[tp] / total_pts * 100
        tier = next((t for line, t in TIER_LINES if p_share >= line), None)
        out = bool(wins[tp]) and tier is None and share < OUTSIDE_SHARE
        parsed = parsed_by[tp]
        if (n < MIN_DECKS and not out) or not parsed:
            continue
        flat = [{**{('main', k): v for k, v in c['main'].items()}, **{('extra', k): v for k, v in c['extra'].items()}, **{('side', k): v for k, v in c['side'].items()}} for _, c in parsed]
        allk = set().union(*flat)
        avg = {k: sum(f.get(k, 0) for f in flat) / len(flat) for k in allk}
        best = min(range(len(parsed)), key=lambda i: sum(abs(flat[i].get(k, 0) - avg[k]) for k in allk))
        d, c = parsed[best]
        pres = collections.Counter()
        for f in flat:
            for nm in {k[1] for k in f}:
                pres[nm] += 1
        pr = lambda nm: round(pres[nm] / len(parsed) * 100)
        recipe = {s: [[nm, k, pr(nm)] for nm, k in c[s].most_common()] for s in ('main', 'extra', 'side')}
        key_cards = [[nm, round(v / len(parsed) * 100)] for nm, v in sorted(pres.items(), key=lambda kv: (-kv[1], kv[0])) if v / len(parsed) >= 0.4][:40]
        # the picture of the deck: the card Master Duel Meta shows for the type; else, among the cards it nearly always plays, the one least played by the other decks (not Ash Blossom)
        core = [(nm, p_) for nm, p_ in key_cards if p_ >= 60]
        art = res(md.get('art', {}).get(tp) or '') or min(core, key=lambda x: (gpres[x[0]] - pres[x[0]], -x[1], x[0]))[0] if core else (key_cards[0][0] if key_cards else None)
        top = [x for x in bytype[tp] if x[0]['place'] in ('1st Place', '2nd Place', 'Top 4')]
        lp = max(top, key=lambda x: (x[0]['d'], x[1]))[0] if top else None
        decks[tp] = {'n': n, 'share': round(share, 1), 'pts': round(p_share, 1), 'tier': tier, 'out': out, 'wins': wins[tp], 'top4': top4[tp], 'art': art,
                     'cards': key_cards, 'sample': len(parsed),
                     'last': {'event': where(lp), 'date': lp['d'], 'place': PLACE_ES.get(lp['place'], '')} if lp else None,
                     'who': {'author': d['who'] or 'Anónimo', 'date': d['d'], 'event': where(d), 'place': PLACE_ES.get(d['place'], ''), 'price': None}, 'recipe': recipe}
    ranked = {k: v for k, v in decks.items() if not v['out']}
    outside = dict(sorted(((k, v) for k, v in decks.items() if v['out']), key=lambda kv: (-kv[1]['wins'], -kv[1]['top4'], -kv[1]['n']))[:MAX_OUTSIDE])
    return {'total': total, 'window': md['window'], 'decks': dict(sorted({**ranked, **outside}.items(), key=lambda kv: -kv[1]['n'])),
            'dropped': {'copies': dropped, 'of': copies}}


STATUS = {'Forbidden': 0, 'Limited': 1, 'SemiLimited': 2}


def format_entry(md, res, pos):
    """The data/formats.js entry of Master Duel (same shape as the OCG one): its own banlist and the cards that exist in the game."""
    ban = {}
    for s, lst in md['ban'].items():
        for n in lst:
            r = res(n)
            if r:
                ban[r] = STATUS[s]
    pool = sorted({pos[r] for r in map(res, md['pool']) if r and r in pos})
    return {'name': 'Master Duel', 'date': None, 'banlistName': 'vigente', 'event': '', 'source': '', 'poolHow': 'api', 'ban': ban, 'removed': [], 'pool': pool,
            'decks': [], 'events': []}
