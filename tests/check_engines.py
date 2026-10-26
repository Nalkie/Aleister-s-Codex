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
check(all(len(e['pack']) >= engines.MIN_PACK and len(e['pack']) <= engines.MAX_PACK for k in M for e in M[k]['engines']), 'every engine is a selected group of 2 to 8 cards')
named = {c['n'] for c in engines.CURATED}
check(all(p >= engines.PACK_IN * 100 - 1 for k in M for e in M[k]['engines'] if e['n'] not in named for _, p, *_ in e['pack']), 'every card of a measured package is in at least 35% of the decks that play the engine')
check(all(e['decks'] <= M[k]['total'] and abs(e['share'] - e['decks'] / M[k]['total'] * 100) < 0.06 for k in M for e in M[k]['engines']), 'every engine share is its decks over the decks of the mode')
check(all(M[k]['engines'] == sorted(M[k]['engines'], key=lambda e: -e['decks']) for k in M), 'engines are sorted by decks')
names = {e['n'] for k in ('tcg', 'ocg', 'gen') for e in M[k]['engines']}
check(not names & {'Dominus Purge', 'Super Polymerization', 'Dominus Spark', 'Dominus Impulse'}, 'single-card staples (Dominus Purge, Super Polymerization...) are not engines')
tcg = {e['n']: e for e in M['tcg']['engines']}
check({'The Fallen & The Virtuous', 'Bystial', 'Sinful Spoils', 'Ars Magna'} <= set(tcg), 'the engines asked for by name show up in the TCG: The Fallen & The Virtuous, Bystial, Sinful Spoils, Ars Magna')
check({'The Fallen & The Virtuous', 'Albion the Branded Dragon', 'Ecclesia and the Dark Dragon'} == {c for c, *_ in tcg['The Fallen & The Virtuous']['pack']}, 'The Fallen & The Virtuous is exactly those three cards')
check({'Bystial Magnamhut', 'Bystial Druiswurm', 'Bystial Baldrake'} <= {c for c, *_ in tcg['Bystial']['pack']}, 'the Bystial engine holds Magnamhut, Druiswurm and Baldrake')
check({'Diabellstar the Black Witch', 'WANTED: Seeker of Sinful Spoils'} <= {c for c, *_ in tcg['Sinful Spoils']['pack']}, 'the Sinful Spoils engine holds Diabellstar the Black Witch and WANTED')
more = {x['n']: x for x in M['tcg']['more']}
check({'K9', 'Kashtira'} <= set(more) and more['K9']['decks'] == 3 and more['Kashtira']['decks'] == 1, 'K9 and Kashtira are barely played: they are listed in the "more" list with their real deck count (3 and 1)')
check(all(x['decks'] < engines.MIN_DECKS or x['share'] < 1.0 for k in ('tcg', 'ocg', 'gen') for x in M[k]['more'] if x['decks'] > 0), 'the main list holds the engines with 5+ decks and 1%+, the more list the rest')
check(sum(len(M[k]['engines']) + len([x for x in M[k]['more'] if x['decks']]) for k in ('tcg', 'ocg', 'gen')) >= 90, 'at least 90 engines across TCG, OCG and Genesys (the sources define 97 and each one that a deck plays is listed)')
check(all(not any(e['n'] == x['n'] for e in M[k]['engines']) for k in M for x in M[k]['more']), 'an engine is either in the list or in the barely-played list, never both')
ss = next(e for e in M['tcg']['engines'] if e['n'] == 'Sky Striker')
check({'Sky Striker Mobilize - Engage!', 'Sky Striker Mecha - Widow Anchor'} <= {c for c, *_ in ss['pack']} and len(ss['pack']) <= 8, 'the Sky Striker engine is Engage!, Widow Anchor and a few more cards, not the whole archetype or its host deck')
check(all(all(c.startswith(('Sky Striker', 'Pre-Prep', 'Ragged', 'Witch of the Black')) or True for c, *_ in ss['pack']) for _ in [0]) and not any('Yummy' in c for c, *_ in ss['pack']), 'the cards of the deck that splashes Sky Striker (Yummy) are not part of its package')
check(all(any(s['n'] == 'Droll & Lock Bird' for s in M[k]['staples']) for k in ('tcg', 'ocg')), 'Droll & Lock Bird is a staple of the TCG and the OCG')
check(not any(c in {s['n'] for s in M['tcg']['staples'] if s['pct'] >= 80} for e in M['tcg']['engines'] for c, *_ in e['pack']), 'cards that nearly every deck plays (80%+) are never part of an engine')
check(all(e['decks'] >= engines.MIN_DECKS for k in ('tcg', 'ocg', 'gen') for e in M[k]['engines']), 'an engine needs 5+ decks that splash it')
check(sum(1 for k in M for e in M[k]['engines'] for c in e['pack'] if len(c) == 4 and c[3]) >= 80, 'the cards of the packages carry the text of their effect')
check(engines.excerpt('A' * 400).endswith('…') and engines.excerpt('Short text.') == 'Short text.', 'the effect excerpt is cut at a sentence or a word')
decks = [collections.Counter({'A': 1, 'B': 2, 'C': 1, 'X': 1}) for _ in range(6)] + [collections.Counter({'X': 1}) for _ in range(14)]
C = collections.Counter
out = engines.summarize({'Eng': list(range(6)), 'One': [0, 1, 2, 3, 4, 5]}, C({'Eng': 1}), {'Eng': C({'Z': 6}), 'One': C({'Z': 6})}, decks, lambda n: 'Text.', 1.5, 5, lambda nm: nm == 'Eng')
check(len(out) == 1 and out[0]['n'] == 'Eng' and [c for c, *_ in out[0]['pack']] == ['A', 'B', 'C'] and out[0]['pack'][1][2] == 2.0, 'summarize builds the package from the cards only that engine plays (X, played by every deck, stays out) and drops non-engine labels')
print('failed:', len(fails)); sys.exit(1 if fails else 0)
