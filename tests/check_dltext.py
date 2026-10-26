"""Gate test: every card that is in Duel Links (Speed or Rush) has effect text, a type line and, for monsters, stats. No network.
Run from the project root after tools/dltext.py:  python tests/check_dltext.py"""
import json, os, re, sys
sys.path.insert(0, 'tools')
import dltext

fails = []
def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

det = {}
for f in os.listdir('data'):
    if re.fullmatch(r'c\d+\.js', f):
        t = open('data/' + f, encoding='utf-8').read()
        det.update(json.loads(t[t.index(',') + 1:-2]))
dl = {n: v for n, v in det.items() if v.get('dl')}
rush = {n: v for n, v in dl.items() if v['dl'].get('rush')}
check(len(dl) > 10000 and len(rush) > 2500, f'{len(dl)} Duel Links cards, {len(rush)} of them Rush')
check(not [n for n, v in dl.items() if not (v.get('d') or '').strip()], 'every Duel Links card has effect text')
check(not [n for n, v in dl.items() if not v.get('ty')], 'every Duel Links card has a type line')
mons = [v for v in dl.values() if 'Monster' in (v.get('ty') or '')]
check(all(v.get('st') and v['st'][3] and v['st'][4] for v in mons), f'{len(mons)} monsters have type and attribute')
check(not [n for n, v in rush.items() if re.search(r'null|undefined', v.get('d') or '') or (v.get('d') or '').strip() in ('None', 'null')], 'no Rush text is null or undefined ("[REQUIREMENT] None" is real Rush wording)')
check(det['Spell Archer']['ty'] == 'Normal Monster' and det['Spell Archer']['st'][:3] == [1000, 400, 3], 'Spell Archer (Rush): Normal Monster, 1000 / 400, level 3')
check(dltext.type_line({'type': 'Monster', 'monsterType': ['Fusion', 'Effect']}) == 'Fusion Monster' and dltext.type_line({'type': 'Spell', 'race': 'Quick-Play'}) == 'Quick-Play Spell', 'type lines follow YGOPRODeck wording')
src = json.load(open('src/dl_cards.json', encoding='utf-8')); texts = json.load(open('src/dl_text.json', encoding='utf-8'))
check(dltext.apply({'X': {'dl': {'rush': True}}}, [{'id': 'a', 'n': 'X', 'rush': True}], {'a': {'description': 'hi\r\nthere', 'type': 'Spell', 'race': 'Normal'}}) == 1, 'apply fills a Duel Links card that has text')
print('failed:', len(fails)); sys.exit(1 if fails else 0)
