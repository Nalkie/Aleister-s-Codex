"""Metagame lists of the OCG and of the retro formats (Edison, Goat, HAT) in the same shape as the TCG and Genesys ones -> data/ygmx.js.
Run from the project root after tools/ygm.py, tools/fetch_formats_meta.py and tools/formats.py:  python tools/formats_meta.py
  ocg                 : src/ygm_ocg.json (tools/ygm.py: YuGiOh Meta decks of the last 42 days, same tiers as the TCG)
  edison, goat, hat   : src/formats_meta.json (Format Library events of the last 365 days: archetypes of every deck that played, top cut, deck lists)
Tier = share of the placement points (1st 8, 2nd 5, top 4 3, top 8 2): T1 >= 8%, T2 >= 4%, T3 >= 2%; "outside the meta" = won but under the tier line and 2.5% of the decks.
The deck list shown for an archetype is the real recent list closest to the archetype average."""
import collections, datetime, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import md as mdmod

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PTS = [(1, 8), (2, 5), (4, 3), (8, 2)]
TIER_LINES = [(8.0, 'T1'), (4.0, 'T2'), (2.0, 'T3')]
OUTSIDE_SHARE = 2.5
MIN_DECKS = 5
MAX_OUTSIDE = 12
SKIP = {'Other', 'Others', 'Unknown'}
PLACE_ES = {1: '1.º puesto', 2: '2.º puesto', 3: 'Top 4', 4: 'Top 4', 5: 'Top 8', 6: 'Top 8', 7: 'Top 8', 8: 'Top 8'}


def points(p):
    return next((v for lim, v in PTS if p <= lim), 0)


def parse_ydk(ydk, by_id):
    sec, out = 'main', {'main': collections.Counter(), 'extra': collections.Counter(), 'side': collections.Counter()}
    miss = 0
    for line in ydk.splitlines():
        line = line.strip()
        if line.startswith('#main'):
            sec = 'main'
        elif line.startswith('#extra'):
            sec = 'extra'
        elif line.startswith('!side'):
            sec = 'side'
        elif line.isdigit():
            nm = by_id.get(str(int(line)))
            if nm:
                out[sec][nm] += 1
            else:
                miss += 1
    return out, miss


def retro(meta, popular, by_id):
    """meta: {'events': {abbr: ev}, 'decks': {id: ydk}}; popular: formats.json decks (name + artwork ids)."""
    evs = sorted(meta['events'].values(), key=lambda e: e['d'])
    if not evs:
        return None
    end = evs[-1]['d']
    start = (datetime.date.fromisoformat(end) - datetime.timedelta(days=365)).isoformat()
    evs = [e for e in evs if e['d'] >= start]
    count, pts, wins, top4, last, lists = collections.Counter(), collections.Counter(), collections.Counter(), collections.Counter(), {}, collections.defaultdict(list)
    for e in evs:
        for tp, c in e['meta']:
            if tp not in SKIP:
                count[tp] += c
        for pl, tp, who, did in e['top']:
            pts[tp] += points(pl)
            if pl == 1:
                wins[tp] += 1
            if pl <= 4:
                top4[tp] += 1
                if tp not in last or e['d'] >= last[tp][1]['d']:
                    last[tp] = (pl, e)
            if str(did) in meta['decks'] and pl <= 8:
                lists[tp].append((e, pl, who, did))
    total, total_pts = sum(count.values()) or 1, sum(pts.values()) or 1
    art_of = {d['n']: d['art'] for d in popular}
    decks = {}
    for tp, n in count.items():
        share, p = n / total * 100, pts[tp] / total_pts * 100
        tier = next((t for line, t in TIER_LINES if p >= line), None)
        out = bool(wins[tp]) and tier is None and share < OUTSIDE_SHARE
        if (n < MIN_DECKS and not out) or not lists[tp]:
            continue
        parsed = []
        for e, pl, who, did in sorted(lists[tp], key=lambda x: (x[0]['d'], -x[1]), reverse=True):
            c, miss = parse_ydk(meta['decks'][str(did)], by_id)
            if sum(c['main'].values()) >= 30:
                parsed.append((e, pl, who, c))
        if not parsed:
            continue
        keys = set().union(*[set(c['main']) | set(c['extra']) | set(c['side']) for *_, c in parsed])
        flat = [{**{('main', k): v for k, v in c['main'].items()}, **{('extra', k): v for k, v in c['extra'].items()}, **{('side', k): v for k, v in c['side'].items()}} for *_, c in parsed]
        allk = set().union(*flat)
        avg = {k: sum(f.get(k, 0) for f in flat) / len(flat) for k in allk}
        best = min(range(len(parsed)), key=lambda i: sum(abs(flat[i].get(k, 0) - avg[k]) for k in allk))
        e, pl, who, c = parsed[best]
        pres = collections.Counter()
        for f in flat:
            for nm in {k[1] for k in f}:
                pres[nm] += 1
        pr = lambda nm: round(pres[nm] / len(parsed) * 100)
        recipe = {s: [[nm, k, pr(nm)] for nm, k in c[s].most_common()] for s in ('main', 'extra', 'side')}
        key_cards = [[nm, round(v / len(parsed) * 100)] for nm, v in sorted(pres.items(), key=lambda kv: (-kv[1], kv[0])) if v / len(parsed) >= 0.4][:40]
        art = by_id.get(str(int(art_of[tp][1]))) if tp in art_of and art_of[tp][1] else None
        art = art or next((nm for nm, p_ in key_cards if p_ >= 70), key_cards[0][0] if key_cards else None)
        lp = last.get(tp)
        decks[tp] = {'n': n, 'share': round(share, 1), 'pts': round(p, 1), 'tier': tier, 'out': out, 'wins': wins[tp], 'top4': top4[tp], 'art': art,
                     'cards': key_cards, 'sample': len(parsed),
                     'last': {'event': lp[1]['n'], 'date': lp[1]['d'], 'place': PLACE_ES.get(lp[0], '')} if lp else None,
                     'who': {'author': who or 'Anónimo', 'date': e['d'], 'event': e['n'], 'place': PLACE_ES.get(pl, ''), 'price': None}, 'recipe': recipe}
    ranked = {k: v for k, v in decks.items() if not v['out']}
    outside = dict(sorted(((k, v) for k, v in decks.items() if v['out']), key=lambda kv: (-kv[1]['wins'], -kv[1]['top4'], -kv[1]['n']))[:MAX_OUTSIDE])
    return {'total': total, 'window': [start, end], 'events': len(evs), 'decks': dict(sorted({**ranked, **outside}.items(), key=lambda kv: -kv[1]['n']))}


def ocg_events(events, tops, since='2026-08-20'):
    """OCG tournaments with their top 8, in the shape of data/events.js (TCG and Genesys) so the page lists them the same way."""
    by = collections.defaultdict(list)
    for d in tops:
        ev = d.get('event') or {}
        if ev.get('_id') and d.get('ocg') and isinstance(d.get('tournamentPlacement'), int) and d['tournamentPlacement'] <= 8:
            who = d['author'] if isinstance(d.get('author'), str) else (d.get('author') or {}).get('username')
            by[ev['_id']].append([d['tournamentPlacement'], who or '?', (d.get('deckType') or {}).get('name') or '?', d.get('url') or ''])
    out = [{'n': e['name'], 'd': e['date'][:10], 'f': 'OCG', 'c': e.get('country') or '', 'p': e.get('playerCount') or 0, 'ty': (e.get('tournamentType') or {}).get('name') or '',
            'top': sorted(by.get(e['_id'], []), key=lambda x: x[0])}
           for e in events if e.get('format') == 'OCG' and e['date'] >= since and 'Test Event' not in e['name']]
    out.sort(key=lambda x: (x['d'], x['p']), reverse=True)
    return out


if __name__ == '__main__':
    os.chdir(ROOT)
    ygo = json.load(open('src/ygo_all.json', encoding='utf-8'))
    by_id = {str(int(c['id'])): c['name'] for c in ygo}
    fm = json.load(open('src/formats.json', encoding='utf-8'))
    fmeta = json.load(open('src/formats_meta.json', encoding='utf-8'))
    out = {'ocg': json.load(open('src/ygm_ocg.json', encoding='utf-8'))}
    ymd = json.load(open('dl/ygmdata.json', encoding='utf-8'))
    out['ocg']['window'] = ymd['window']
    for k in ('edison', 'goat', 'hat'):
        out[k] = retro(fmeta[k], fm[k]['decks'], by_id)
    md_src, md_res = json.load(open('src/md.json', encoding='utf-8')), mdmod.resolver(c['name'] for c in ygo)
    out['md'] = mdmod.meta(md_src, md_res, mdmod.ban_state(md_src, md_res)[0])
    out['ocgEvents'] = ocg_events(json.load(open('src/ygm_events.json', encoding='utf-8')), json.load(open('src/ygm_topdecks.json', encoding='utf-8')))
    open('data/ygmx.js', 'w', encoding='utf-8').write('__load("ygmx",' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ');')
    print('data/ygmx.js', {k: ((v['total'], len(v['decks']), v.get('events')) if isinstance(v, dict) else len(v)) for k, v in out.items() if v})
