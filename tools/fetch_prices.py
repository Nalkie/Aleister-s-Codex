"""Precios de las cartas en cinco tiendas y el dólar blue -> src/prices.json y src/fx_ars.json.   Run from the project root:  python tools/fetch_prices.py

  src/prices.json : {nombre de carta: [TCGplayer US$, Cardmarket €, eBay US$, CoolStuffInc US$, Amazon US$]} (null cuando la tienda no tiene precio).
                    Sale de YGOPRODeck (campo card_prices), que junta esas cinco tiendas. TrollAndToad no publica API de precios y no se puede
                    consultar en bloque sin saltarse sus reglas: no se incluye.
  src/fx_ars.json : dólar blue (compra y venta, pesos argentinos por US$) de dolarapi.com (Bluelytics de respaldo) y euro -> dólar de Frankfurter (ECB).
No hay una fuente pública de «última venta» por carta: lo que no tiene precio en ninguna tienda se estima en tools/rushprice.py (mediana de cartas parecidas).
"""
import json, os, sys, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {'User-Agent': 'aleisters-codex'}


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                return json.load(r)
        except Exception as e:
            print('retry', url[:70], e, flush=True)
            time.sleep(2)
    raise SystemExit('failed ' + url)


def num(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return round(x, 2) if x > 0 else None


def prices():
    raw = get('https://db.ygoprodeck.com/api/v7/cardinfo.php')['data']
    out = {}
    for c in raw:
        p = (c.get('card_prices') or [{}])[0]
        row = [num(p.get(k)) for k in ('tcgplayer_price', 'cardmarket_price', 'ebay_price', 'coolstuffinc_price', 'amazon_price')]
        if any(row):
            out[c['name']] = row
    return out


def blue():
    try:
        j = get('https://dolarapi.com/v1/dolares/blue')
        return {'buy': float(j['compra']), 'sell': float(j['venta']), 'date': j['fechaActualizacion'][:10], 'src': 'dolarapi.com'}
    except SystemExit:
        j = get('https://api.bluelytics.com.ar/v2/latest')['blue']
        return {'buy': float(j['value_buy']), 'sell': float(j['value_sell']), 'date': time.strftime('%Y-%m-%d'), 'src': 'Bluelytics'}


def eur_usd():
    j = get('https://api.frankfurter.dev/v1/latest?base=EUR&symbols=USD')
    return {'rate': j['rates']['USD'], 'date': j['date']}


if __name__ == '__main__':
    os.chdir(ROOT)
    p = prices()
    json.dump(p, open('src/prices.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    b, e = blue(), eur_usd()
    json.dump({'blue': b, 'eur_usd': e}, open('src/fx_ars.json', 'w'), separators=(',', ':'))
    print('prices', len(p), '| blue', b['buy'], b['sell'], b['date'], b['src'], '| EUR/USD', e['rate'], e['date'])
