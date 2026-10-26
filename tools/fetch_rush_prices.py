"""Rush Duel prices -> src/yuyutei_rush.json (+ src/rush_names.json, src/fx.json).   Run from the project root:  python tools/fetch_rush_prices.py
Rush Duel cards are not sold in the TCG, so TCGplayer has no price for them. The Japanese shop Yuyu-tei (yuyu-tei.jp) lists every Rush Duel set with the price in yen:
  * yuyutei_rush.json : one row per listing (set, card number, rarity, Japanese name, yen, stock, url). One request per set, 1 second apart (the site's crawl delay).
  * rush_names.json   : Japanese -> English name of every Rush Duel card, from the Yugipedia semantic API (needed to match a listing with a card).
  * fx.json           : yen -> US dollar rate of the day (Frankfurter, ECB reference rates).
Prices are the shop's selling price, not a market average. Tools/rushprice.py does the matching offline."""
import json, os, re, sys, time, unicodedata, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'Mozilla/5.0'}
SET_CODES = ([f'rdkp{i:02d}' for i in range(1, 31)] + [f'rdlp{i:02d}' for i in range(1, 6)] + [f'rdca{i:02d}' for i in range(1, 4)] + [f'rdbt{i:02d}' for i in range(1, 4)]
             + [f'rdst{i:02d}' for i in range(1, 4)] + ['rdpr01', 'rdprd', 'rdprb'] + [f'rdsd{i:02d}' for i in range(1, 6)] + [f'rdsp{i:02d}' for i in range(1, 3)]
             + [f'rdpp{i:02d}' for i in range(1, 3)] + [f'rdgp{i:02d}' for i in range(1, 3)] + [f'rddb{i:02d}' for i in range(1, 3)] + [f'rdtp{i:02d}' for i in range(1, 3)])


def norm(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s or '')).lower()


def parse_listing(html, code):
    out = []
    for b in html.split('class="card-product')[1:]:
        m = re.search(r'alt="(RD/\S+)\s+(\S+)\s+([^"]*)"', b)   # the card picture, not the star icon of the favourites button
        pr = re.search(r'<strong[^>]*>\s*([\d,]+)\s*円', b)
        nm = re.search(r'<h4[^>]*>([^<]+)</h4>', b)
        ln = re.search(r'href="(https://yuyu-tei\.jp/sell/yrd/card/[^"]+)"', b)
        if m and pr and nm:
            stock = re.search(r'在庫\s*:\s*(\d+)', b)
            out.append({'set': code, 'no': m.group(1), 'rar': m.group(2), 'ja': nm.group(1).strip(), 'jpy': int(pr.group(1).replace(',', '')),
                        'stock': int(stock.group(1)) if stock else 0, 'url': ln.group(1) if ln else ''})
    return out


def plain_ja(x):
    x = re.sub(r'<rt>.*?</rt>|<rp>.*?</rp>', '', x or '')
    return re.sub(r'<[^>]+>', '', x)


def get(u, tries=3):
    for i in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60).read().decode('utf-8', 'replace')
        except Exception as e:
            err = e
            time.sleep(2 * (i + 1))
    print('failed', u, err, flush=True)
    return ''


if __name__ == '__main__':
    os.chdir(ROOT)
    rows = []
    for code in SET_CODES:
        h = get('https://yuyu-tei.jp/sell/yrd/s/' + code)
        r = parse_listing(h, code) if len(h) > 150000 else []
        rows += r
        print(code, len(r), flush=True)
        time.sleep(1)
    json.dump(rows, open('src/yuyutei_rush.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    names, off = {}, 0
    while True:
        q = '[[Category:Rush Duel cards]]|?Japanese name|?English name|limit=500|offset=%d' % off
        d = json.loads(get('https://yugipedia.com/api.php?action=ask&format=json&query=' + urllib.parse.quote(q)))
        res = d.get('query', {}).get('results', {})
        for title, v in res.items():
            p = v.get('printouts', {})
            ja, en = (p.get('Japanese name') or [''])[0], (p.get('English name') or [''])[0]
            if ja and en:
                names[norm(plain_ja(ja))] = plain_ja(en)
        nxt = d.get('query-continue-offset')
        print('names', len(names), flush=True)
        if not nxt:
            break
        off = nxt
        time.sleep(0.5)
    json.dump(names, open('src/rush_names.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    fx = json.loads(get('https://api.frankfurter.dev/v1/latest?base=JPY&symbols=USD'))
    json.dump({'JPY_USD': fx['rates']['USD'], 'date': fx['date'], 'source': 'Frankfurter (ECB)'}, open('src/fx.json', 'w'))
    print('listings', len(rows), 'names', len(names), 'fx', fx['rates']['USD'], fx['date'])
