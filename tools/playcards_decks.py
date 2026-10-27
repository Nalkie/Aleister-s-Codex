"""Lista los mazos de un formato que merecen ficha (tier 1 a 3) con su clave, su receta y su Side, para redactar src/playcards/<formato>.json.
  python tools/playcards_decks.py edison            (formatos: adv ocg edison goat hat gen)
Después de escribir:  python tools/playcards.py   (valida contra las cartas y las listas reales)"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import playcards

fmt = sys.argv[1] if len(sys.argv) > 1 else ''
if fmt not in playcards.FORMATS:
    sys.exit(__doc__)
sys.stdout.reconfigure(encoding='utf-8')
t = playcards.load_js(os.path.join(ROOT, 'data/ygmx.js'))
y = json.load(open(os.path.join(ROOT, 'dl/ygmdata.json'), encoding='utf-8'))
if fmt == 'dl':                  # Duel Links: Speed Duel con tiers y Rush Duel sin tiers (se listan los 6 más usados)
    dl = json.load(open(os.path.join(ROOT, 'dl/dldata.json'), encoding='utf-8'))
    rec = playcards.recipes()['dl']
    for mode in ('speed', 'rush'):
        top = sorted(dl[mode]['decks'].items(), key=lambda kv: -kv[1]['share'])
        for n, d in top:
            if d.get('out') or (mode == 'speed' and d.get('tier') not in (1, 2, 3)) or (mode == 'rush' and n not in [k for k, _ in top[:6]]):
                continue
            name = n.replace(' : Rush!', ' (Rush)').replace(': Rush!', ' (Rush)')
            r = rec[playcards.DECK_SLUG(name)]
            print('== KEY dl/%s | %s | %s | tier %s | %.1f%% of decks | %d wins | Skill: %s (%s%%)' % (playcards.DECK_SLUG(name), name, mode, d.get('tier'), d['share'], d['wins'], d.get('skill'), d.get('skillPct')))
            for sec in ('main', 'extra'):
                print('  %s: %s' % (sec, ', '.join('%dx %s' % (q, c) for c, q in r[sec].items())))
    sys.exit(0)
decks = {'ocg': t['ocg']['decks'], 'edison': t['edison']['decks'], 'goat': t['goat']['decks'], 'hat': t['hat']['decks'], 'adv': y['tcg']['decks'], 'gen': y['gen']['decks']}[fmt]
rec = playcards.recipes()[fmt]
for n, d in decks.items():
    if d.get('tier') not in ('T1', 'T2', 'T3'):
        continue
    r = rec[playcards.DECK_SLUG(n)]
    print('== KEY %s/%s | %s | tier %s | %.1f%% of decks | %d wins' % (fmt, playcards.DECK_SLUG(n), n, d['tier'], d['share'], d['wins']))
    for s in ('main', 'extra', 'side'):
        print('  %s: %s' % (s, ', '.join('%dx %s' % (q, c) for c, q in r[s].items())))
