"""Retro TCG formats -> data/formats.js.  Run from the project root after tools/build_db.py:  python tools/formats.py
Reads src/formats.json (tools/fetch_formats.py), src/ygo_all.json + src/cardsets.json for first-print dates and data/index.js for the card rows.
  ban   : card name -> 0 forbidden, 1 limited, 2 semi-limited (the banlist of the format, from Format Library; the Goat list is identical to YGOPRODeck's)
  pool  : positions in data/index.js of the cards that exist in the format. Goat and Edison use the exact pool YGOPRODeck publishes; HAT has no
          published pool, so it is every card whose first TCG print is on or before the format date (Edison checked this rule: 3,661 of 3,662 match)."""
import html, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ['edison', 'goat', 'hat']
STATUS = {'forbidden': 0, 'limited': 1, 'semiLimited': 2}


def first_print(ygo, sets):
    sd = {html.unescape(s['set_name']): s.get('tcg_date') for s in sets}
    out = {}
    for c in ygo:
        ds = [sd.get(html.unescape(s[0])) for s in c['sets']]
        ds = [d for d in ds if d]
        if ds:
            out[c['name']] = min(ds)
    return out


def build(src, ygo, sets, names):
    pos = {n: i for i, n in enumerate(names)}
    fp = first_print(ygo, sets)
    out = {'order': ORDER, 'formats': {}}
    for k in ORDER:
        f = src[k]
        if f.get('pool'):
            pool, how = f['pool'], 'api'
        else:
            pool, how = [n for n, d in fp.items() if d <= f['date']], 'date'
        out['formats'][k] = {
            'name': f['name'], 'date': f['date'], 'banlistName': f['banlistName'], 'event': f['event'], 'source': f['description'], 'poolHow': how,
            'ban': {n: STATUS[s] for s, l in f['banlist'].items() for n in l}, 'removed': f['removed'],
            'pool': sorted(pos[n] for n in set(pool) if n in pos), 'decks': f['decks'], 'events': f['events'],
        }
    return out


if __name__ == '__main__':
    os.chdir(ROOT)
    idx = open('data/index.js', encoding='utf-8').read()
    names = [r[0] for r in json.loads(idx[idx.index(',') + 1:-2])['cards']]
    out = build(json.load(open('src/formats.json', encoding='utf-8')), json.load(open('src/ygo_all.json', encoding='utf-8')),
                json.load(open('src/cardsets.json', encoding='utf-8')), names)
    open('data/formats.js', 'w', encoding='utf-8').write('__load("formats",' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ');')
    print('data/formats.js', {k: (len(v['pool']), len(v['ban']), v['poolHow']) for k, v in out['formats'].items()})
