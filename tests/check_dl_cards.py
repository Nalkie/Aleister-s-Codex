"""Gate test: Speed Duel and Rush Duel share 400+ card names with another rarity and other boxes, so dl/dldata.json keeps two tables (`cards` for Speed, `rcards` for Rush)
and the page reads the one of the format.  Sin red.  python tests/check_dl_cards.py"""
import collections, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


D = json.load(open('dl/dldata.json', encoding='utf-8'))
cards = json.load(open('src/dl_cards.json', encoding='utf-8'))
speed = {c['n']: c for c in cards if not c.get('rush') and not c['alt']}
rush = {c['n']: c for c in cards if c.get('rush') and not c['alt']}
shared = set(speed) & set(rush)
check(len(shared) > 100, '%d names exist in both Speed Duel and Rush Duel' % len(shared))
rnames = {r[0] for d in D['rush']['decks'].values() for sec in ('main', 'extra', 'side') for r in d['recipe'][sec]}
snames = {r[0] for d in D['speed']['decks'].values() for sec in ('main', 'extra', 'side') for r in d['recipe'][sec]}
check(all(n in D['rcards'] for n in rnames if n in rush), 'every card of a Rush recipe that is a Rush card has its Rush entry (%d recipe cards)' % len(rnames))
check(all(D['rcards'][n]['r'] == rush[n]['r'] for n in D['rcards'] if n in rush), 'the rarity of every Rush entry is the one of the Rush card')
both = [n for n in rnames & snames & shared]
check(both and all(D['rcards'][n]['r'] == rush[n]['r'] and D['cards'][n]['r'] == speed[n]['r'] for n in both), '%d names played in both formats keep each rarity apart' % len(both))
differ = [n for n in rnames & shared if rush[n]['r'] != speed[n]['r'] or rush[n]['rel'] != speed[n]['rel']]
check(differ and all(D['rcards'][n]['rel'] == rush[n]['rel'] and D['cards'][n]['rel'] == speed[n]['rel'] for n in differ), '%d Rush recipe cards differ from their Speed namesake in rarity or release date, and each table has its own' % len(differ))
dups = [(f, k, sec) for f in ('speed', 'rush') for k, d in D[f]['decks'].items() for sec in ('main', 'extra', 'side') if len({r[0] for r in d['recipe'][sec]}) != len(d['recipe'][sec])]
check(not dups, 'no recipe lists the same card twice (found: %s)' % dups[:3])
src = open('src.html', encoding='utf-8').read()
check('DLD.cards[' not in re.sub(r'function dlc\(.*?\n\}', '', src, flags=re.S).replace('DLD.cards[n]; sc=', ''), 'the page reads Duel Links cards through dlc(), which picks the table of the format')
print('failed:', len(fails))
sys.exit(1 if fails else 0)
