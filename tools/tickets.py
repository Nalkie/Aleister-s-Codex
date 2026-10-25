"""What the exchange tickets can get -> data/tickets.js.  Run from the project root after tools/build_db.py:  python tools/tickets.py
  Dream UR / Dream SR (Speed Duel): UR / SR cards that come in a box released up to DREAM_SPEED_UNTIL
  Dream UR / Dream SR (Rush Duel):  same, Rush boxes up to DREAM_RUSH_UNTIL
  UR / SR / R tickets: cards that can be farmed (character levels, Gate drops, character decks, events, missions, Card Trader...)
                       released up to FARM_UNTIL; Speed and Rush apart
The cut-offs are the game's rule as given by the project owner, not something the sources publish: change them here when the game moves them.
The dates of the boxes come from Duel Links Meta (src/dl_sets.json), the sources of each card from src/dl_cards.json."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DREAM_SPEED_UNTIL = 'Predator of the Abyss'
DREAM_RUSH_UNTIL = 'Eternal Genesis'
FARM_UNTIL = '2026-05-11'
FARM_KINDS = ('characters', 'otherSources')


def build(sets, cards, names):
    box = {s['name']: s for s in sets}
    cut = {'speed': box[DREAM_SPEED_UNTIL]['release'][:10], 'rush': box[DREAM_RUSH_UNTIL]['release'][:10]}
    out = {'cuts': {'speedSet': DREAM_SPEED_UNTIL, 'speed': cut['speed'], 'rushSet': DREAM_RUSH_UNTIL, 'rush': cut['rush'], 'farm': FARM_UNTIL},
           'dream': {m: {'UR': [], 'SR': []} for m in ('speed', 'rush')}, 'farm': {m: {'UR': [], 'SR': [], 'R': []} for m in ('speed', 'rush')}}
    for c in sorted(cards, key=lambda c: (c.get('rel') or '', c['n']), reverse=True):
        n, r = c['n'], c.get('r')
        if n not in names or r not in ('UR', 'SR', 'R'):
            continue
        ob = c.get('ob') or []
        for mode in ('speed', 'rush'):
            if r in ('UR', 'SR') and any(o[0] == 'sets' and o[1] in box and bool(box[o[1]].get('rush')) == (mode == 'rush')
                                          and (box[o[1]].get('release') or '9')[:10] <= cut[mode] for o in ob):
                out['dream'][mode][r].append(n)
        mode = 'rush' if c.get('rush') else 'speed'
        if (c.get('rel') or '9') <= FARM_UNTIL and any(o[0] in FARM_KINDS for o in ob):
            out['farm'][mode][r].append(n)
    return out


if __name__ == '__main__':
    os.chdir(ROOT)
    idx = open('data/index.js', encoding='utf-8').read()
    names = {r[0] for r in json.loads(idx[idx.index(',') + 1:-2])['cards']}
    out = build(json.load(open('src/dl_sets.json', encoding='utf-8')), json.load(open('src/dl_cards.json', encoding='utf-8')), names)
    open('data/tickets.js', 'w', encoding='utf-8').write('__load("tickets",' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ');')
    print('data/tickets.js', {k: {m: {r: len(v) for r, v in d.items()} for m, d in out[k].items()} for k in ('dream', 'farm')})
