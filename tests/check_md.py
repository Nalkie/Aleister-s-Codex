"""Gate test of the Master Duel format (banlist, pool, tier list, recipes).  Sin red.  Run from the project root after tools/formats.py and tools/formats_meta.py:
  python tests/check_md.py

  * src/md.json (tools/fetch_md.py) is a recent, complete snapshot of Master Duel Meta.
  * data/formats.js has the Master Duel banlist and pool, and data/ygmx.js the tier list, both identical to what tools/md.py builds from src/md.json.
  * Tiers follow the rule written in tools/md.py, every recipe is a real list of database cards, and the Maliss spelling is mapped.
  * The page lists Master Duel next to the OCG in the TCG format bar, the banlist, the deck builder, the guide and the URL routes.
"""
import datetime, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, 'tools')
import md as mdmod
import formats

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


load_js = lambda p: json.loads(open(p, encoding='utf-8').read()[open(p, encoding='utf-8').read().index(',') + 1:-2])
src = json.load(open('src/md.json', encoding='utf-8'))
ygo = json.load(open('src/ygo_all.json', encoding='utf-8'))
names = [r[0] for r in load_js('data/index.js')['cards']]
res = mdmod.resolver(c['name'] for c in ygo)

# ---- the snapshot ----
w0, w1 = (datetime.date.fromisoformat(x) for x in src['window'])
check(36 <= (w1 - w0).days <= 48, 'the window is about 42 days (%s .. %s)' % tuple(src['window']))
check(all(w0.isoformat() <= d['d'] <= w1.isoformat() for d in src['decks']), 'every deck is inside the window')
check(len(src['pool']) > 10000 and len(set(src['pool'])) == len(src['pool']), 'pool: %d cards, no duplicates' % len(src['pool']))
check(all(len(src['ban'][k]) > 10 for k in src['ban']) and len(src['decks']) > 500, 'banlist (%s) and %d decks' % ({k: len(v) for k, v in src['ban'].items()}, len(src['decks'])))
check(not (set(src['ban']['Forbidden']) & set(src['ban']['Limited'])) and not (set(src['ban']['Limited']) & set(src['ban']['SemiLimited'])), 'a card has one banlist status only')
check(all(d['type'] and d['who'] for d in src['decks']), 'every deck has a type and an author')

# ---- name resolution ----
check(res('Maliss P Chessy Cat') == 'Maliss <P> Chessy Cat' and res('Ash Blossom & Joyous Spring') == 'Ash Blossom & Joyous Spring' and res('Not A Card') is None, 'resolver: Maliss spelling mapped, real names kept, unknown names rejected')

# ---- data/formats.js ----
F = load_js('data/formats.js')
check(F['order'] == ['ocg', 'md', 'edison', 'goat', 'hat'], 'formats order: OCG, Master Duel, Edison, Goat, HAT')
m = F['formats']['md']
pool = {names[i] for i in m['pool']}
check(m['name'] == 'Master Duel' and 10000 < len(pool) < len(names), 'Master Duel pool: %d cards of %d' % (len(pool), len(names)))
want = {res(n): {'Forbidden': 0, 'Limited': 1, 'SemiLimited': 2}[s] for s, l in src['ban'].items() for n in l if res(n)}
check(m['ban'] == want and len(want) >= sum(map(len, src['ban'].values())) - 3, 'banlist: %d cards, same as Master Duel Meta (statuses 0/1/2)' % len(m['ban']))
check(all(n in pool for n in m['ban']), 'every banlisted card is in the pool')
check('Maliss <Q> White Binder' in pool and 'Maliss <P> Chessy Cat' in pool, 'Maliss cards are in the pool under the database names')
out = formats.build(json.load(open('src/formats.json', encoding='utf-8')), ygo, json.load(open('src/cardsets.json', encoding='utf-8')), names, src)
check(out == F, 'data/formats.js matches what tools/formats.py builds now')

# ---- data/ygmx.js ----
X = load_js('data/ygmx.js')['md']
check(X == json.loads(json.dumps(mdmod.meta(src, res), ensure_ascii=False)), 'data/ygmx.js matches what tools/md.py builds now')
dk = X['decks']
ranked = {k: v for k, v in dk.items() if not v['out']}
check(len(ranked) >= 10 and any(v['tier'] == 'T1' for v in ranked.values()), 'tier list: %d decks, with a Tier 1' % len(ranked))
tier_of = lambda p: next((t for line, t in mdmod.TIER_LINES if p >= line), None)
check(all(v['tier'] == tier_of(v['pts']) for v in ranked.values()), 'every tier follows its share of points (8 / 4 / 2)')
check(all(not v['out'] or (v['wins'] > 0 and v['tier'] is None and v['share'] < mdmod.OUTSIDE_SHARE) for v in dk.values()), 'outside the meta = won, no tier, under 2.5%')
check(abs(sum(v['n'] for v in dk.values()) / X['total'] * 100 - sum(v['share'] for v in dk.values())) < 1.5, 'shares add up to the decks they count')
check(X['dropped']['copies'] <= X['dropped']['of'] * 0.01, 'cards missing from the database: %d of %d copies (max 1%%)' % (X['dropped']['copies'], X['dropped']['of']))
bad = [(k, n) for k, v in dk.items() for s in ('main', 'extra', 'side') for n, *_ in v['recipe'][s] if n not in set(names)]
check(not bad, 'every recipe card is a database card%s' % (bad[:2] or ''))
check(all(40 <= sum(c[1] for c in v['recipe']['main']) <= 60 and sum(c[1] for c in v['recipe']['extra']) <= 15 and sum(c[1] for c in v['recipe']['side']) <= 15 for v in dk.values()), 'every recipe has a 40-60 card Main Deck, Extra and Side up to 15')
check(all(v['art'] in set(names) for v in dk.values()), 'every deck has a picture card from the database')
check(all(all(k <= 3 for _, k, *_ in v['recipe']['main']) for v in dk.values()), 'no recipe has more than 3 copies of a card')

# ---- the page ----
page = open('src.html', encoding='utf-8').read()
check("md:'Master Duel'" in page and "RETRO_ES.md=" in page, 'FMT_RETRO and RETRO_ES know Master Duel')
check("['adv','ocg','md','edison','goat','hat'].map(k=>`<button data-tcgf" in page, 'the TCG format bar lists Master Duel')
check("['tcg','ocg','md','edison','goat','hat','gen','dl']" in page, 'the deck builder offers Master Duel')
check("md:['tcg','md']" in page and "md:'#4ee1ff'" in page and "FMT_ES={tcg:'TCG',ocg:'OCG',md:'Master Duel'" in page, 'route ?mode=md, builder color and name')
check("retro=k!=='ocg'&&k!=='md'" in page, 'Master Duel is not treated as a historical format (no event table, no format date)')
check('data/formats.js' in open('files.json').read() and 'data/ygmx.js' in open('files.json').read(), 'files.json publishes formats.js and ygmx.js')
refresh = open('tools/refresh.py', encoding='utf-8').read()
check("'tools/fetch_md.py'" in refresh and "'src/md.json'" in refresh and 'tests/check_md.py' in refresh, 'refresh.py downloads Master Duel, backs it up and runs this test')
print('failed:', len(fails))
sys.exit(1 if fails else 0)
