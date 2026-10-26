"""Engines in use per game mode -> data/engines.js.  Run from the project root after tools/ygm.py and tools/fetch_engines.py:  python tools/engines.py
TCG, OCG and Genesys: the engines YuGiOh Meta labels on each tournament deck (src/ygm_topdecks.json), same window as the meta lists.
Duel Links Speed and Rush: an engine is "in" a deck when the deck has at least half of the cards that identify it (Duel Links Meta's requiredCards), over the last 42 days of decks.
Per engine: decks that play it and their share of the mode, victories, the archetypes that use it, the cards that identify it and the effect of its central card.
Everything is counted; the only prose is the card's own text."""
import collections, datetime, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIN_SHARE, MIN_DECKS, MAX_ENGINES = 1.5, 5, 28
DL_MIN_SHARE, DL_MIN_DECKS = 0.8, 3   # Duel Links Meta defines few engines (mostly archetype families), so the bar is lower


def excerpt(text, limit=230):
    t = re.sub(r'\s+', ' ', (text or '').replace('●', '·')).strip()
    if len(t) <= limit:
        return t
    cut = t[:limit]
    i = max(cut.rfind('. '), cut.rfind('; '))
    return (cut[:i + 1] if i > 80 else cut.rsplit(' ', 1)[0] + '…')


def summarize(counter, wins, archs, total, engines_by_name, text_of, min_share=MIN_SHARE, min_decks=MIN_DECKS):
    out = []
    for name, n in counter.most_common():
        share = n / total * 100
        if n < min_decks or share < min_share:
            continue
        req = engines_by_name.get(name, [])
        central = next((c for c in req if text_of(c)), req[0] if req else None)
        a = archs[name].most_common()
        out.append({'n': name, 'decks': n, 'share': round(share, 1), 'wins': wins[name], 'archN': len(a), 'archs': [[x, c] for x, c in a[:5]],
                    'req': req[:4], 'central': central, 'txt': excerpt(text_of(central)) if central else ''})
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
    ygm = json.load(open('src/engines_ygm.json', encoding='utf-8'))
    ymeta = {e['_id']: e for e in ygm}
    by_name_y = {e['name']: [c['name'] for c in e['requiredCards']] for e in ygm}
    win = json.load(open('dl/ygmdata.json', encoding='utf-8'))['window']
    decks = [d for d in json.load(open('src/ygm_topdecks.json', encoding='utf-8')) if d.get('deckType') and not d.get('incomplete') and win[0] <= d['created'][:10] <= win[1]]
    modes = {}
    for key, flt in (('tcg', lambda d: not d.get('ocg') and not d.get('genesys')), ('ocg', lambda d: bool(d.get('ocg'))), ('gen', lambda d: bool(d.get('genesys')))):
        pool = [d for d in decks if flt(d)]
        cnt, wins, archs = collections.Counter(), collections.Counter(), collections.defaultdict(collections.Counter)
        for d in pool:
            for e in d.get('engines') or []:
                nm = ymeta[e]['name'] if e in ymeta else None
                if nm:
                    cnt[nm] += 1
                    wins[nm] += d.get('tournamentPlacement') == 1
                    archs[nm][d['deckType']['name']] += 1
        modes[key] = {'total': len(pool), 'window': win, 'engines': summarize(cnt, wins, archs, len(pool) or 1, by_name_y, text_of)}
    dlm = json.load(open('src/engines_dlm.json', encoding='utf-8'))
    by_name_d = {e['name']: [c['name'] for c in e['requiredCards']] for e in dlm if e['requiredCards']}
    dl = json.load(open('dl/topdecks.json', encoding='utf-8'))
    end = max(d['created'][:10] for d in dl)
    start = (datetime.date.fromisoformat(end) - datetime.timedelta(days=42)).isoformat()
    for key, rush in (('speed', False), ('rush', True)):
        pool = [d for d in dl if bool(d.get('rush')) == rush and d['created'][:10] >= start and d.get('deckType')]
        cnt, wins, archs = collections.Counter(), collections.Counter(), collections.defaultdict(collections.Counter)
        for d in pool:
            have = {c['card']['name'] for sec in ('main', 'extra', 'side') for c in d.get(sec, []) if isinstance(c.get('card'), dict)}
            for nm, req in by_name_d.items():
                if sum(r in have for r in req) >= max(1, -(-len(req) // 2)):   # at least half of the cards that identify it
                    cnt[nm] += 1
                    archs[nm][d['deckType']['name']] += 1
        modes[key] = {'total': len(pool), 'window': [start, end], 'engines': summarize(cnt, wins, archs, len(pool) or 1, by_name_d, text_of, DL_MIN_SHARE, DL_MIN_DECKS)}
    open('data/engines.js', 'w', encoding='utf-8').write('__load("engines",' + json.dumps({'modes': modes}, ensure_ascii=False, separators=(',', ':')) + ');')
    print({k: (v['total'], len(v['engines']), [e['n'] for e in v['engines'][:3]]) for k, v in modes.items()})
