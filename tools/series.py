"""Valida las series del anime (src/series/series.json) y las escribe en data/series.js.   Run from the project root:  python tools/series.py

El build falla (exit 1) si una serie no cumple el contrato (contracts/series.ts):
  * ids distintos de los de la ruleta (dm gx 5d zx av vr) o repetidos, año fuera de 1998-2030, protagonista vacío
  * era que no existe en src/formats.json
  * mech de 5 a 30 palabras o blurb de 25 a 70, igual en es y en en, con raya larga o "banish"/"banear"
  * un protagonista que no tiene duelista en la ruleta (src/roulette/*.json) para esa serie
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = ['dm', 'gx', '5d', 'zx', 'av', 'vr']
KEYS = {'id', 'year', 'protagonist', 'who', 'era', 'mech', 'blurb'}


def words(t):
    return len(re.findall(r"[\wÀ-ÿ'’-]+", t))


def roulette_chars():
    """{(serie, personaje)} de data/roulette.js si existe; si no, de src/roulette/*.json."""
    out = set()
    f = os.path.join(ROOT, 'data', 'roulette.js')
    if os.path.exists(f):
        s = open(f, encoding='utf-8').read()
        for d in json.loads(s[s.index('{'):s.rindex('}') + 1])['decks']:
            out.add((d['series'], d['character']))
    return out


def lore_characters():
    """{nombre: slug} de las entradas de Lore de tipo personaje (src/lore/*.json)."""
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, 'src', 'lore', '*.json'))):
        e = json.load(open(f, encoding='utf-8'))
        if e.get('kind') == 'character':
            out[e['name']] = e['slug']
    return out


def check(items):
    bad = []
    if [x.get('id') for x in items] != IDS:
        bad.append('los ids tienen que ser exactamente %s, en ese orden' % IDS)
    formats = json.load(open(os.path.join(ROOT, 'src', 'formats.json'), encoding='utf-8'))
    chars = roulette_chars()
    for x in items:
        i = x.get('id', '?')
        if set(x) != KEYS:
            bad.append('%s: claves %s, esperadas %s' % (i, sorted(x), sorted(KEYS)))
            continue
        if not (isinstance(x['year'], int) and 1998 <= x['year'] <= 2030):
            bad.append('%s: año inválido' % i)
        if not x['who'].strip() or x['protagonist'] not in x['who']:
            bad.append('%s: el nombre completo (who) tiene que contener al protagonista' % i)
        if not x['protagonist'].strip():
            bad.append('%s: protagonista vacío' % i)
        if chars and (i, x['protagonist']) not in chars:
            bad.append('%s: el protagonista %r no tiene duelista en la ruleta' % (i, x['protagonist']))
        if x['era'] and x['era'] not in formats:
            bad.append('%s: la era %r no está en src/formats.json' % (i, x['era']))
        for f, lo, hi in (('mech', 5, 30), ('blurb', 25, 70)):
            t = x[f]
            if set(t) != {'es', 'en'}:
                bad.append('%s.%s: tiene que traer es y en' % (i, f))
                continue
            if t['es'].strip() == t['en'].strip():
                bad.append('%s.%s: igual en los dos idiomas' % (i, f))
            for l in ('es', 'en'):
                n = words(t[l])
                if not lo <= n <= hi:
                    bad.append('%s.%s.%s: %d palabras, tienen que ser %d a %d' % (i, f, l, n, lo, hi))
                if '—' in t[l]:
                    bad.append('%s.%s.%s: raya larga' % (i, f, l))
            if re.search(r'banish|banear', t['es'], re.I):
                bad.append('%s.%s: en español se dice desterrar' % (i, f))
    return bad


def main():
    os.chdir(ROOT)
    items = json.load(open('src/series/series.json', encoding='utf-8'))
    bad = check(items)
    if bad:
        print('\n'.join(' - ' + b for b in bad))
        print('\n%d problemas: no escribo data/series.js' % len(bad))
        sys.exit(1)
    d = {'s': [{'id': x['id'], 'y': x['year'], 'p': x['protagonist'], 'w': x['who'], 'e': x['era'], 'm': x['mech'], 'b': x['blurb']} for x in items], 'l': {n: sl for n, sl in lore_characters().items() if any(c == n for _, c in roulette_chars())}}
    open('data/series.js', 'w', encoding='utf-8').write('__load("series",' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ');')
    print('data/series.js: %d series, %d personajes con entrada de Lore' % (len(d['s']), len(d['l'])))


if __name__ == '__main__':
    main()
