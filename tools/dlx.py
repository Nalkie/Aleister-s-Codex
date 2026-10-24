"""Duel Links extras from Duel Links Meta: character portraits and worlds, skills (with how each character gives them), in-game events with start and end.
Writes src/dl_extra.json.  Run from build/:  python tools/dlx.py   (add --refresh to download again)"""
import json, os, sys, urllib.request

B = 'https://www.duellinksmeta.com/api/v1/'
OUT = 'src/dl_extra.json'
if os.path.exists(OUT) and '--refresh' not in sys.argv:
    print('dl_extra.json exists'); sys.exit(0)


def get(u):
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=120))


chars = get(B + 'characters?limit=500&fields=name,thumbnailImage,victoryImage,worlds')
skills = get(B + 'skills?limit=2000&fields=name,description,characters,rush')
events = get(B + 'articles?category=event&sort=-date&limit=400&fields=title,date,countdownDate,countdownLabel,url,image,description')
out = {
    'chars': [{'n': c['name'], 'p': c.get('thumbnailImage') or '', 'v': c.get('victoryImage') or '', 'w': [w.get('shortName') or w.get('name') for w in c.get('worlds', [])]} for c in chars],
    'skills': [{'n': s['name'], 'd': s.get('description') or '', 'rush': bool(s.get('rush')),
                'c': [[(x.get('character') or {}).get('name'), x.get('how') or ''] for x in s.get('characters', []) if x.get('character')]} for s in skills],
    'events': [{'t': e['title'], 'd': (e.get('date') or '')[:10], 'e': (e.get('countdownDate') or '')[:10], 'u': e.get('url') or '', 'i': e.get('image') or '', 'x': e.get('description') or ''} for e in events],
}
json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print({k: len(v) for k, v in out.items()})
