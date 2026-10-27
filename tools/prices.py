"""Precios por tienda y dólar blue en los datos de la página.  Edita data/index.js y data/c<N>.js.  Run from the project root after tools/build_db.py y ANTES de tools/rushprice.py:
  python tools/prices.py
  * data/c<N>.js, campo p de cada carta: [TCGplayer US$, Cardmarket €, eBay US$, CoolStuffInc US$, Amazon US$] (null si la tienda no tiene precio).
  * data/index.js, columna de precio: cuando una carta no tiene precio en TCGplayer se usa el de otra tienda (Cardmarket pasado a dólares, o la mediana de eBay,
    CoolStuffInc y Amazon) y se marca con la bandera 32.  Lo que sigue sin precio lo estima tools/rushprice.py (bandera 16).
  * data/index.js, campo fx: dólar blue (compra y venta) y euro -> dólar, para mostrar los precios también en pesos argentinos.
Correrlo dos veces da lo mismo."""
import json, os, re, statistics, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRICE, FLAGS = 9, 8
FLAG_EST, FLAG_STORE = 16, 32


def load(path):
    t = open(path, encoding='utf-8').read()
    head = t[:t.index(',') + 1]
    return head, json.loads(t[len(head):-2])


def save(path, head, obj):
    open(path, 'w', encoding='utf-8').write(head + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ');')


def store_price(row, eur_usd):
    """Precio en dólares de una carta que no está en TCGplayer: Cardmarket convertido, o la mediana de eBay, CoolStuffInc y Amazon. None si no hay."""
    tcg, cm, eb, cs, am = (row + [None] * 5)[:5]
    if tcg:
        return None
    if cm:
        return round(cm * eur_usd, 2)
    others = [x for x in (eb, cs, am) if x]
    return round(statistics.median(others), 2) if others else None


JUNK = 0.02       # US$: por debajo de esto, el «más bajo en venta» no representa a la carta


def version_prices(det, tp):
    """Precio real de TCGplayer de cada versión (impresión), por productId: el más bajo en venta, y si no hay publicaciones, el de mercado.
    Si el más bajo es de JUNK dólares o menos y el de mercado es mayor, se usa el de mercado. Marca la fuente en el sexto lugar de la impresión: 0 = más bajo en venta, 1 = mercado (no hay publicaciones), 2 = mercado (el más bajo es de centavos). Devuelve cuántas impresiones cambió."""
    n = 0
    for d in det.values():
        for p in d.get('pn') or []:
            pid = p[4] if len(p) > 4 else 0
            v = tp.get(str(pid)) if pid else None
            if not v:
                continue
            market, lowest = v
            if lowest and lowest <= JUNK and market and market > lowest:
                new, src = market, 2      # un «más bajo» de centavos es una publicación suelta, no el precio de la carta
            else:
                new, src = (lowest, 0) if lowest else (market, 1) if market else (None, None)
            if new is None:
                continue
            while len(p) < 6:
                p.append(0)
            if p[3] != new or p[5] != src:
                p[3], p[5] = new, src
                n += 1
    return n


def version_ratios(ref, min_n=30):
    """Para estimar el precio de una versión de una carta sin ninguna impresión con precio: por rareza (con al menos min_n muestras), cuánto suelen valer las impresiones respecto del precio de su carta (k) y cuántas muestras hay (n).
    Los precios por impresión (YGOPRODeck, set_price) no están en la misma escala que el de la carta, por eso se miden entre sí."""
    vals, ratios = {}, {}
    for f in sorted(x for x in os.listdir('data') if re.fullmatch(r'c\d+\.js', x)):
        _, det = load('data/' + f)
        for name, d in det.items():
            for p in d.get('pn') or []:
                if p[3] and p[3] > 0:
                    vals.setdefault(p[2], []).append(p[3])
                    if ref.get(name):
                        ratios.setdefault(p[2], []).append(p[3] / ref[name])
    return {r: {'n': len(ratios[r]), 'k': round(statistics.median(ratios[r]), 2)} for r in ratios if len(ratios[r]) >= min_n}


def apply(rows, prices, eur_usd):
    """Pone el precio de otra tienda en las filas sin precio de TCGplayer. Devuelve cuántas cambió."""
    n = 0
    for r in rows:
        if r[FLAGS] & (FLAG_STORE | FLAG_EST):         # parte siempre del estado de TCGplayer: dos corridas dan lo mismo (tools/rushprice.py recalcula las estimadas después)
            r[PRICE], r[FLAGS] = -1, r[FLAGS] & ~(FLAG_STORE | FLAG_EST)
        if r[PRICE] == 0:                              # TCGplayer lo lista en 0,00: es «sin precio», no una carta gratis
            r[PRICE] = -1
        p = prices.get(r[0])
        if not p or r[PRICE] > 0:
            continue
        usd = store_price(p, eur_usd)
        if usd:
            r[PRICE], r[FLAGS] = usd, r[FLAGS] | FLAG_STORE
            n += 1
    return n


if __name__ == '__main__':
    os.chdir(ROOT)
    prices = json.load(open('src/prices.json', encoding='utf-8'))
    fx = json.load(open('src/fx_ars.json'))
    eur = fx['eur_usd']['rate']
    hi, idx = load('data/index.js')
    rows = idx['cards']
    n = apply(rows, prices, eur)
    idx['fx'] = {'ars': fx['blue']['sell'], 'arsBuy': fx['blue']['buy'], 'date': fx['blue']['date'], 'src': fx['blue']['src'], 'eur': eur}
    save('data/index.js', hi, idx)
    tp = json.load(open('src/tcgprices.json')) if os.path.exists('src/tcgprices.json') else {}
    chunks = sorted(x for x in os.listdir('data') if re.fullmatch(r'c\d+\.js', x))
    nver = 0
    for f in chunks:          # primero el precio de cada versión: la estimación de la página y las proporciones por rareza (vr) parten de ahí
        head, det = load('data/' + f)
        k = version_prices(det, tp)
        if k:
            save('data/' + f, head, det)
        nver += k
    ref = {r[0]: r[PRICE] for r in rows if r[PRICE] > 0 and not r[FLAGS] & FLAG_EST}
    vr = version_ratios(ref)
    idx['vr'] = vr
    save('data/index.js', hi, idx)
    changed = 0
    for f in chunks:
        head, det = load('data/' + f)
        ch = False
        for name, d in det.items():
            old = d.get('p')
            new = prices.get(name)
            if new is None and old is not None:                      # ninguna tienda la lista: se conserva lo que había, con cinco lugares
                num = lambda v: round(float(v), 2) if v not in (None, '') and float(v) > 0 else None
                new = [num(x) for x in old[:5]] + [None] * (5 - len(old[:5]))
            if new is not None and old != new:
                d['p'] = new
                ch = True
        if ch:
            save('data/' + f, head, det)
            changed += 1
    print('versiones con el precio real de TCGplayer:', nver, '| cartas con el precio de otra tienda:', n, '| archivos de detalle actualizados:', changed, '| dólar blue (venta):', fx['blue']['sell'], fx['blue']['date'])
