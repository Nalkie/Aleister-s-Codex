"""Gate test for data/formats.js (Edison, Goat, HAT). Run from the project root after tools/formats.py: python tests/check_formats.py. Deterministic, no network."""
import json, sys
sys.path.insert(0, 'tools')
import formats

fails = []
def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

t = open('data/formats.js', encoding='utf-8').read()
d = json.loads(t[t.index(',') + 1:-2])
idx = open('data/index.js', encoding='utf-8').read()
names = [r[0] for r in json.loads(idx[idx.index(',') + 1:-2])['cards']]
src = json.load(open('src/formats.json', encoding='utf-8'))
F = d['formats']
count = lambda k, s: sum(1 for v in F[k]['ban'].values() if v == s)

check(d['order'] == ['ocg', 'md', 'edison', 'goat', 'hat'], 'formats: OCG, Master Duel, Edison, Goat, HAT')
check([F[k]['banlistName'] for k in d['order'][2:]] == ['March 2010', 'April 2005', 'April 2014'], 'banlists: March 2010, April 2005, April 2014')
check((count('ocg', 0), count('ocg', 1), count('ocg', 2)) == (93, 93, 13) and F['ocg']['ban'].get('Pot of Greed') == 0, 'OCG banlist from YGOPRODeck: 93 forbidden, 93 limited, 13 semi-limited (Pot of Greed forbidden)')
check([(count(k, 0), count(k, 1), count(k, 2)) for k in d['order'][2:]] == [(43, 70, 19), (17, 41, 15), (77, 71, 14)], 'banlist sizes (forbidden, limited, semi-limited): Edison 43/70/19, Goat 17/41/15, HAT 77/71/14')
check(all(n in names for k in F for n in F[k]['ban']), 'every banlist card resolves to a card of the page')
yb = src['goat']['ygoprodeckBan']
check({n for n, v in F['goat']['ban'].items() if v == 0} == set(yb['Forbidden']) and {n for n, v in F['goat']['ban'].items() if v == 1} == set(yb['Limited'])
      and {n for n, v in F['goat']['ban'].items() if v == 2} == set(yb['Semi-Limited']), 'Goat banlist is identical to YGOPRODeck (second, independent source)')
g = lambda k, n: F[k]['ban'].get(n)
check(g('goat', 'Chaos Emperor Dragon - Envoy of the End') == 0 and g('goat', 'Delinquent Duo') == 1 and g('goat', 'Confiscation') == 0, 'Goat: Chaos Emperor Dragon and Confiscation forbidden, Delinquent Duo limited (unbanned from forbidden)')
check(g('edison', 'Black Luster Soldier - Envoy of the Beginning') == 0 and g('edison', 'Mystical Space Typhoon') == 1 and g('edison', 'Brain Control') == 1, 'Edison: Black Luster Soldier forbidden, Mystical Space Typhoon and Brain Control limited')
pool = {k: {names[i] for i in F[k]['pool']} for k in F}
check(len(pool['goat']) == 1691 and len(pool['edison']) == 3662 and 5000 < len(pool['hat']) < 7000, f"pools: Goat {len(pool['goat'])}, Edison {len(pool['edison'])}, HAT {len(pool['hat'])}")
check(pool['goat'] < pool['edison'] and len(pool['edison'] - pool['hat']) <= 2 and len(pool['hat']) > len(pool['edison']), 'each format pool contains the one before it (Goat < Edison < HAT; one token of the API pool has no print date)')
check(all(n in pool[k] for k in F for n in F[k]['ban']), 'every banlisted card is in the pool of its format')
check('Blackwing - Gale the Whirlwind' in pool['edison'] and 'Blackwing - Gale the Whirlwind' not in pool['goat'], 'Blackwing - Gale the Whirlwind: legal in Edison, not in Goat')
ygo = json.load(open('src/ygo_all.json', encoding='utf-8'))
for k, flag in formats.FLAG.items():
    miss = sorted(c['name'] for c in ygo if flag in (c.get('formats') or []) and c['name'] in names and c['name'] not in pool[k])
    check(not miss, f'{k}: every card YGOPRODeck flags {flag} is in the pool ({miss[:3]})')
check('Blade Knight' in pool['goat'] and 'Blade Knight' in pool['edison'], 'Goat: Blade Knight is in the pool (the Goat pool endpoint omits it, the card flag has it)')
check('Traptrix Dionaea' in pool['hat'] and 'Traptrix Dionaea' not in pool['edison'], 'Traptrix Dionaea: legal in HAT, not in Edison')
check(all(len(F[k]['decks']) >= 5 and len(F[k]['events']) >= 3 for k in F if k not in ('ocg', 'md')), 'each retro format has popular decks and recent events')
check(13000 < len(pool['ocg']) < 15000 and len(pool['ocg']) < len(names), f"OCG pool: {len(pool['ocg'])} cards (cards of the TCG that are not out in the OCG are left out)")
out = formats.build(src, json.load(open('src/ygo_all.json', encoding='utf-8')), json.load(open('src/cardsets.json', encoding='utf-8')), names, json.load(open('src/md.json', encoding='utf-8')))
check(out == d, 'data/formats.js matches what tools/formats.py builds now')
print('failed:', len(fails)); sys.exit(1 if fails else 0)
