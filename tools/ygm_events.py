"""All events of YuGiOh Meta (TCG, OCG, Genesys) -> src/ygm_events.json (the page keeps TCG and Genesys; build_db.py joins them with the top decks).
Run from build/:  python tools/ygm_events.py"""
import json, urllib.request

out, skip = [], 0
while True:
    page = json.load(urllib.request.urlopen(urllib.request.Request(f'https://www.yugiohmeta.com/api/v1/events?limit=500&skip={skip}', headers={'User-Agent': 'Mozilla/5.0'}), timeout=120))
    if not page:
        break
    out += page
    skip += len(page)
out.sort(key=lambda x: x['date'])
json.dump(out, open('src/ygm_events.json', 'w', encoding='utf-8'), separators=(',', ':'))
print('events', len(out), 'newest', out[-1]['date'][:10])
