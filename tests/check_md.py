"""Gate test of the Master Duel format (banlist, pool, tier list, recipes).  Sin red.  Run from the project root after tools/formats.py and tools/formats_meta.py:
  python tests/check_md.py

  * src/md.json (tools/fetch_md.py) is a recent, complete snapshot of Master Duel Meta.
  * data/formats.js has the Master Duel banlist and pool, and data/ygmx.js the tier list, both identical to what tools/md.py builds from src/md.json.
  * Tiers follow the rule written in tools/md.py, every recipe is a real list of database cards, and the Maliss spelling is mapped.
  * The page lists Master Duel next to the OCG in the TCG format bar, the banlist, the deck builder, the guide and the URL routes.
"""
import collections, datetime, json, os, re, sys

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

import fetch_md
check(fetch_md.today() == datetime.datetime.now(datetime.timezone.utc).date(), 'fetch_md dates the window in UTC like the API (a local date left the newest deck outside the window)')

# ---- name resolution ----
check(res('Maliss P Chessy Cat') == 'Maliss <P> Chessy Cat' and res('Ash Blossom & Joyous Spring') == 'Ash Blossom & Joyous Spring' and res('Not A Card') is None, 'resolver: Maliss spelling mapped, real names kept, unknown names rejected')

# ---- data/formats.js ----
F = load_js('data/formats.js')
check(F['order'] == ['ocg', 'md', 'edison', 'goat', 'hat'], 'formats order: OCG, Master Duel, Edison, Goat, HAT')
m = F['formats']['md']
pool = {names[i] for i in m['pool']}
check(m['name'] == 'Master Duel' and 10000 < len(pool) < len(names), 'Master Duel pool: %d cards of %d' % (len(pool), len(names)))
api = {res(n): {'Forbidden': 0, 'Limited': 1, 'SemiLimited': 2}[s] for s, l in src['ban'].items() for n in l if res(n)}
cur, nxt = mdmod.ban_state(src, res)
check(m['ban'] == cur and len(api) >= sum(map(len, src['ban'].values())) - 3, 'banlist in force: %d cards (statuses 0/1/2)' % len(m['ban']))
# banStatus of the API already carries the announced list that is not in force yet: the list in force plus that list must give the API back
future = [c for c in src['changes'] if c['d'] > src['fetched']]
check(bool(src['changes']) and [c['d'] for c in src['changes']] == sorted(c['d'] for c in src['changes']), 'banlist changes: %d, sorted by date' % len(src['changes']))
back = dict(cur)
for c in (nxt or {'changes': []})['changes']:
    if c['to'] >= 3:
        back.pop(c['card'], None)
    else:
        back[c['card']] = c['to']
check(back == api, 'the list in force plus the announced next list is what the API calls banStatus (%d cards change on %s)' % (len(nxt['changes']) if nxt else 0, nxt['date'] if nxt else '-'))
check((nxt is None) == (not future) and (nxt is None or (nxt['date'] > src['fetched'] and nxt['changes'] and m['upcoming'] == nxt)), 'data/formats.js carries the next list (date after the download, with its changes)')
check(all((c['from'] if c['from'] < 3 else None) == (cur.get(c['card']) if cur.get(c['card'], 3) < 3 else None) for c in (nxt or {'changes': []})['changes']), 'every change of the next list starts from the list in force')
check(m['last'] is None or m['last']['date'] <= src['fetched'], 'the last update is dated on or before the download')
check(all(n in pool for n in m['ban']), 'every banlisted card is in the pool')
check('Maliss <Q> White Binder' in pool and 'Maliss <P> Chessy Cat' in pool, 'Maliss cards are in the pool under the database names')
out = formats.build(json.load(open('src/formats.json', encoding='utf-8')), ygo, json.load(open('src/cardsets.json', encoding='utf-8')), names, src)
check(out == F, 'data/formats.js matches what tools/formats.py builds now')

# ---- data/ygmx.js ----
X = load_js('data/ygmx.js')['md']
check(X == json.loads(json.dumps(mdmod.meta(src, res, cur), ensure_ascii=False)), 'data/ygmx.js matches what tools/md.py builds now')
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
def copies(v):
    c = collections.Counter()
    for s in ('main', 'extra', 'side'):
        for n, k, *_ in v['recipe'][s]:
            c[n] += k
    return c
legal_ok = [k for k, v in dk.items() if v['who']['post'] and all(n_ <= cur.get(n, 3) for n, n_ in copies(v).items())]
check(all(k in legal_ok for k, v in dk.items() if v['who']['post']), 'a recipe marked as played under the current banlist obeys it (no Forbidden card, no card over its limit)')
check(sum(1 for v in dk.values() if v['who']['post']) >= len(dk) * 0.8 and all(v['npost'] == v['legal'] for v in dk.values()), 'most decks have recipes from lists that are legal today (%d of %d)' % (sum(1 for v in dk.values() if v['who']['post']), len(dk)))

# ---- same input, same output, whatever the hash seed ----
import subprocess
probe = "import json,sys; sys.path.insert(0,'tools'); import md; s=json.load(open('src/md.json',encoding='utf-8')); g=json.load(open('src/ygo_all.json',encoding='utf-8')); print(json.dumps(md.meta(s, md.resolver(c['name'] for c in g)), sort_keys=True))"
outs = {seed: subprocess.run([sys.executable, '-c', probe], env={**os.environ, 'PYTHONHASHSEED': seed}, capture_output=True).stdout for seed in map(str, range(12))}
check(len(set(outs.values())) == 1 and all(outs.values()), 'tools/md.py gives the same tier list under 12 hash seeds (the unsorted version gave 2 different lists)')

# ---- the page ----
page = open('src.html', encoding='utf-8').read()
check("md:'Master Duel'" in page and "RETRO_ES.md=" in page, 'FMT_RETRO and RETRO_ES know Master Duel')
check("['adv','ocg','edison','goat','hat'].map(k=>`<button data-tcgf" in page, 'the TCG format bar does not list Master Duel (it is a section of its own)')
check('id="tab-md" data-mode="md"' in page and "md:['Master Duel',viewMD]" in page and 'function viewMD()' in page and 'body.md{--accent:var(--ac-md)}' in page, 'Master Duel is a top-level section next to TCG, Genesys and Duel Links (card, view and accent)')
check('class="glyph mdicon"' in page and '/*__LINE_MD__*/art/line-md.png' in page and os.path.getsize('art/line-md.png') > 2000 and 'art/line-md.png' in open('files.json').read() and os.path.exists('tools/mkicon_md.py'), 'the Master Duel card has its own icon (art/line-md.png, an orange mask, built by tools/mkicon_md.py, published in files.json)')
check('Ranked y banlist propia' in page and 'Videojuego de Konami</small>' not in page, 'the Master Duel card says what is specific to it (ranked and its own banlist), not a generic tagline')
foot = page[page.index('<summary>Fuentes y l'):page.index('</details>', page.index('<summary>Fuentes y l'))]
check('masterduelmeta.com' in foot and 'Master Duel, cómo se calcula' in foot and 'dolarapi.com' in foot and 'Actualización:' in foot and 'sin relación con Konami' in foot, 'Sources and limits name Master Duel Meta, how Master Duel is computed, DolarAPI, the daily update and that the site is not affiliated with Konami')
check("if(['tcg','md','ban','deck','ex','guide','rou'].includes(mode)) render()" in page and "mode==='md'||mode==='ev'" in page, 'the Master Duel view redraws when its data arrives')
check("['tcg','ocg','md','edison','goat','hat','gen','dl']" in page, 'the deck builder offers Master Duel')
check("md:['md','']" in page and "md:'#4ee1ff'" in page and "FMT_ES={tcg:'TCG',ocg:'OCG',md:'Master Duel'" in page, 'route ?mode=md, builder color and name')
check("retro=k!=='ocg'&&k!=='md'" in page, 'Master Duel is not treated as a historical format (no event table, no format date)')
check('data/formats.js' in open('files.json').read() and 'data/ygmx.js' in open('files.json').read(), 'files.json publishes formats.js and ygmx.js')
refresh = open('tools/refresh.py', encoding='utf-8').read()
check("'tools/fetch_md.py'" in refresh and "'src/md.json'" in refresh and 'tests/check_md.py' in refresh, 'refresh.py downloads Master Duel, backs it up and runs this test')
print('failed:', len(fails))
sys.exit(1 if fails else 0)
