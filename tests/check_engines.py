"""Gate test for data/engines.js: engines (card packages) per mode with the cards that make them up, and staples apart. Deterministic, no network.
Run from the project root after tools/engines.py:  python tests/check_engines.py"""
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
check(len(M['tcg']['engines']) >= 8 and len(M['ocg']['engines']) >= 8, 'TCG and OCG list 8+ engines')
check(all(len(e['pack']) >= engines.MIN_PACK for k in M for e in M[k]['engines']), 'every engine is made of at least 3 cards')
check(all(p >= engines.PACK_IN * 100 - 1 for k in M for e in M[k]['engines'] for _, p, _ in e['pack']), 'every card of a package is in at least 55% of the decks with the engine')
check(all(e['decks'] <= M[k]['total'] and abs(e['share'] - e['decks'] / M[k]['total'] * 100) < 0.06 for k in M for e in M[k]['engines']), 'every engine share is its decks over the decks of the mode')
check(all(M[k]['engines'] == sorted(M[k]['engines'], key=lambda e: -e['decks']) for k in M), 'engines are sorted by decks')
names = {e['n'] for k in ('tcg', 'ocg', 'gen') for e in M[k]['engines']}
check(not names & {'Dominus Purge', 'Dominus Impulse', 'Dominus Spark', 'Super Polymerization', 'The Fallen & The Virtuous', 'Fidraulis Harmonia'}, 'single-card staples (Dominus Purge, Super Polymerization...) are not engines')
check({'Branded', 'Diabellestar', 'Azamina'} <= {e['n'] for e in M['tcg']['engines']} | {e['n'] for e in M['speed']['engines']}, 'Branded, Diabellestar and Azamina are engines')
br = next(e for e in M['speed']['engines'] if e['n'] == 'Branded')
check({'Albion the Branded Dragon', 'Fallen of Albaz'} <= {c for c, *_ in br['pack']}, 'the Branded package holds Fallen of Albaz and Albion the Branded Dragon')
check(all(any(s['n'] == 'Droll & Lock Bird' for s in M[k]['staples']) for k in ('tcg', 'ocg')), 'Droll & Lock Bird is a staple of the TCG and the OCG')
check(not any(c in {s['n'] for s in M['tcg']['staples'] if s['pct'] >= 80} for e in M['tcg']['engines'] for c, *_ in e['pack']), 'cards that nearly every deck plays (80%+) are never part of an engine')
check(engines.excerpt('A' * 400).endswith('…') and engines.excerpt('Short text.') == 'Short text.', 'the effect excerpt is cut at a sentence or a word')
decks = [collections.Counter({'A': 1, 'B': 2, 'C': 1, 'X': 1}) for _ in range(6)] + [collections.Counter({'X': 1}) for _ in range(14)]
C = collections.Counter
out = engines.summarize({'Eng': list(range(6)), 'One': [0, 1, 2, 3, 4, 5]}, C({'Eng': 1}), {'Eng': C({'Z': 6}), 'One': C({'Z': 6})}, decks, lambda n: 'Text.', 1.5, 5, lambda nm: nm == 'Eng')
check(len(out) == 1 and out[0]['n'] == 'Eng' and [c for c, *_ in out[0]['pack']] == ['A', 'B', 'C'] and out[0]['pack'][1][2] == 2.0, 'summarize builds the package from the cards only that engine plays (X, played by every deck, stays out) and drops non-engine labels')
print('failed:', len(fails)); sys.exit(1 if fails else 0)
