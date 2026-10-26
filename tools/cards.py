"""Build step: scan src.html for card names, resolve them (plus staples and the TCG banlist)
against the YGOPRODeck API, pack 128px thumbnails into sprite sheets and write index.html.
Run from build/:  python -I tools/cards.py
"""
import io, json, os, re, sys, time, urllib.parse, urllib.request
from PIL import Image

API = 'https://db.ygoprodeck.com/api/v7/cardinfo.php?'
UA = {'User-Agent': 'meta-page/2'}
CELL, COLS, ROWS = 128, 8, 8
GEN_IDS = [11895663, 84401954, 58916810, 22912101, 85523502, 12266229, 88570003, 97631303, 59438930, 102380,
           18738846, 37654623, 64049762, 433377, 22283204, 25789292, 59921227, 23526128,
           59400890, 73452089, 85899505, 85059922, 98502113, 58071334, 7894706, 21281085, 72444406, 37675907,
           70980824, 15123983, 18969888,
           34267821, 26084285, 67750322, 8267140, 66236707, 65703851]
ALIASES = {}


def get(q):
    try:
        with urllib.request.urlopen(urllib.request.Request(API + q, headers=UA), timeout=60) as r:
            return json.load(r)['data']
    except Exception:
        return None


def fetch_img(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return Image.open(io.BytesIO(r.read())).convert('RGB')


src = open('src.html', encoding='utf-8').read()
names = set()
STR = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"")
for m in re.finditer(r"\b[PN]\(\[(.*?)\]", src, re.S):
    for q in STR.finditer(m.group(1)):
        names.add((q.group(1) if q.group(1) is not None else q.group(2)).replace("\\'", "'"))
for m in re.finditer(r"art:'([^']*)'", src):
    names.add(m.group(1))
for m in re.finditer(r"^\s*\d+x (.+?)\s*$", src, re.M):
    names.add(m.group(1).split('`')[0])
art_names = {m.group(1) for m in re.finditer(r"art:'([^']*)'", src)}
DLDATA = json.load(open('dl/dldata.json', encoding='utf-8'))
for fmt in ('speed', 'rush'):
    for dd in DLDATA[fmt]['decks'].values():
        for sec in dd['recipe'].values():
            for row in sec:
                names.add(row[0])
# set release dates (for first-print lookup)
SETDATES = {}
try:
    with urllib.request.urlopen(urllib.request.Request('https://db.ygoprodeck.com/api/v7/cardsets.php', headers=UA), timeout=60) as r:
        for st in json.load(r):
            if st.get('tcg_date'):
                SETDATES[st['set_name']] = st['tcg_date']
except Exception as e:
    print('cardsets failed', e)
print('sets with dates', len(SETDATES))


cards = {}   # canonical name -> record
unresolved = []


def add(rec):
    cards[rec['name']] = rec


# staples and TCG banlist
for q in ('staple=yes', 'banlist=tcg'):
    for c in get(q) or []:
        add(c)
for gid in range(0, len(GEN_IDS), 20):
    for c in get('id=' + ','.join(map(str, GEN_IDS[gid:gid + 20]))) or []:
        add(c)
alias = {}
for n in sorted(names):
    if n in cards:
        continue
    q = ALIASES.get(n, n)
    d = get('name=' + urllib.parse.quote(q)) or get('fname=' + urllib.parse.quote(q))
    time.sleep(0.05)
    if d:
        add(d[0])
        alias[n] = d[0]['name']
    else:
        unresolved.append(n)
print('cards', len(cards), 'unresolved', unresolved)

os.makedirs('raw', exist_ok=True)
os.makedirs('art', exist_ok=True)
os.makedirs('sheets', exist_ok=True)
for f in os.listdir('sheets'):
    os.remove('sheets/' + f)

ordered = sorted(cards.values(), key=lambda c: c['name'])
per_sheet = COLS * ROWS
db = {}
sheets = {}
fails = []
for i, c in enumerate(ordered):
    path = f"raw/{c['id']}.jpg"
    if not os.path.exists(path):
        try:
            im = fetch_img(c['card_images'][0]['image_url_cropped'])
            im = im.resize((CELL, CELL))
            im.save(path, quality=80)
            time.sleep(0.05)
        except Exception:
            fails.append(c['name'])
            continue
    s, k = divmod(len(db), per_sheet)
    sheet = sheets.setdefault(s, Image.new('RGB', (CELL * COLS, CELL * ROWS), (10, 20, 50)))
    sheet.paste(Image.open(path), ((k % COLS) * CELL, (k // COLS) * CELL))
    desc = (c.get('desc') or '').replace('\r', '')
    if len(desc) > 420:
        desc = desc[:417] + '...'
    ban = (c.get('banlist_info') or {}).get('ban_tcg', '')
    prints = [x for x in c.get('card_sets', []) if x.get('set_name') in SETDATES]
    first = min(prints, key=lambda x: SETDATES[x['set_name']]) if prints else None
    rar = []
    for x in c.get('card_sets', []):
        code = (x.get('set_rarity_code') or '').strip('()') or ''.join(w[0] for w in x.get('set_rarity', '').split()).upper()
        if code and code not in rar:
            rar.append(code)
    pr = (c.get('card_prices') or [{}])[0]
    def num(v):
        try:
            return round(float(v), 2)
        except Exception:
            return None
    info = [first['set_name'], first['set_code'], SETDATES[first['set_name']][:7]] if first else None
    db[c['name']] = [s, k, c.get('humanReadableCardType', c.get('type', '')), ban,
                     0, desc, info, rar[:9], num(pr.get('tcgplayer_price')), num(pr.get('cardmarket_price')), len(c.get('card_sets', []))]
for s, im in sheets.items():
    im.save(f'sheets/s{s}.jpg', quality=72)

# staple flag
for c in get('staple=yes') or []:
    if c['name'] in db:
        db[c['name']][4] = 1

# flagship art (200px individual files)
art_ids = {}
for n in art_names:
    cn = alias.get(n, n)
    c = cards.get(cn)
    if not c:
        continue
    p = f"art/{c['id']}.jpg"
    if not os.path.exists(p):
        try:
            im = fetch_img(c['card_images'][0]['image_url_cropped'])
            im.thumbnail((200, 200))
            im.save(p, quality=72)
        except Exception:
            continue
    art_ids[n] = c['id']

# names as used in src -> canonical db names (aliases)
name_map = {n: a for n, a in alias.items() if n != a}
gen_names = {}
for c in cards.values():
    if c['id'] in GEN_IDS:
        gen_names[c['id']] = c['name']

out = src
out = out.replace('/*__CARDS__*/{}', json.dumps(db, ensure_ascii=False, separators=(',', ':')))
out = out.replace('/*__ARTS__*/{}', json.dumps(art_ids, ensure_ascii=False))
out = out.replace('/*__DLDATA__*/{}', json.dumps(DLDATA, ensure_ascii=False, separators=(',', ':')))
out = out.replace('/*__ALIAS__*/{}', json.dumps(name_map, ensure_ascii=False))
out = out.replace('/*__GENIDS__*/{}', json.dumps({str(k): v for k, v in gen_names.items()}, ensure_ascii=False))
open('index.html', 'w', encoding='utf-8').write(out)

used_art = {f'{v}.jpg' for v in art_ids.values()}
for f in os.listdir('art'):
    if f not in used_art and f.endswith('.jpg') and f[:-4].isdigit():
        os.remove('art/' + f)
print('db', len(db), 'sheets', len(sheets), 'art', len(art_ids), 'img fails', fails)
missing = [n for n in names if alias.get(n, n) not in db]
print('names without image:', sorted(missing))
