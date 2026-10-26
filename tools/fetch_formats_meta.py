"""Metagame of the retro formats (Goat, Edison, HAT) -> src/formats_meta.json.   Run from the project root:  python tools/fetch_formats_meta.py
Source: Format Library public API. For each event of the last WINDOW_DAYS days of its format: how many decks of each archetype played (metagame),
the top cut (placement, archetype, player, deck id) and, for the best-placed decks of each archetype, the deck list (ydk).
Resumable: events and decks already in the file are not downloaded again."""
import concurrent.futures as cf, datetime, json, os, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'Mozilla/5.0'}
FL = 'https://formatlibrary.com/api/'
FORMATS = {'Goat': 'goat', 'Edison': 'edison', 'HAT': 'hat'}
WINDOW_DAYS = 365
LISTS_PER_TYPE = 8        # best-placed, newest decks per archetype whose list is downloaded
MAX_PLACE = 8


def get(path, tries=4):
    for i in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(FL + path, headers=H), timeout=60))
        except Exception as e:
            err = e
            time.sleep(2 * (i + 1))
    print('failed', path, err, flush=True)
    return None


if __name__ == '__main__':
    os.chdir(ROOT)
    out = json.load(open('src/formats_meta.json', encoding='utf-8')) if os.path.exists('src/formats_meta.json') else {}
    for k in FORMATS.values():
        out.setdefault(k, {'events': {}, 'decks': {}})
    listed, page, stop = [], 1, False
    newest = None
    while not stop:
        rows = get(f'events?page={page}&limit=100')
        if not rows:
            break
        for e in rows:
            d = (e.get('startedAt') or '')[:10]
            newest = newest or d
            if newest and (datetime.date.fromisoformat(newest) - datetime.date.fromisoformat(d)).days > WINDOW_DAYS:
                stop = True
            elif e['formatName'] in FORMATS:
                listed.append(e)
        page += 1
        print('events page', page - 1, 'listed', len(listed), flush=True)
    todo = [e for e in listed if e['abbreviation'] not in out[FORMATS[e['formatName']]]['events']]
    def event(e):
        d = get('events/' + urllib.parse.quote(e['abbreviation']))
        return e, d
    with cf.ThreadPoolExecutor(6) as ex:
        for e, d in ex.map(event, todo):
            if not d:
                continue
            out[FORMATS[e['formatName']]]['events'][e['abbreviation']] = {
                'abbr': e['abbreviation'], 'n': e['name'], 'd': (e.get('startedAt') or '')[:10], 'size': e.get('size'), 'community': e.get('communityName'),
                'url': e.get('referenceUrl'), 'winner': e.get('winnerName'),
                'meta': [[t[0], t[1]] for t in (d.get('metagame') or {}).get('deckTypes', [])],
                'top': [[t['placement'], t['deckTypeName'], t['builderName'], t['id']] for t in d.get('topDecks', []) if t.get('deckTypeName')]}
    print('events downloaded', len(todo), flush=True)
    for k, f in out.items():
        best = {}
        for ev in sorted(f['events'].values(), key=lambda e: e['d'], reverse=True):
            for pl, tp, by, did in sorted(ev['top']):
                if pl <= MAX_PLACE and len(best.setdefault(tp, [])) < LISTS_PER_TYPE:
                    best[tp].append(did)
        need = [did for l in best.values() for did in l if str(did) not in f['decks']]
        def deck(did):
            d = get(f'decks/{did}')
            return did, d and d.get('ydk')
        with cf.ThreadPoolExecutor(6) as ex:
            for did, ydk in ex.map(deck, need):
                if ydk:
                    f['decks'][str(did)] = ydk
        print(k, 'events', len(f['events']), 'decks', len(f['decks']), flush=True)
    json.dump(out, open('src/formats_meta.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print('src/formats_meta.json', {k: (len(v['events']), len(v['decks'])) for k, v in out.items()})
