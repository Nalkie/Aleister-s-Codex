"""Build the card database and the page.

Reads src/*.json (tools/fetch_sources.py), gen/points.json + the anniversary change list, dl/dldata.json
(tools/dl.py) and src.html, then writes:
  data/index.js        one row per card (name, type, sprite cell, bans, Genesys points, chunk, price, card code)
  data/c<N>.js         card details (effect text, printings, Duel Links acquisition), loaded on demand
  data/sets-tcg.js     TCG sets with their cards, rarities and numbers
  data/sets-dl.js      Duel Links boxes, characters and other sources with their cards
  sheets/s<N>.jpg      112px art sprite sheets for the relevant cards
  art/<id>.jpg         200px art for each deck's flagship card
  index.html           src.html with the small data blocks injected
Run from build/:  python tools/build_db.py
"""
import concurrent.futures as cf
import html as htmllib
import io, json, os, re, sys, time, urllib.request
from PIL import Image

UA = {'User-Agent': 'Mozilla/5.0'}
CELL, COLS, ROWS = 112, 9, 9
CHUNK = 400
GEN_BASE_DATE = '2026-10-05'

ygo = json.load(open('src/ygo_all.json', encoding='utf-8'))
tcg_sets_raw = json.load(open('src/cardsets.json', encoding='utf-8'))
dl_raw = json.load(open('src/dl_cards.json', encoding='utf-8'))
dl_sets_raw = json.load(open('src/dl_sets.json', encoding='utf-8'))
dldata = json.load(open('dl/dldata.json', encoding='utf-8'))
ygm = json.load(open('dl/ygmdata.json', encoding='utf-8'))
TODAY = __import__('datetime').date.today().isoformat()
src = open('src.html', encoding='utf-8').read()

# ---------------- names the page itself uses ----------------
STR = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"")
page_names = set()
for m in re.finditer(r"\b[PN]\(\[(.*?)\]", src, re.S):
    for q in STR.finditer(m.group(1)):
        page_names.add((q.group(1) if q.group(1) is not None else q.group(2)).replace("\\'", "'"))
for m in re.finditer(r"^\s*\d+x (.+?)\s*$", src, re.M):
    page_names.add(m.group(1).split('`')[0])
art_names = {m.group(1) for m in re.finditer(r"art:'([^']*)'", src)}
page_names |= art_names
for fmt in ('speed', 'rush'):
    for d in dldata[fmt]['decks'].values():
        for sec in d['recipe'].values():
            for row in sec:
                page_names.add(row[0])

# YGOPRODeck returns HTML entities in set names ("5D&apos;s"); unescape once, everywhere
for st in tcg_sets_raw:
    st['set_name'] = htmllib.unescape(st['set_name'])
for c in ygo:
    for st in c['sets']:
        st[0] = htmllib.unescape(st[0])

# names from the generated meta (recipes, key cards, flagship art)
for fmt in ('tcg', 'gen'):
    for dd in ygm[fmt]['decks'].values():
        for sec in dd['recipe'].values():
            for row in sec:
                page_names.add(row[0])
        for row in dd['cards']:
            page_names.add(row[0])
        if dd.get('art'):
            art_names.add(dd['art'])
            page_names.add(dd['art'])
for fmt in ('speed', 'rush'):
    for dd in dldata[fmt]['decks'].values():
        if dd.get('art'):
            art_names.add(dd['art'])
            page_names.add(dd['art'])

# ---------------- Genesys points ----------------
# Genesys points: the YuGiOh Meta card database carries genesysPoints for every card (it already
# includes the 1st anniversary adjustment of 5 Oct 2026 and the points of newer sets)
ygm_gen = json.load(open('src/ygm_genesys.json', encoding='utf-8'))
gen_pts = {}
for c in ygm_gen:
    if c['g'] and c['g'] > 0 and (c['n'] not in gen_pts or not c['alt']):
        gen_pts[c['n']] = c['g']
print('genesys: pointed cards (YuGiOh Meta)', len(gen_pts))

# ---------------- unified card universe ----------------
cards = {}  # name -> dict
for c in ygo:
    cards[c['name']] = {'ygo': c}
dl_by_name = {}
for d in dl_raw:
    if d['n'] not in dl_by_name or (dl_by_name[d['n']]['alt'] and not d['alt']):
        dl_by_name[d['n']] = d
for n, d in dl_by_name.items():
    cards.setdefault(n, {})['dl'] = d
print('cards', len(cards), 'ygo', len(ygo), 'dl', len(dl_by_name))

# official TCG forbidden & limited list (Konami Europe); 0 forbidden, 1 limited, 2 semi-limited
official = json.load(open('src/konami_current.json', encoding='utf-8'))
OFF_BAN, OFF_CHANGES = {}, []
for k in ('0', '1', '2'):
    for c in official[k]:
        nm = htmllib.unescape(c['nameeng'])
        OFF_BAN[nm] = int(k)
        if 'prev' in c:
            OFF_CHANGES.append([nm, int(c['prev']), int(k)])
print('official banlist', official.get('from'), len(OFF_BAN), 'cards,', len(OFF_CHANGES), 'changes')

# DL banStatus -> max copies
def dl_limit(d):
    if d is None:
        return -1
    if (d.get('b') or '') == 'Forbidden':
        return 0
    m = re.match(r'Limited (\d)', d.get('b') or '')
    return int(m.group(1)) if m else 4   # 0 forbidden, 1-3 shared limits, 4 not on the list (3 copies)

BAN_TCG = {'Forbidden': 0, 'Limited': 1, 'Semi-Limited': 2}
def cat_of(n, c):
    y = c.get('ygo')
    if y:
        ty = y.get('type') or ''
        if 'Spell' in ty:
            return 's'
        if 'Trap' in ty:
            return 't'
        if any(k in ty for k in ('Fusion', 'Synchro', 'XYZ', 'Link')):
            return 'e'
        return 'm'
    d = c['dl']
    if d['t'] == 'Spell':
        return 's'
    if d['t'] == 'Trap':
        return 't'
    if any(k in (d.get('mt') or []) for k in ('Fusion', 'Synchro', 'Xyz', 'Link')):
        return 'e'
    return 'm'

# set dates (TCG) and DL set info
tcg_date = {s['set_name']: s.get('tcg_date') for s in tcg_sets_raw}
tcg_set_meta = {s['set_name']: s for s in tcg_sets_raw}
dl_set_info = {s['name']: s for s in dl_sets_raw}

# ---------------- relevance (who gets an image) ----------------
dl_cards_meta = {}
relevant = set(page_names) | set(dl_cards_meta) | set(gen_pts)
for n, c in cards.items():
    y = c.get('ygo')
    if y and (y['staple'] or y['ban'].get('ban_tcg')):
        relevant.add(n)
    d = c.get('dl')
    if d and d.get('b'):
        relevant.add(n)
relevant = {n for n in relevant if n in cards and cards[n].get('ygo')}
print('with image:', len(relevant))

# ---------------- images and sprites ----------------
os.makedirs('raw', exist_ok=True)
os.makedirs('art', exist_ok=True)
os.makedirs('sheets', exist_ok=True)
os.makedirs('data', exist_ok=True)
for f in os.listdir('sheets'):
    os.remove('sheets/' + f)


def fetch_thumb(n):
    y = cards[n]['ygo']
    p = f"raw/{y['id']}.jpg"
    if os.path.exists(p):
        return n, p
    for i in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(y['img'], headers=UA), timeout=60) as r:
                im = Image.open(io.BytesIO(r.read())).convert('RGB')
            im.thumbnail((128, 128))
            im.save(p, quality=80)
            return n, p
        except Exception:
            time.sleep(1)
    return n, None


order = sorted(relevant)
paths = {}
with cf.ThreadPoolExecutor(8) as ex:
    for n, p in ex.map(fetch_thumb, order):
        if p:
            paths[n] = p
print('thumbs', len(paths), 'failed', len(order) - len(paths))

per_sheet = COLS * ROWS
cell_of = {}
sheets = {}
for i, n in enumerate(sorted(paths)):
    s, k = divmod(i, per_sheet)
    sh = sheets.setdefault(s, Image.new('RGB', (CELL * COLS, CELL * ROWS), (10, 20, 50)))
    sh.paste(Image.open(paths[n]).resize((CELL, CELL)), ((k % COLS) * CELL, (k // COLS) * CELL))
    cell_of[n] = (s, k)
for s, sh in sheets.items():
    sh.save(f'sheets/s{s}.jpg', quality=70)

# flagship art (200px)
art_ids = {}
for n in art_names:
    y = (cards.get(n) or {}).get('ygo')
    if not y:
        continue
    p = f"art/{y['id']}.jpg"
    if not os.path.exists(p):
        try:
            with urllib.request.urlopen(urllib.request.Request(y['img'], headers=UA), timeout=60) as r:
                im = Image.open(io.BytesIO(r.read())).convert('RGB')
            im.thumbnail((200, 200))
            im.save(p, quality=72)
        except Exception:
            continue
    art_ids[n] = y['id']

# ---------------- low-res sprites for every other card ----------------
LCELL, LCOLS = 72, 12
LPER = LCOLS * LCOLS
os.makedirs('raw_lo', exist_ok=True)


def fetch_lo(n):
    c = cards[n]
    y, d = c.get('ygo'), c.get('dl')
    key = f"y{y['id']}" if y else f"d{d['id']}"
    p = f'raw_lo/{key}.jpg'
    if os.path.exists(p):
        return n, p
    for i in range(3):
        try:
            url = y['img'] if y else f"https://s3.duellinksmeta.com/cards/{d['id']}_w100.webp"
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                im = Image.open(io.BytesIO(r.read())).convert('RGB')
            if not y:   # full card picture: cut the art box
                w, h = im.size
                x0, y0, side = int(w * .093), int(w * .2535), int(w * .813)
                im = im.crop((x0, y0, x0 + side, y0 + side))
            im = im.resize((LCELL, LCELL), Image.LANCZOS)
            im.save(p, quality=78)
            return n, p
        except Exception:
            time.sleep(1)
    return n, None


lo_names = [n for n in sorted(cards) if n not in paths and (cards[n].get('ygo') or cards[n].get('dl'))]
lo_paths = {}
with cf.ThreadPoolExecutor(6) as ex:
    for i, (n, p) in enumerate(ex.map(fetch_lo, lo_names)):
        if p:
            lo_paths[n] = p
        if i % 1000 == 0:
            print('lo thumbs', i, 'of', len(lo_names), flush=True)
print('lo thumbs', len(lo_paths), 'failed', len(lo_names) - len(lo_paths))
cell_lo = {}
sh_img, cur = None, -1
for i, n in enumerate(sorted(lo_paths)):
    s_, k = divmod(i, LPER)
    if s_ != cur:
        if sh_img is not None:
            sh_img.save(f'sheets/l{cur}.jpg', quality=70)
        sh_img, cur = Image.new('RGB', (LCELL * LCOLS, LCELL * LCOLS), (10, 20, 50)), s_
    sh_img.paste(Image.open(lo_paths[n]), ((k % LCOLS) * LCELL, (k // LCOLS) * LCELL))
    cell_lo[n] = (s_, k)
if sh_img is not None:
    sh_img.save(f'sheets/l{cur}.jpg', quality=70)

def dump_js(name, obj):
    """Data files are classic scripts (<script src>) instead of JSON fetched at runtime: a script
    tag needs no CORS or fetch permission inside the artifact frame."""
    with open(f'data/{name}.js', 'w', encoding='utf-8') as f:
        f.write('__load(' + json.dumps(name) + ',' + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ');')


for f in os.listdir('data'):
    os.remove('data/' + f)

# ---------------- indexes ----------------
names_sorted = sorted(cards)
idx_of = {n: i for i, n in enumerate(names_sorted)}
tcg_set_names = sorted({s[0] for c in ygo for s in c['sets']}, key=lambda s: (tcg_date.get(s) or '0000', s))
tcg_set_idx = {n: i for i, n in enumerate(tcg_set_names)}

dl_set_list = []  # [name, type, rel]
dl_set_idx = {}
def dl_src(kind, name, stype, rel):
    key = (kind, name)
    if key not in dl_set_idx:
        dl_set_idx[key] = len(dl_set_list)
        dl_set_list.append({'n': name, 'kind': kind, 't': stype or '', 'rel': rel or '', 'k': []})
    return dl_set_idx[key]

index_rows = []
chunks = {}
tcg_set_cards = {i: [] for i in range(len(tcg_set_names))}
for i, n in enumerate(names_sorted):
    c = cards[n]
    y, d = c.get('ygo'), c.get('dl')
    flags = 0
    if y and 'TCG' in y['formats']:
        flags |= 1
    released = bool(d and (d.get('rush') or (d.get('rel') and d['rel'] <= TODAY)))
    if d and not d.get('rush') and released:
        flags |= 2
    if d and d.get('rush'):
        flags |= 4
    if y and y['staple']:
        flags |= 8
    ban = -1
    if n in OFF_BAN:
        ban = OFF_BAN[n]
    elif y and flags & 1:
        ban = 3
    gen = gen_pts.get(n)
    if gen is None:
        fp_date = None
        if y:
            ds = [tcg_date.get(s[0]) for s in y['sets'] if tcg_date.get(s[0])]
            fp_date = min(ds) if ds else None
        gen = -1 if (fp_date and fp_date > GEN_BASE_DATE) else 0   # -1: recent card, points unknown
    if not (flags & 1):
        gen = None if gen == 0 else gen
    if y and ('Link' in (y['type'] or '') or 'Pendulum' in (y['type'] or '')):
        gen = -3          # Link and Pendulum monsters cannot be used in Genesys (format rule)
    if n in cell_of:
        s, k = cell_of[n]
    elif n in cell_lo:
        s, k = -2 - cell_lo[n][0], cell_lo[n][1]
    else:
        s, k = -1, -1
    ch = i // CHUNK
    price = -1
    if y and y['tcg']:
        try:
            price = round(float(y['tcg']), 2)
        except Exception:
            price = -1
    lim = dl_limit(d)
    if d and not released and lim == 4:
        lim = 5      # in the Duel Links database but not released yet
    index_rows.append([n, cat_of(n, c), s, k, ban, lim, gen if gen is not None else -2, ch, flags, price, y['id'] if y else 0])

    # detail
    det = {}
    if y:
        det['d'] = y['desc']
        det['ty'] = y['hr']
        det['st'] = [y['atk'], y['def'], y['level'], y['race'], y['attr'], y.get('lk'), y.get('sc')]
        det['p'] = [y['tcg'], y['cm']]
        pr = []
        for sname, code, rc, rn, price in y['sets']:
            num = code.split('-', 1)[1] if '-' in code else code
            try:
                pf = float(price)
            except Exception:
                pf = 0
            pr.append([tcg_set_idx[sname], num, rc.strip('()') or ''.join(w[0] for w in rn.split()).upper(), round(pf, 2)])
            tcg_set_cards[tcg_set_idx[sname]].append([i, num, pr[-1][2], round(pf, 2)])
        pr.sort(key=lambda r: tcg_set_names[r[0]] and (tcg_date.get(tcg_set_names[r[0]]) or ''), reverse=True)
        det['pn'] = pr
    if d and released:
        ob = []
        for kind, sname, stype, amount in d['ob']:
            if kind == 'sets':
                info = dl_set_info.get(sname, {})
                rel = (info.get('release') or '')[:10]
                si = dl_src('set', sname, stype, rel)
                dl_set_list[si]['k'].append([i, amount])
                ob.append(['s', sname, stype, amount, rel])
            elif kind == 'characters':
                si = dl_src('char', sname, 'Personaje', '')
                dl_set_list[si]['k'].append([i, amount])
                ob.append(['c', sname, '', amount, ''])
            else:
                si = dl_src('other', sname, 'Otra vía', '')
                dl_set_list[si]['k'].append([i, amount])
                ob.append(['o', sname, '', amount, ''])
        det['dl'] = {'r': d['r'], 'rel': d['rel'], 'ob': ob, 'rush': bool(d.get('rush'))}
    chunks.setdefault(ch, {})[n] = det

for ch, body in chunks.items():
    dump_js(f'c{ch}', body)

dump_js('index', {'chunk': CHUNK, 'cols': COLS, 'lcols': LCOLS, 'cards': index_rows,
           'tcgsets': [[n, (tcg_date.get(n) or '')[:10], (tcg_set_meta.get(n) or {}).get('set_code') or ''] for n in tcg_set_names],
           'gen': {'base': GEN_BASE_DATE, 'ann': '2026-10-05', 'n': len(gen_pts)},
           'ban': {'from': official.get('from'), 'n': [sum(1 for v in OFF_BAN.values() if v == i) for i in (0, 1, 2)], 'changes': OFF_CHANGES}})

tcg_sets_out = []
for i, sname in enumerate(tcg_set_names):
    m = tcg_set_meta.get(sname, {})
    tcg_sets_out.append({'n': sname, 'd': (m.get('tcg_date') or '')[:10], 'code': m.get('set_code') or '', 'k': tcg_set_cards[i]})
tcg_sets_out.sort(key=lambda s: s['d'], reverse=True)
dump_js('sets-tcg', tcg_sets_out)

# DL sources: include the boxes that exist even without cards, sorted newest first
for sname, info in dl_set_info.items():
    dl_src('set', sname, info.get('type'), (info.get('release') or '')[:10])
dl_out = sorted(dl_set_list, key=lambda s: (s['rel'] or '0000'), reverse=True)
dump_js('sets-dl', dl_out)

# ---------------- small blocks into the page ----------------
genids = {}
for m in re.finditer(r"\[(\d{3,9}),(\d)\]", src):
    pass
by_id = {c['id']: c['name'] for c in ygo}
gen_id_block = re.search(r"const GEN_LIST = .*?\}\)\(\);", src, re.S)
ids = {int(x) for x in re.findall(r"\[(\d{3,9}),\d\]", gen_id_block.group(0))} if gen_id_block else set()
genids = {str(i): by_id[i] for i in ids if i in by_id}

out = src
out = out.replace('/*__ARTS__*/{}', json.dumps(art_ids, ensure_ascii=False))
out = out.replace('/*__ALIAS__*/{}', '{}')
out = out.replace('/*__YGMDATA__*/{}', json.dumps(ygm, ensure_ascii=False, separators=(',', ':')))
out = out.replace("/*__BUILT__*/''", repr(TODAY))
out = out.replace('/*__GENIDS__*/{}', json.dumps(genids, ensure_ascii=False))
out = out.replace('/*__DLDATA__*/{}', json.dumps(dldata, ensure_ascii=False, separators=(',', ':')))
open('index.html', 'w', encoding='utf-8').write(out)

unresolved = sorted(n for n in page_names if n not in cards)
missing_ban = sorted(n for n in OFF_BAN if n not in cards)
print('official banlist names not in the database:', missing_ban)
used_art = {f'{v}.jpg' for v in art_ids.values()}
for f in os.listdir('art'):
    if f not in used_art:
        os.remove('art/' + f)
print('index rows', len(index_rows), 'chunks', len(chunks), 'sheets', len(sheets), 'art', len(art_ids))
print('tcg sets', len(tcg_sets_out), 'dl sources', len(dl_out))
print('page names not in any db:', unresolved)
