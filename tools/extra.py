"""Extra card data that fetch_sources.py does not keep: alternate artworks and Spanish names.
  - YGOPRODeck: every card_images entry (cards with more than one artwork)
  - YGOResources (Konami database mirror): Spanish card names, matched to English names by card id
Writes src/extra.json = {"alts": {name: [passcodes]}, "es": {english name: spanish name}}.
Run from build/:  python tools/extra.py   (add --refresh to download again)
"""
import json, os, sys, urllib.request

UA = {'User-Agent': 'Mozilla/5.0'}
OUT = 'src/extra.json'


def get(url):
    for _ in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
                return json.load(r)
        except Exception as e:
            print('retry', url[:70], e)
    raise SystemExit('failed ' + url)


if os.path.exists(OUT) and '--refresh' not in sys.argv:
    print('extra.json exists')
    sys.exit(0)

api = get('https://db.ygoprodeck.com/api/v7/cardinfo.php')['data']
alts = {c['name']: [i['id'] for i in c['card_images']] for c in api if len(c['card_images']) > 1}
print('cards with alternate art:', len(alts))


# YGOJSON (Konami illustrations, release v1) lists far more alternate artworks than YGOPRODeck's card_images: merge them,
# keeping the original passcode first and dropping any picture YGOPRODeck does not serve.
import concurrent.futures as cf, io, zipfile
SLIM = 'src/ygojson_alts.json'
if not os.path.exists(SLIM):
    with urllib.request.urlopen(urllib.request.Request('https://github.com/iconmaster5326/YGOJSON/releases/download/v1/aggregate.zip', headers=UA), timeout=600) as r:
        z = zipfile.ZipFile(io.BytesIO(r.read()))
    cj = json.loads(z.read('cards.json'))
    slim = {}
    for c in cj:
        imgs = [int(i['password']) for i in c.get('images', []) if i.get('password')]
        nm = (c.get('text', {}).get('en') or {}).get('name')
        if nm and len(imgs) > 1:
            slim[nm] = imgs
    json.dump(slim, open(SLIM, 'w', encoding='utf-8'), separators=(',', ':'))
ygj = json.load(open(SLIM, encoding='utf-8'))
main_id = {c['name']: c['id'] for c in api}


def served(i):
    try:
        with urllib.request.urlopen(urllib.request.Request(f'https://images.ygoprodeck.com/images/cards_small/{i}.jpg', headers=UA, method='HEAD'), timeout=30):
            return True
    except Exception:
        return False


cand = {}
for nm, ids in ygj.items():
    if nm in main_id:
        known = set(alts.get(nm, [main_id[nm]]))
        new = [i for i in ids if i not in known]
        if new:
            cand[nm] = new
flat = sorted({i for v in cand.values() for i in v})
print('candidate extra artworks:', len(flat), 'cards:', len(cand))
with cf.ThreadPoolExecutor(16) as ex:
    ok = dict(zip(flat, ex.map(served, flat)))
for nm, new in cand.items():
    good = [i for i in new if ok[i]]
    if good:
        alts[nm] = list(dict.fromkeys(alts.get(nm, [main_id[nm]]) + good))
print('cards with alternate art after merge:', len(alts), 'artworks:', sum(len(v) for v in alts.values()))

en_idx = get('https://db.ygoresources.com/data/idx/card/name/en')
es_idx = get('https://db.ygoresources.com/data/idx/card/name/es')
es_of_id = {}
for name, ids in es_idx.items():
    for i in ids:
        es_of_id.setdefault(i, name)
es = {}
for name, ids in en_idx.items():
    for i in ids:
        if i in es_of_id and es_of_id[i] != name:
            es[name] = es_of_id[i]
            break
print('spanish names:', len(es), 'of', len(en_idx))
json.dump({'alts': alts, 'es': es}, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
