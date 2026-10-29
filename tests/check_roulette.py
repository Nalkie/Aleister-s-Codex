"""Gate + eval of the deck roulette data (data/roulette.js).  Sin red, <2 s.  python tests/check_roulette.py
`python tools/roulette.py check` validates every sheet against the wiki data (slow, run it after editing src/roulette); this test guards the built output the page reads.
Outcome: mean share of anime copies of the anime decks >= 75%, every deck 40-60 Main / <=15 Extra / <=3 copies, signature inside the deck, thematic decks explain their basis."""
import collections, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


t = open('data/roulette.js', encoding='utf-8').read()
D = json.loads(t[t.index(',') + 1:-2])['decks']
names = {c['name'] for c in json.load(open('src/ygo_all.json', encoding='utf-8'))}
check(len(D) >= 60 and len({d['id'] for d in D}) == len(D), '%d decks, ids unique' % len(D))
check({d['series'] for d in D} == {'dm', 'gx', '5d', 'zx'}, 'the four series are present: %s' % dict(collections.Counter(d['series'] for d in D)))
size = lambda l: sum(c[1] for c in l)
cp = lambda d: collections.Counter({n: k for n, k, *_ in d['main']}) + collections.Counter({n: k for n, k, *_ in d['extra']})
check(all(40 <= size(d['main']) <= 60 and size(d['extra']) <= 15 for d in D), 'Main 40-60 and Extra <= 15 in every deck')
check(all(k <= 3 for d in D for k in cp(d).values()), 'no deck has more than 3 copies of a name')
check(all(n in names for d in D for n, *_ in d['main'] + d['extra']), 'every card is a database card')
check(all(d['sig'] in cp(d) for d in D), 'the signature card is in its deck')
check(all(d['kind'] in ('anime', 'thematic') for d in D), 'kind is anime or thematic')
check(all(d['kind'] != 'thematic' or len(d['basis']) > 30 for d in D) and all(d['character'] and d['blurb'] and d['arc'] for d in D), 'thematic decks carry a basis; every deck has character, arc and blurb')
check(all(f in (0, 1, 2) for d in D for _, _, f in d['main'] + d['extra']), 'flags are 0 anime / 1 replacement / 2 filler')
an = [d for d in D if d['kind'] == 'anime']
mean = sum(d['anime'] for d in an) / len(an)
check(mean >= 75 and all(d['anime'] >= 50 for d in an), 'EVAL: mean share of anime copies %.1f%% (>= 75), no anime deck under 50%% (min %d%%)' % (mean, min(d['anime'] for d in an)))
check(all('banish' not in (d['blurb'] + d['basis']).lower() and 'banear' not in (d['blurb'] + d['basis']).lower() for d in D), 'Spanish text says "desterrar", never banish/banear')
check(sum(1 for d in D if d.get('face')) / len(D) >= 0.8, 'at least 80%% of the decks have a face (%d of %d); the others use a monogram' % (sum(1 for d in D if d.get('face')), len(D)))
print('failed:', len(fails))
sys.exit(1 if fails else 0)
