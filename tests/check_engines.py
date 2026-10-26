"""Gate test for data/engines.js (engines per game mode). Deterministic, no network. Run from the project root after tools/engines.py:  python tests/check_engines.py"""
import collections, json, sys
sys.path.insert(0, 'tools')
import engines

fails = []
def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c: fails.append(m)

t = open('data/engines.js', encoding='utf-8').read()
M = json.loads(t[t.index(',') + 1:-2])['modes']
check(list(M) == ['tcg', 'ocg', 'gen', 'speed', 'rush'], 'modes: TCG, OCG, Genesys, Duel Links Speed and Rush')
check(all(len(M[k]['engines']) >= 10 for k in ('tcg', 'ocg', 'gen')) or len(M['gen']['engines']) >= 8, 'TCG and OCG list 10+ engines, Genesys 8+')
check(all(e['decks'] <= M[k]['total'] and abs(e['share'] - e['decks'] / M[k]['total'] * 100) < 0.06 for k in M for e in M[k]['engines']), 'every engine share is its decks over the decks of the mode')
check(all(M[k]['engines'] == sorted(M[k]['engines'], key=lambda e: -e['decks']) for k in M), 'engines are sorted by decks')
check(all(e['wins'] <= e['decks'] and e['archN'] >= 1 and e['archs'] for k in M for e in M[k]['engines']), 'wins never exceed decks and every engine has archetypes')
check(M['tcg']['engines'][0]['n'] == 'The Fallen & The Virtuous' and M['tcg']['engines'][0]['share'] > 20, 'The Fallen & The Virtuous leads the TCG list with more than 20% of the decks')
check(sum(1 for k in ('tcg', 'ocg', 'gen') for e in M[k]['engines'] if e['txt']) >= 25, 'the central card text is there for most engines')
check(M['speed']['engines'][0]['n'] == 'Branded', 'Duel Links Speed: Branded is the first engine')
check(engines.excerpt('A' * 400).endswith('…') and engines.excerpt('Short text.') == 'Short text.' and len(engines.excerpt('Sentence one. ' * 40)) <= 232, 'the effect excerpt is cut at a sentence or a word')
C = collections.Counter
c = engines.summarize(C({'X': 10, 'Y': 1}), C({'X': 2}), {'X': C({'A': 7, 'B': 3}), 'Y': C({'A': 1})}, 100, {'X': ['Card']}, lambda n: 'Text.')
check(len(c) == 1 and c[0]['n'] == 'X' and c[0]['share'] == 10.0 and c[0]['archN'] == 2 and c[0]['central'] == 'Card', 'summarize counts share, archetypes and the central card, and drops engines below the bar')
print('failed:', len(fails)); sys.exit(1 if fails else 0)
