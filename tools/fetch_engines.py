"""Engines (motores) of YuGiOh Meta and Duel Links Meta -> src/engines_ygm.json, src/engines_dlm.json.   Run from the project root:  python tools/fetch_engines.py
An engine is a group of cards that is played together and repeats across different decks; each one lists the cards that identify it (requiredCards) and the archetypes
that use it (relatedDeckTypes). tools/engines.py counts how many recent decks play each one."""
import json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'Mozilla/5.0'}


def all_pages(base):
    out, skip = [], 0
    while True:
        page = json.load(urllib.request.urlopen(urllib.request.Request(f'{base}/api/v1/engines?limit=500&skip={skip}', headers=H), timeout=90))
        if not page:
            return out
        out += page
        skip += len(page)


if __name__ == '__main__':
    os.chdir(ROOT)
    for name, base in (('ygm', 'https://www.yugiohmeta.com'), ('dlm', 'https://www.duellinksmeta.com')):
        e = all_pages(base)
        json.dump(e, open(f'src/engines_{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print(name, len(e))
