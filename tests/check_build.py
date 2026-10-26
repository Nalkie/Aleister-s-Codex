"""Gate test for the built page data. Run from build/ after tools/build_db.py:  python tests/check_build.py
Exit code 0 = every check passed. Deterministic, no network."""
import json, os, re, sys


def load(name):
    txt = open(f"data/{name}.js", encoding="utf-8").read()
    assert txt.startswith("__load(") and txt.endswith(");"), name
    return json.loads(txt[txt.index(",") + 1:-2])

fails = []


def check(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg)
    if not cond:
        fails.append(msg)


idx = load('index')
rows = idx['cards']
by = {r[0]: r for r in rows}
# row layout: name, cat, sheet, cell, tcgBan, dlLimit, gen, chunk, flags, price
check(len(rows) > 14000, f'index has {len(rows)} cards (> 14000)')
check(len(by) == len(rows), 'card names are unique')
check([r[0] for r in rows] == sorted(by), 'index rows are sorted by name (sets files rely on the position)')

d = by['Droll & Lock Bird']
check(d[4] == 1, 'Droll & Lock Bird is Limited (1) in the TCG')
check(d[5] in (3, 4), 'Droll & Lock Bird allows 3 copies in Duel Links')
check(d[6] == 20, 'Droll & Lock Bird costs 20 Genesys points')
check(by['Pot of Greed'][4] == 0 and by['Pot of Greed'][6] == 20, 'Pot of Greed: forbidden in the TCG, 20 points after the anniversary update (30 -> 20)')
check(by['Blitzclique - Breakaway'][6] == 3, 'Blitzclique - Breakaway is 3 points (anniversary update 2 -> 3)')
check(by['Whisker Blitzclique'][6] == 11, 'Whisker Blitzclique is 11 points (anniversary update 6 -> 11)')
check(by['Brain Research Lab'][6] == 0, 'Brain Research Lab dropped to 0 points')
forb = [r[0] for r in rows if r[5] == 0]
check(len(forb) >= 30, f'{len(forb)} cards forbidden in Duel Links (>= 30)')
official = json.load(open('src/konami_current.json', encoding='utf-8'))
import html as _h
off = {_h.unescape(x['nameeng']): int(k) for k in ('0', '1', '2') for x in official[k]}
tcgb = {k: sum(1 for r in rows if r[4] == k) for k in (0, 1, 2)}
check(tcgb == {0: len(official['0']), 1: len(official['1']), 2: len(official['2'])}, f'TCG banlist matches the official Konami list exactly: {tcgb} (effective {official["from"]})')
check(all(by[n][4] == v for n, v in off.items() if n in by) and all(n in by for n in off), 'every official entry is in the database with its status')
check(not any(r[4] in (0, 1, 2) and r[0] not in off for r in rows), 'no card outside the official list is marked forbidden or limited')
check(by['Maliss <Q> White Binder'][4] == 0 and by['Armageddon Knight'][4] == 3, 'the 19 Oct 2026 list is applied (Maliss <Q> White Binder forbidden, Armageddon Knight unrestricted)')
check(len(idx['ban']['changes']) == sum(1 for k in ('0', '1', '2') for x in official[k] if 'prev' in x), 'banlist changes are carried to the page')
lim = [r for r in rows if 1 <= r[5] <= 3]
check(len(lim) > 50, f'{len(lim)} cards on the Duel Links restricted list')
check(any(r[4] == 2 for r in rows) and any(r[4] == 1 for r in rows) and any(r[4] == 0 for r in rows), 'TCG banlist has forbidden, limited and semi-limited cards')
check(sum(1 for r in rows if r[6] > 0) >= 740, f"{sum(1 for r in rows if r[6] > 0)} cards have Genesys points (YuGiOh Meta lists about 750)")
check(len(idx['tcgsets']) > 900, f"{len(idx['tcgsets'])} TCG sets in the index")

hi = {r[2] for r in rows if r[2] >= 0}
lo = {-2 - r[2] for r in rows if r[2] <= -2}
check(all(os.path.exists(f'sheets/s{s}.jpg') for s in hi) and all(os.path.exists(f'sheets/l{s}.jpg') for s in lo), f'all {len(hi)} hi-res and {len(lo)} low-res sprite sheets exist')
with_art = sum(1 for r in rows if r[2] != -1)
check(with_art / len(rows) > 0.97, f'{with_art} of {len(rows)} cards have art ({with_art / len(rows):.1%})')
sheets = hi
check(sum(1 for r in rows if r[2] >= 0) > 1500, 'at least 1500 cards have hi-res art (meta recipes, staples, banlists, Genesys points)')
cells = [(r[2], r[3]) for r in rows if r[2] != -1]
check(len(cells) == len(set(cells)) and all(k < (idx['cols'] if s >= 0 else idx['lcols']) ** 2 for s, k in cells), 'sprite cells are unique and inside their sheet')

chunk = load(f'c{d[7]}')
det = chunk['Droll & Lock Bird']
check(len(det['pn']) >= 10, f"Droll & Lock Bird has {len(det['pn'])} TCG printings")
dates = [idx['tcgsets'][p[0]][1] for p in det['pn']]
check(dates == sorted(dates, reverse=True), 'printings are listed newest first')
check(det['dl']['ob'] and det['dl']['r'], 'Droll & Lock Bird has Duel Links rarity and sources')

alb = load(f"c{by['Albion the Branded Dragon'][7]}")['Albion the Branded Dragon']
sets = [o for o in alb['dl']['ob'] if o[0] == 's']
check(any(o[1] == 'Chaos Voltage' for o in sets) and any('Selection' in (o[2] or '') for o in sets), 'Albion: sold in Chaos Voltage and in a Selection Box (source order is applied in the page)')
check(all(o[4] for o in sets), 'every Duel Links box source carries a release date')

has_trader = has_trader_only = 0
for f in os.listdir('data'):
    if re.match(r'c\d+\.js$', f):
        for n, det in load(f[:-3]).items():
            ob = (det.get('dl') or {}).get('ob', [])
            if any(o[0] == 'o' and o[1] in ('Card Trader', 'Ex Card Trader') for o in ob):
                has_trader += 1
                if not any(o[0] == 's' for o in ob):
                    has_trader_only += 1
check(has_trader > 40 and has_trader_only > 0, f'Card Trader cards: {has_trader}, of which {has_trader_only} not sold in any box')

tcg = load('sets-tcg')
check(len(tcg) > 900 and tcg[0]['d'] >= tcg[-1]['d'], 'TCG sets are sorted newest first')
check(any(len(s['k']) > 50 for s in tcg), 'TCG sets list their cards')
check(not any('&' in s['n'] and ';' in s['n'] for s in tcg) and not any('&apos;' in n[0] for n in idx['tcgsets']), 'no HTML entities in TCG set names')
dls = load('sets-dl')
cv = [s for s in dls if s['n'] == 'Chaos Voltage' and s['kind'] == 'set']
check(cv and by['Albion the Branded Dragon'] and any(rows[k[0]][0] == 'Albion the Branded Dragon' for k in cv[0]['k']), 'Chaos Voltage lists Albion the Branded Dragon')
check({s['kind'] for s in dls} == {'set', 'char', 'other'}, 'Duel Links sources include boxes, characters and other routes')

check(by['Amazoness Paladin'][5] == 5, 'Amazoness Paladin (TCG card without a Duel Links release) is marked as not available yet')
check(by['Droll & Lock Bird'][8] & 2 and not by['Amazoness Paladin'][8] & 2, 'only released cards carry the Duel Links flag')
unavail = sum(1 for r in rows if r[8] & 1 and (r[5] < 0 or r[5] == 5))
check(unavail > 3000, f'{unavail} TCG cards are not available in Duel Links yet')

ygm = json.load(open('dl/ygmdata.json', encoding='utf-8'))
dld = json.load(open('dl/dldata.json', encoding='utf-8'))
for f in ('tcg', 'gen'):
    ds = ygm[f]['decks']
    check(any(v['tier'] == 'T1' for v in ds.values()), f'{f}: at least one T1 deck (computed)')
    check(any(v['out'] and v['wins'] >= 1 for v in ds.values()), f'{f}: has winners outside the meta')
    check(all(sum(r[1] for r in v['recipe']['main']) >= 40 for v in ds.values()), f'{f}: every recipe has at least 40 main-deck cards')
check(any(v['tier'] for v in dld['speed']['decks'].values()) and any(v['out'] for v in dld['speed']['decks'].values()), 'Duel Links: tiers from the API and winners outside the meta')
check(all(sum(r[1] for r in v['recipe']['main']) >= 20 for v in dld['speed']['decks'].values()), 'Duel Links Speed recipes have at least 20 main-deck cards')
check(ygm['asof'] >= '2026-10-01' and dld['asof'] >= '2026-10-20', f"meta data is recent (TCG {ygm['asof']}, Duel Links {dld['asof']})")

page = open('index.html', encoding='utf-8').read()
check('__' not in re.sub(r'__proto__', '', ''.join(re.findall(r'/\*__[A-Z]+__\*/', page))), 'no unreplaced placeholders in index.html')
check("<title>Aleister's Codex</title>" in page, "page title is Aleister's Codex")
for tab in ('tab-ex', 'tab-sets', 'tab-ban'):
    check(f'id="{tab}"' in page, f'{tab} present')

ygo = json.load(open('src/ygo_all.json', encoding='utf-8'))
lp = [c['name'] for c in ygo if 'Link' in (c['type'] or '') or 'Pendulum' in (c['type'] or '')]
check(len(lp) > 800 and all(by[n][6] == -3 for n in lp), f'{len(lp)} Link and Pendulum monsters are marked as not usable in Genesys')
check(not any(r[6] > 0 and r[0] in set(lp) for r in rows), 'no Link or Pendulum monster carries Genesys points')
check(by['Droll & Lock Bird'][6] == 20 and by['Link Spider'][6] == -3, 'Genesys: pointed cards keep their points, Link Spider is not usable')

check(by['Ash Blossom & Joyous Spring'][10] == 14558127 and by['Droll & Lock Bird'][10] == 94145021, 'cards carry their passcode (needed for YDK and YDKE export)')
check(sum(1 for r in rows if r[10]) > 14000, 'more than 14000 cards have a passcode')

# regression: a body mode class equal to a component class (.deck{overflow:hidden}) locked page scroll
modes = re.search(r"const MODES\s*=\s*\[([^\]]*)\]", page)
comp = set(re.findall(r'(?m)^\.([a-z][\w-]*)\{[^}]*overflow:hidden', page))
body_cls = set(re.findall(r'body\.([a-z][\w-]*)\{', page))
check(not (body_cls & comp), 'body mode classes do not collide with overflow:hidden components: %s' % (body_cls & comp))

# ---- patch 16: Spanish names, alternate arts, box art, real card images, guide data
es = load('es')
check(len(es) == len(rows) and sum(1 for n in es if n) > 12000, f'Spanish names aligned with the index rows ({sum(1 for n in es if n)} of {len(rows)})')
check(es[[r[0] for r in rows].index('Dark Magician')] == 'Mago Oscuro', 'Dark Magician is Mago Oscuro in Spanish')
check(len(idx['alts']) > 500 and len(idx['alts']['Ash Blossom & Joyous Spring']) >= 2, f"{len(idx['alts'])} cards carry alternate artworks (YGOPRODeck + YGOJSON + Duel Links Meta)")
check(any(isinstance(i, str) and i.startswith('d:') for v in idx['alts'].values() for i in v), 'Duel Links alternate cards are listed as d:<id>')
check(idx['alts']['Aleister the Invoker'][0] == 86120751, 'the first artwork of a card is its original passcode')
check(all(os.path.getsize(f'art/line-{k}.png') > 20000 for k in ('aleister', 'ecclesia')), 'side line-art images exist (tools/lineart.py)')
check(all(len(r) == 14 for r in rows), 'index rows carry the Duel Links Meta id, Duel Links rarity and release date')
check(sum(1 for r in rows if r[12] in ('N', 'R', 'SR', 'UR')) > 3000 and by['Blue-Eyes White Dragon'][12] == 'UR', 'Duel Links rarity is in the index for every Duel Links card (not only deck cards)')
check(sum(1 for r in rows if r[13]) > 3000, 'Duel Links release dates are in the index')
check(sum(1 for r in rows if not r[10] and r[11]) > 100 and sum(1 for r in rows if r[10] and r[11]) > 1000, 'every Duel Links card carries its Duel Links Meta id (fallback picture)')
check(sum(1 for s in dls if s['kind'] == 'set' and s['img']) > 100, 'Duel Links boxes carry their banner image path')
check(sum(1 for s in tcg if s['code']) > 900, 'TCG sets carry their set code (box picture URL)')
arts = [f for f in os.listdir('art') if not f.startswith('line-')]
check(len(arts) > 40 and all(os.path.getsize('art/' + f) > 15000 for f in arts), f'{len(arts)} deck art files at 360px (larger than the old 200px thumbnails)')
check('const ARTPOS = {' in page and re.search(r'const ARTPOS = \{"\d+": ?\d+', page) is not None, 'deck art focal positions are injected')

SRC_NAMES = {c['name'] for c in ygo} | {x['n'] for x in json.load(open('src/dl_cards.json', encoding='utf-8'))}
txt = open('tools/guide_extra.js', encoding='utf-8').read() + open('src.html', encoding='utf-8').read()
keys = set()
for m in re.finditer(r"keys:\[([^\]]*)\]", txt):
    for q in re.finditer(r"'((?:[^'\\]|\\.)*)'", m.group(1)):
        keys.add(q.group(1).replace("\\'", "'"))
for m in re.finditer(r"\{n:'((?:[^'\\]|\\.)*)',s:", txt):
    keys.add(m.group(1).replace("\\'", "'"))
bad = sorted(k for k in keys if k not in SRC_NAMES)
check(len(keys) > 80 and not bad, f'every guide card exists in the database ({len(keys)} names; missing: {bad})')
check('Pot of Greed' in keys and by['Pot of Greed'][4] == 0, 'the guide lists Pot of Greed and the page marks it forbidden from the data (not hard-coded)')
check('__GUIDEX__' not in page and 'GUIDE.summons=' in page, 'guide extension (summons, deck write-ups) is inlined in index.html')
for rule in ('const DL_MIN=20, DL_MAX=30, DL_EXTRA=9;', 'No se pueden usar cartas prohibidas', 'id="dk-notes"', 'wsrv.nl'):
    check(rule in page, f'page contains: {rule}')

# ---- patch 18: TCGplayer pictures, character sources, original deck art
pm = sum(1 for s_ in tcg for k in s_['k'] if len(k) > 4 and k[4])
tot = sum(len(s_['k']) for s_ in tcg)
check(pm / tot > 0.7, f'{pm} of {tot} TCG printings have their TCGplayer picture id ({pm / tot:.0%})')
chars = [s_ for s_ in dls if s_['kind'] == 'char']
subs = {k[2] for s_ in chars for k in s_['k'] if len(k) > 2}
check('Drop' in subs and 'Starter Deck' in subs and any(x.startswith('Level ') for x in subs), f'character sources carry how the card is obtained: {sorted(subs)[:6]}...')
import re as _re
arts_js = _re.search(r'const ARTS = (\{.*?\});', page).group(1)
check('86120751' in arts_js and '86120752' not in arts_js, 'deck art uses the original Aleister the Invoker artwork')
check(os.path.exists('art/86120751.jpg'), 'original Aleister art file exists')

# ---- patch 19: events, characters, tickets, versions
evs = load('events')
check(sum(1 for e in evs if e['f'] == 'Genesys') > 20 and sum(1 for e in evs if e['f'] == 'TCG') > 50, f'{len(evs)} TCG and Genesys events')
check(sum(1 for e in evs if e['top']) > 100 and any(e['top'][0][0] == 1 for e in evs if e['top']), 'events carry their top placements')
dli = load('dlinfo')
check(len(dli['chars']) > 150 and dli['chars']['Yugi Muto']['p'].startswith('/img/characters/') and dli['chars']['Yugi Muto']['s'], 'Duel Links characters have portraits and skills')
check(any(e['e'] >= '2026-10-20' for e in dli['events']), 'Duel Links events carry end dates')
check(any(s_['kind'] == 'char' and s_.get('img') for s_ in dls), 'character sources carry their portrait')
oth = [s_ for s_ in dls if s_['kind'] == 'other']
check(any(s_['rush'] for s_ in oth) and any(not s_['rush'] for s_ in oth), 'other routes are listed apart for Speed Duel and Rush Duel')
pn = load(f"c{by['Dark Magician'][7]}")['Dark Magician']['pn']
check(all(len(p_) == 5 for p_ in pn) and sum(1 for p_ in pn if p_[4]) > len(pn) * 0.5, f'card detail printings carry the TCGplayer picture id ({sum(1 for p_ in pn if p_[4])} of {len(pn)})')
check('data:image/png;base64' in page and '__LINE_' not in page, 'side art and Duel Links icon are inlined')

# event links: the APIs return paths the sites do not serve (404); the page must add /articles (Duel Links Meta) and /top-decks (YuGiOh Meta)
m_dlm = re.search(r"const dlmUrl=u=>(.*?);", page)
m_ygm = re.search(r"const ygmDeckUrl=u=>(.*?);", page)
check(bool(m_dlm and m_ygm), 'page defines dlmUrl and ygmDeckUrl')
check('duellinksmeta.com${esc(e.u)}' not in page and 'yugiohmeta.com${esc(u)}' not in page, 'no event link is built from a raw API path')
import shutil, subprocess
if shutil.which('node') and m_dlm and m_ygm:
    js = f"const dlmUrl=u=>{m_dlm.group(1)};const ygmDeckUrl=u=>{m_ygm.group(1)};"          "console.log(JSON.stringify([dlmUrl('/events/2026/october/zane-raid-event/'),dlmUrl('/articles/events/x/'),dlmUrl('/tournaments/2026/rush/world-championship-qualifiers/'),"          "ygmDeckUrl('/fort-worth-october-2026-regional/elfnote/cameron-neal/2eMdo/'),ygmDeckUrl('/top-decks/a/b/c/')]))"
    got = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, encoding='utf-8').stdout or '[]')
    check(got == ['https://www.duellinksmeta.com/articles/events/2026/october/zane-raid-event/', 'https://www.duellinksmeta.com/articles/events/x/',
                  'https://www.duellinksmeta.com/articles/tournaments/2026/rush/world-championship-qualifiers/',
                  'https://www.yugiohmeta.com/top-decks/fort-worth-october-2026-regional/elfnote/cameron-neal/2eMdo/', 'https://www.yugiohmeta.com/top-decks/a/b/c/'],
          'dlmUrl / ygmDeckUrl add the prefix once and never twice')

# characters: victory art (transparent 512x512) leaves the box; tickets drawn like the game's
check("class=\"spack char vic\"" in page and 'const charVic=' in page and '.setb .spack.vic img' in page, 'character lists use the victory art (portrait only as fallback)')
check('function tkSvg(kind,label,stars,o={})' in page and all(k in page for k in ("UR:['#46e6ff'", "SR:['#fff0a0'", "R:['#8cc0ff'", "N:['#ffffff'")), 'tickets: UR, SR, R and N have their own gradient (tkSvg)')

check('function viewTickets()' not in page and 'id="tab-tk"' not in page, 'no separate Tickets tab (tickets live in Cajas y sets > Otras vías)')
check('Dream UR' in page and 'dragon' in page, 'Dream tickets draw the dragon head')

check(all(x in page for x in ('const FMT_RETRO=', 'function fmLimit(', 'function viewMetaFmt(', "['formats','Formatos del TCG']", 'data-dkfmt=')) and os.path.exists('data/formats.js'), 'TCG formats: Edison, Goat and HAT in the TCG tab, banlist, search, deck builder and Guide')

check(os.path.exists('art/ticket-dragon.png') and 'art/ticket-dragon.png' in page, 'Dream tickets use art/ticket-dragon.png (transparent PNG of the dragon head)')

check(all(x in page for x in ('function viewAboutAdv()', 'Cartas más usadas', 'const localToday=', 'hue-rotate(200deg)')), 'every TCG format has card usage and an About section; gold Dream ticket uses a warm dragon tone; "hoy" uses the local date')

check(all(x in page for x in ('function charFlag(', 'function charCard(', 'class="cfg"', '.chcard{')), 'characters: translucent art + signature card in the list, character card when one is chosen')

check('Personajes y habilidades' not in page and 'function evChars' not in page and 'data-evtab' not in page, 'Eventos y torneos no longer has Personajes y habilidades (characters live in Cajas y sets)')

check('id="tab-obt"' in page and "obt:['Obtención',viewSets]" in page and '.fill{animation:none!important}' in page, 'Obtención tab (characters and other ways to get cards) and no periodic light flashes')

print('failed:', len(fails))
sys.exit(1 if fails else 0)
