"""Gate test: every card the Yu-Gi-Oh! Wiki lists for an Anniversary Box is in that box on the page, and in the card's own detail. No network.
Run from the project root after tools/fandom_anniv.py:  python tests/check_anniversary.py"""
import json, os, re, sys
sys.path.insert(0, 'tools')
import fandom_anniv as fa

fails = []
def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

lists = json.load(open('src/fandom_anniversary.json', encoding='utf-8'))
names = [r[0] for r in fa.load('data/index.js')[1]['cards']]
sets_dl = fa.load('data/sets-dl.js')[1]
box = {s['n']: {names[k[0]] for k in s['k']} for s in sets_dl if s['kind'] == 'set'}
det = {}
for f in os.listdir('data'):
    if re.fullmatch(r'c\d+\.js', f):
        det.update(fa.load('data/' + f)[1])
check(len(lists) == 7, 'seven Anniversary boxes have a wiki list')
for nm, l in lists.items():
    miss = [n for n, _ in l if n not in box[nm]]
    check(not miss, f'{nm}: all {len(l)} wiki cards are in the box on the page' + (f' (missing {miss[:3]})' if miss else ''))
v4 = box['Anniversary Box Vol. 04']
check({'Shooting Quasar Dragon', 'Red-Eyes Dark Dragoon', 'Fusion Deployment', 'Polymerization'} <= v4, 'Vol. 04 has the extended and alternate artwork cards Duel Links Meta leaves out')
check(all(any(o[0] == 's' and o[1] == 'Anniversary Box Vol. 04' for o in det[n]['dl']['ob']) for n in ('Shooting Quasar Dragon', 'Polymerization')), "those cards list the box in their own 'how to get it'")
check(fa.parse('{{Set list|region=EN|\nA; Ultra Rare //description::(Alt)\nB (card); Super Rare\n}}') == [('A', 'Ultra Rare'), ('B', 'Super Rare')], 'the wiki list parser reads names and rarities and drops "(card)" and notes')
print('failed:', len(fails)); sys.exit(1 if fails else 0)
