"""Anniversary Boxes: add the cards that Duel Links Meta leaves out of each box (the extended / alternate artwork versions) using the box lists of
the Yu-Gi-Oh! Wiki (yugioh.fandom.com, text under CC BY-SA). Only the Anniversary boxes use this source.
  python tools/fandom_anniv.py --fetch   downloads the lists -> src/fandom_anniversary.json (network)
  python tools/fandom_anniv.py           adds the missing cards to data/sets-dl.js and to each card's detail (data/c<N>.js); running it twice changes nothing
Run from the project root after tools/build_db.py."""
import json, os, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = {'User-Agent': 'AleistersCodex/1.0'}
OUT = 'src/fandom_anniversary.json'


def parse(wikitext):
    """[(card name, rarity)] of every {{Set list ...}} block of the page."""
    out, pos = [], 0
    while True:
        a = wikitext.find('{{Set list', pos)
        if a < 0:
            return out
        b = wikitext.find('\n}}', a)
        b = len(wikitext) if b < 0 else b
        for line in wikitext[a:b].splitlines()[1:]:
            line = re.sub(r'//.*', '', line).strip()
            if ';' in line:
                name, rar = [x.strip() for x in line.split(';')[:2]]
                out.append((re.sub(r'\s*\(card\)$', '', name), rar))
        pos = b


def fetch(set_names):
    res = {}
    for nm in set_names:
        u = 'https://yugioh.fandom.com/api.php?action=parse&page=' + urllib.parse.quote(nm.replace(' ', '_')) + '&prop=wikitext&format=json&redirects=1'
        t = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=H), timeout=60))['parse']['wikitext']['*']
        res[nm] = parse(t)
    return res


def load(path):
    t = open(path, encoding='utf-8').read()
    head = t[:t.index(',') + 1]
    return head, json.loads(t[len(head):-2])


def save(path, head, obj):
    open(path, 'w', encoding='utf-8').write(head + json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + ');')


def apply_sets(sets_dl, lists, pos):
    """Add the listed cards that the set lacks. Returns (added, unknown names)."""
    added, unknown = {}, set()
    for s in sets_dl:
        if s['kind'] != 'set' or s['n'] not in lists:
            continue
        have = {k[0] for k in s['k']}
        for name, _ in lists[s['n']]:
            if name not in pos:
                unknown.add(name)
            elif pos[name] not in have:
                s['k'].append([pos[name], 1])
                have.add(pos[name])
                added.setdefault(s['n'], []).append(name)
    return added, unknown


if __name__ == '__main__':
    os.chdir(ROOT)
    if '--fetch' in sys.argv:
        sets = json.load(open('src/dl_sets.json', encoding='utf-8'))
        lists = fetch([s['name'] for s in sets if s['name'].startswith('Anniversary Box')])
        json.dump(lists, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        print(OUT, {k: len(v) for k, v in lists.items()})
        sys.exit(0)
    lists = json.load(open(OUT, encoding='utf-8'))
    idx = load('data/index.js')[1]['cards']
    names = [r[0] for r in idx]
    pos = {n: i for i, n in enumerate(names)}
    head, sets_dl = load('data/sets-dl.js')
    sets_info = {s['name']: s for s in json.load(open('src/dl_sets.json', encoding='utf-8'))}
    added, unknown = apply_sets(sets_dl, lists, pos)
    save('data/sets-dl.js', head, sets_dl)
    for f in sorted(x for x in os.listdir('data') if re.fullmatch(r'c\d+\.js', x)):
        head, det = load('data/' + f)
        changed = False
        for sname, cs in added.items():
            for c in cs:
                d = det.get(c)
                if d and d.get('dl') and not any(o[0] == 's' and o[1] == sname for o in d['dl']['ob']):
                    d['dl']['ob'].append(['s', sname, 'Main Box', 1, (sets_info[sname].get('release') or '')[:10]])
                    changed = True
        if changed:
            save('data/' + f, head, det)
    print('cards added from the Yu-Gi-Oh! Wiki:', {k: len(v) for k, v in added.items()}, '· not in the page index:', sorted(unknown))
