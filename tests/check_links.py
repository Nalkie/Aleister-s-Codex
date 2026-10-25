"""Periodic eval (needs network): every event link the page can build must answer 200 on the live sites.
Run from the project root:  python tests/check_links.py [--all]   (default: every Duel Links event + the top 2 decks of each TCG/Genesys event; --all checks every deck)
Exit code 0 = all links alive."""
import json, sys, urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

H = {'User-Agent': 'Mozilla/5.0'}


def load(name):
    t = open(f'data/{name}.js', encoding='utf-8').read()
    return json.loads(t[t.index(',') + 1:-2])


def status(u):
    try:
        return urllib.request.urlopen(urllib.request.Request(urllib.parse.quote(u, safe=":/%?&=#'.-_~!*()@,;+$"), headers=H), timeout=40).status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return type(e).__name__


dlm = lambda u: 'https://www.duellinksmeta.com' + (u if u.startswith('/articles/') else '/articles' + u)
ygm = lambda u: 'https://www.yugiohmeta.com' + (u if u.startswith('/top-decks/') else '/top-decks' + u)
urls = [dlm(e['u']) for e in load('dlinfo')['events']]
for ev in load('events'):
    urls += [ygm(t[3]) for t in (ev['top'] if '--all' in sys.argv else ev['top'][:2]) if t[3]]
urls = sorted(set(urls))
with ThreadPoolExecutor(8) as ex:
    res = list(zip(urls, ex.map(status, urls)))
bad = [(u, c) for u, c in res if c != 200]
print(f'{len(res) - len(bad)}/{len(res)} links answer 200')
for u, c in bad:
    print('BAD', c, u)
sys.exit(1 if bad else 0)
