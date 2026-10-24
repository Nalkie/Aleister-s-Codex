"""TCGplayer product ids for every TCG printing, so the page can show the real card picture of each rarity
(product-images.tcgplayer.com/fit-in/437x437/<productId>.jpg).
Reads src/cardsets.json (set names), queries TCGplayer's public marketplace search once per set page (50 products, 4 parallel requests, retries),
writes src/tcgplayer.json = {set name: [[number, rarityName, productId], ...]}. Resumable: sets already in the file are skipped.
Run from build/:  python tools/tcgp.py"""
import concurrent.futures as cf, json, os, time, urllib.request

OUT = 'src/tcgplayer.json'
sets = [s['set_name'] for s in json.load(open('src/cardsets.json', encoding='utf-8'))]
# TCGplayer names some sets differently ("(Worldwide English)", "Special Edition" without colon...): also fetch every set it lists
_H = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json', 'Origin': 'https://www.tcgplayer.com', 'Referer': 'https://www.tcgplayer.com/'}
_b = {"algorithm": "sales_synonym_v2", "from": 0, "size": 1, "filters": {"term": {"productLineName": ["yugioh"]}, "range": {}, "match": {}}, "listingSearch": {"filters": {"term": {}, "range": {}, "exclude": {"channelExclusion": 0}}}, "context": {"cart": {}, "shippingCountry": "US"}, "sort": {}}
try:
    _r = json.load(urllib.request.urlopen(urllib.request.Request('https://mp-search-api.tcgplayer.com/v1/search/request?q=&isList=true', data=json.dumps(_b).encode(), headers=_H), timeout=60))['results'][0]
    sets += [x['value'] for x in _r['aggregations']['setName'] if x['value'] not in sets]
except Exception as e:
    print('could not list TCGplayer sets', e)
done = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
H = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json', 'Origin': 'https://www.tcgplayer.com', 'Referer': 'https://www.tcgplayer.com/'}


def page(name, frm):
    body = {"algorithm": "sales_synonym_v2", "from": frm, "size": 50,
            "filters": {"term": {"productLineName": ["yugioh"], "setName": [name]}, "range": {}, "match": {}},
            "listingSearch": {"filters": {"term": {}, "range": {}, "exclude": {"channelExclusion": 0}}},
            "context": {"cart": {}, "shippingCountry": "US"}, "sort": {}}
    for i in range(4):
        try:
            req = urllib.request.Request('https://mp-search-api.tcgplayer.com/v1/search/request?q=&isList=true', data=json.dumps(body).encode(), headers=H)
            return json.load(urllib.request.urlopen(req, timeout=40))['results'][0]
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def one_set(name):
    rows, frm, total = [], 0, None
    while total is None or frm < total:
        r = page(name, frm)
        if not r:
            return name, None
        total = r['totalResults']
        for x in r['results']:
            ca = x.get('customAttributes') or {}
            if x.get('setName') == name and ca.get('number'):
                rows.append([ca['number'], x.get('rarityName') or '', int(x['productId'])])
        frm += 50
        if total > 10000:    # the search API stops at 10k results: never the case for one set
            break
        time.sleep(0.15)
    return name, rows


if '--refresh' in __import__('sys').argv:     # recent and upcoming sets get new cards listed over time
    import datetime, refreshlib
    dates = {s['set_name']: (s.get('tcg_date') or '') for s in json.load(open('src/cardsets.json', encoding='utf-8'))}
    cutoff = (datetime.date.today() - datetime.timedelta(days=150)).isoformat()
    for name in refreshlib.stale_sets(done, dates, cutoff):
        done.pop(name)
todo = [n for n in sets if n not in done]
print('sets to fetch', len(todo), flush=True)
n = 0
with cf.ThreadPoolExecutor(4) as ex:
    for name, rows in ex.map(one_set, todo):
        if rows is not None:
            done[name] = rows
        n += 1
        if n % 50 == 0:
            json.dump(done, open(OUT, 'w', encoding='utf-8'), separators=(',', ':'))
            print(n, 'of', len(todo), 'prints so far', sum(len(v) for v in done.values()), flush=True)
json.dump(done, open(OUT, 'w', encoding='utf-8'), separators=(',', ':'))
print('done: sets', len(done), 'prints', sum(len(v) for v in done.values()))
