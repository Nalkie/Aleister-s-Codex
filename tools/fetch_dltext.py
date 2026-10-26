"""Card text for the cards that only exist in Duel Links (every Rush Duel card and the Speed Duel cards with no TCG print) -> src/dl_text.json.
YGOPRODeck has no Rush Duel cards, so their effect, type, level, ATK/DEF come from the Duel Links Meta card API. Keyed by the Duel Links Meta card id.
Run from the project root:  python tools/fetch_dltext.py"""
import json, os, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIELDS = 'name,type,monsterType,race,attribute,level,atk,def,description,linkRating,rush'
if __name__ == '__main__':
    os.chdir(ROOT)
    out, skip = {}, 0
    while True:
        u = f'https://www.duellinksmeta.com/api/v1/cards?limit=500&skip={skip}&fields={FIELDS}'
        page = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120))
        if not page:
            break
        for c in page:
            out[c['_id']] = {k: c.get(k) for k in ('name', 'type', 'monsterType', 'race', 'attribute', 'level', 'atk', 'def', 'description', 'linkRating')}
        skip += len(page)
        print('dl text', skip, flush=True)
        time.sleep(0.2)
    json.dump(out, open('src/dl_text.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('src/dl_text.json', len(out))
