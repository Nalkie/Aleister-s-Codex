"""Gate test de la banlist y los tiers de Duel Links.  Sin red.  Run from the project root:  python tests/check_dl_legal.py

  * tools/dl_legal.py: Prohibida, Límite 1/2/3 compartidos entre Main, Extra y Side, tope de 3 copias, Rush con su propia lista,
    y los tiers por bandas de poder (límites inclusivos).
  * dl/dldata.json: ninguna receta publicada rompe la banlist vigente (src/dl_bans.json); el tier de cada mazo sale de su poder
    (dl/power.json) y no del tier editorial; Rush también tiene tiers.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import dl_legal as L

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


B = {('A', False): 3, ('B', False): 3, ('C', False): 3, ('D', False): 3, ('L1', False): 1, ('M1', False): 1, ('P', False): 2, ('Q', False): 2, ('X', False): 0,
     ('R', True): 1}

# --- reglas ---
check(L.violations({'A': 1, 'B': 1, 'C': 1}, B) == [], 'three Limited 3 cards in total is legal')
check(len(L.violations({'A': 2, 'B': 1, 'C': 1}, B)) == 1, 'four Limited 3 cards in total is not (the limit is shared, not per card)')
check(len(L.violations({'A': 3, 'B': 2}, B)) == 1, 'the old Snake-Eye recipe (Ash x3 + Oak x2, both Limited 3) is flagged')
check(L.violations({'L1': 1}, B) == [] and len(L.violations({'L1': 1, 'M1': 1}, B)) == 1, 'two different Limited 1 cards cannot be played together')
check(L.violations({'P': 2}, B) == [] and L.violations({'P': 1, 'Q': 1}, B) == [] and len(L.violations({'P': 2, 'Q': 1}, B)) == 1, 'Limited 2 allows two cards in total')
check(len(L.violations({'X': 1}, B)) == 1 and L.violations({'X': 0}, B) == [], 'a Forbidden card cannot be played')
check(len(L.violations({'Z': 4}, B)) == 1 and L.violations({'Z': 3}, B) == [], 'no card above 3 copies')
check(L.violations({'R': 1}, B, rush=False) == [] and L.violations({'R': 1, 'L1': 1}, B, rush=True) == [], 'Rush and Speed Duel have separate lists')
check(len(L.violations({'R': 1, 'R2': 1}, {('R', True): 1, ('R2', True): 1}, rush=True)) == 1, 'the Rush list also shares its limits')
check(L.deck_counts({'main': [['A', 2, 90]], 'extra': [['A', 1, 50], ['B', 1, 10]], 'side': []}) == {'A': 3, 'B': 1}, 'Main, Extra and Side count together')
check(L.api_deck_counts({'main': [{'card': {'name': 'A'}, 'amount': 2}], 'side': [{'card': {'name': 'A'}, 'amount': 1}]}) == {'A': 3}, 'the API deck shape is read the same way')

# --- tiers por poder ---
S, R = 'speed', 'rush'
check([L.tier_of(p, S) for p in (43.5, 27, 26.9, 17.5, 16, 15.9, 14, 6, 5.9, 0, None)] == [1, 1, 2, 2, 2, 3, 3, 3, None, None, None], 'Speed bands: 27 / 16 / 6 (lower bound inclusive)')
check([L.tier_of(p, R) for p in (20, 14, 12, 11.9, 7.5, 7, 6.5, 4, 3, 2.5, None)] == [1, 1, 1, 2, 2, 2, 3, 3, 3, None, None], 'Rush bands: 12 / 7 / 3 (lower bound inclusive)')

# --- datos publicados ---
bans = L.load_bans()
check(len(bans) > 200, 'the banlist loaded (' + str(len(bans)) + ' cards with a status)')
data = json.load(open('dl/dldata.json', encoding='utf-8'))
power = json.load(open('dl/power.json', encoding='utf-8'))
check(data.get('powerAsof') == power['asof'], 'dldata says which day the power ranking is from')
for fmt in ('speed', 'rush'):
    bad, wrong, nolegal = [], [], []
    for name, d in data[fmt]['decks'].items():
        v = L.violations(L.deck_counts(d['recipe']), bans, fmt == 'rush')
        if v:
            bad.append(name + ': ' + v[0])
        if d.get('tier') != L.tier_of(power[fmt].get(name), fmt) or d.get('power') != power[fmt].get(name):
            wrong.append(name)
        if not d.get('legal') or d['legal'] > d['n']:
            nolegal.append(name)
    check(not bad, fmt + ': every published recipe is legal under today\'s banlist' + ('' if not bad else ' -> ' + '; '.join(bad[:3])))
    check(not wrong, fmt + ': tier and power come from the power ranking' + ('' if not wrong else ' -> ' + ', '.join(wrong)))
    check(not nolegal, fmt + ': every deck reports how many of its lists are legal')
check(any(d['tier'] for d in data['rush']['decks'].values()), 'Rush has tiers too')
check(all(d['tier'] in (1, 2, 3, None) for f in ('speed', 'rush') for d in data[f]['decks'].values()), 'tiers are 1, 2, 3 or none')
top = [k for k, d in data['speed']['decks'].items() if d['tier'] == 1]
check(top and all(power['speed'][k] >= 27 for k in top), 'Speed tier 1 = at least 27 power points')

print('failed:', len(fails))
sys.exit(1 if fails else 0)
