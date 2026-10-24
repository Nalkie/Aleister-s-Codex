"""Download the raw sources once and keep slim copies under src/.
  - YGOPRODeck: every card (misc=yes) and the set list with TCG dates
  - Duel Links Meta: every card with acquisition data, and the set list
Run from build/:  python tools/fetch_sources.py
"""
import json, os, time, urllib.request, urllib.parse

UA = {'User-Agent': 'Mozilla/5.0'}
os.makedirs('src', exist_ok=True)
os.makedirs('dl', exist_ok=True)
import sys
if '--refresh' in sys.argv:   # re-download everything that changes over time
    for f in ('src/ygo_all.json', 'src/cardsets.json', 'src/dl_cards.json', 'src/dl_sets.json', 'src/dl_bans.json',
              'src/ygm_topdecks.json', 'dl/topdecks.json', 'src/konami_current.json', 'src/ygm_genesys.json'):
        if os.path.exists(f):
            os.remove(f)


def get(url, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
                return json.load(r)
        except Exception as e:
            print('retry', url[:80], e)
            time.sleep(2)
    raise SystemExit('failed ' + url)


# --- YGOPRODeck ---
if not os.path.exists('src/ygo_all.json'):
    raw = get('https://db.ygoprodeck.com/api/v7/cardinfo.php?misc=yes')['data']
    slim = []
    for c in raw:
        mi = (c.get('misc_info') or [{}])[0]
        pr = (c.get('card_prices') or [{}])[0]
        slim.append({
            'id': c['id'], 'name': c['name'], 'type': c.get('type'), 'hr': c.get('humanReadableCardType'),
            'desc': c.get('desc', ''), 'atk': c.get('atk'), 'def': c.get('def'), 'level': c.get('level'),
            'race': c.get('race'), 'attr': c.get('attribute'), 'lk': c.get('linkval'), 'sc': c.get('scale'), 'ban': c.get('banlist_info') or {},
            'sets': [[s['set_name'], s['set_code'], s.get('set_rarity_code') or '', s.get('set_rarity') or '', s.get('set_price') or '0']
                     for s in c.get('card_sets', [])],
            'tcg': pr.get('tcgplayer_price'), 'cm': pr.get('cardmarket_price'),
            'formats': mi.get('formats') or [], 'staple': mi.get('staple') == 'Yes', 'tcg_date': mi.get('tcg_date'),
            'img': (c.get('card_images') or [{}])[0].get('image_url_cropped'),
        })
    json.dump(slim, open('src/ygo_all.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('ygo cards', len(slim))
if not os.path.exists('src/cardsets.json'):
    sets = get('https://db.ygoprodeck.com/api/v7/cardsets.php')
    json.dump(sets, open('src/cardsets.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('sets', len(sets))

# --- Duel Links Meta ---
B = 'https://www.duellinksmeta.com/api/v1/'
if not os.path.exists('src/dl_cards.json'):
    FIELDS = 'name,konamiID,type,monsterType,rarity,release,banStatus,obtain,alternateArt,gameId,rush'
    out, skip = [], 0
    while True:
        page = get(B + f'cards?limit=500&skip={skip}&fields={FIELDS}')
        if not page:
            break
        for c in page:
            ob = []
            for o in c.get('obtain', []):
                s = o.get('source') or {}
                ob.append([o.get('type'), s.get('name'), s.get('type'), o.get('amount'), o.get('subSource')])   # subSource: how a character gives the card (Starter Deck, Drop, ...)
            out.append({'id': c.get('_id'), 'n': c['name'], 'k': c.get('konamiID'), 't': c.get('type'), 'mt': c.get('monsterType') or [], 'r': c.get('rarity'),
                        'rel': (c.get('release') or '')[:10], 'b': c.get('banStatus'), 'alt': bool(c.get('alternateArt')),
                        'rush': c.get('rush'), 'ob': ob})
        skip += len(page)
        print('dl cards', skip)
        time.sleep(0.2)
    json.dump(out, open('src/dl_cards.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
if not os.path.exists('src/dl_sets.json'):
    sets = get(B + 'sets?limit=1000')
    json.dump(sets, open('src/dl_sets.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('dl sets', len(sets))
if not os.path.exists('src/dl_bans.json'):
    out, skip = [], 0
    while True:
        page = get(B + f'cards?limit=500&skip={skip}&fields=name,banStatus,tcgBanStatus,alternateArt,rush')
        if not page:
            break
        out += page
        skip += len(page)
    json.dump(out, open('src/dl_bans.json', 'w', encoding='utf-8'), ensure_ascii=False)
# --- official TCG forbidden & limited list (Konami, Europe) ---
if not os.path.exists('src/konami_current.json'):
    cur = get('https://www.yugioh-card.com/eu/_data/fllists/current.json')
    json.dump(cur, open('src/konami_current.json', 'w', encoding='utf-8'), ensure_ascii=False)
    print('official banlist effective', cur.get('from'), {k: len(v) for k, v in cur.items() if isinstance(v, list)})

# --- Genesys points for every card (YuGiOh Meta card database) ---
if not os.path.exists('src/ygm_genesys.json'):
    gen, skip = [], 0
    while True:
        page = get(f'https://www.yugiohmeta.com/api/v1/cards?limit=500&skip={skip}&fields=name,genesysPoints,tcgRelease,alternateArt')
        if not page:
            break
        gen += [{'n': c['name'], 'g': c.get('genesysPoints'), 'rel': (c.get('tcgRelease') or '')[:10], 'alt': bool(c.get('alternateArt'))} for c in page]
        skip += len(page)
    json.dump(gen, open('src/ygm_genesys.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('genesys points rows', len(gen), 'pointed', sum(1 for c in gen if c['g']))

# --- latest tournament decks (the meta itself) ---
if not os.path.exists('dl/topdecks.json'):
    allp = []
    for skip in range(0, 1500, 300):
        allp += get(B + f'top-decks?sort=-created&limit=300&skip={skip}')
    json.dump(allp, open('dl/topdecks.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('dl top decks', len(allp))
if not os.path.exists('src/ygm_topdecks.json'):
    YB = 'https://www.yugiohmeta.com/api/v1/top-decks?limit=300&skip='
    lo, hi = 20000, 60000     # the list is oldest-first: find its end, then take the last 3300 records
    while hi - lo > 300:
        mid = (lo + hi) // 2
        if get(YB.replace('limit=300', 'limit=1') + str(mid)):
            lo = mid
        else:
            hi = mid
    total = hi
    tail = []
    for skip in range(max(0, total - 3300), total + 300, 300):
        page = get(YB + str(skip))
        if not page:
            break
        tail += page
        time.sleep(0.2)
    json.dump(tail, open('src/ygm_topdecks.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('yugiohmeta top decks', len(tail))
print('done')
