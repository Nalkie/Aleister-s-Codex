"""Precio de mercado de TCGplayer de CADA versión (impresión) de cada carta -> src/tcgprices.json = {productId: [mercado, más bajo]}.   Run from the project root:  python tools/fetch_tcg_prices.py

Usa la misma búsqueda pública del mercado de TCGplayer que tools/tcgp.py (una consulta por página de 50 productos de cada expansión) y se queda con marketPrice y lowestPrice
(en dólares, null si no hay). El productId es el mismo que tools/tcgp.py guarda en src/tcgplayer.json y que la página usa para la foto de cada versión.
Los precios por impresión de YGOPRODeck (set_price) casi siempre vienen en 0, por eso se piden acá: tools/prices.py los pone en los datos."""
import concurrent.futures as cf, json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/json', 'Origin': 'https://www.tcgplayer.com', 'Referer': 'https://www.tcgplayer.com/'}
URL = 'https://mp-search-api.tcgplayer.com/v1/search/request?q=&isList=true'


def body(name, frm, size=50):
    term = {"productLineName": ["yugioh"]}
    if name:
        term["setName"] = [name]
    return {"algorithm": "sales_synonym_v2", "from": frm, "size": size, "filters": {"term": term, "range": {}, "match": {}},
            "listingSearch": {"filters": {"term": {}, "range": {}, "exclude": {"channelExclusion": 0}}}, "context": {"cart": {}, "shippingCountry": "US"}, "sort": {}}


def page(name, frm):
    for i in range(4):
        try:
            req = urllib.request.Request(URL, data=json.dumps(body(name, frm)).encode(), headers=H)
            return json.load(urllib.request.urlopen(req, timeout=40))['results'][0]
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def num(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return round(x, 2) if x > 0 else None


def one_set(name):
    out, frm, total = {}, 0, None
    while total is None or frm < total:
        r = page(name, frm)
        if not r:
            return name, None
        total = r['totalResults']
        for x in r['results']:
            if (x.get('customAttributes') or {}).get('number'):
                out[int(x['productId'])] = [num(x.get('marketPrice')), num(x.get('lowestPrice'))]
        frm += 50
        if total > 10000:
            break
        time.sleep(0.15)
    return name, out


if __name__ == '__main__':
    os.chdir(ROOT)
    sets = [s['set_name'] for s in json.load(open('src/cardsets.json', encoding='utf-8'))]
    first = page(None, 0)
    if first:
        sets += [x['value'] for x in first['aggregations']['setName'] if x['value'] not in sets]
    prices, failed = {}, []
    with cf.ThreadPoolExecutor(4) as ex:
        for i, (name, got) in enumerate(ex.map(one_set, sets), 1):
            if got is None:
                failed.append(name)
            else:
                prices.update(got)
            if i % 100 == 0:
                print(i, 'of', len(sets), 'products so far', len(prices), flush=True)
    if len(prices) < 20000:       # something went wrong (blocked, offline): keep what was there
        sys.exit('only %d products priced: the previous src/tcgprices.json is kept' % len(prices))
    json.dump(prices, open('src/tcgprices.json', 'w'), separators=(',', ':'))
    print('products', len(prices), '| with market price', sum(1 for v in prices.values() if v[0]), '| sets that failed', len(failed), failed[:5])
