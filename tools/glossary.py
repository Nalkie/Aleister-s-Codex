"""Valida el glosario (src/glossary/*.json) y lo escribe en data/glossary.js.   Run from the project root:  python tools/glossary.py

Una entrada por término.  El build falla (exit 1) si una entrada:
  * no tiene exactamente las claves del contrato (contracts/glossary.ts) o le falta un idioma (es / en)
  * tiene una definición fuera de 15-80 palabras, o igual en español e inglés, o un término vacío
  * usa "banish" o "banear" en español (se dice desterrar), o una raya larga (—)
  * remite (see) a un término que no existe, a sí mismo, o no remite a ninguno
  * cita (cards) una carta que no existe en src/ygo_all.json
  * tiene una categoría que no figura en CATS, o repite slug
y si el glosario tiene menos de 60 términos o alguna categoría menos de 4.
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATS = [
    ('campo', 'El campo y las zonas', 'The field and its zones'),
    ('turno', 'El turno y la batalla', 'The turn and battle'),
    ('invocacion', 'Invocaciones', 'Summons'),
    ('efectos', 'Efectos y cadenas', 'Effects and chains'),
    ('cartas', 'Tipos de carta', 'Card types'),
    ('formatos', 'Formatos y listas', 'Formats and lists'),
    ('jerga', 'Jerga del meta', 'Meta slang'),
]
KEYS = {'slug', 'cat', 'es', 'en', 'see', 'cards'}
D_MIN, D_MAX, N_MAX = 15, 80, 60
SLUG = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
MIN_TERMS, MIN_PER_CAT = 60, 4


def words(t):
    return len(re.findall(r"[\wÀ-ÿ'’-]+", t))


def load():
    items, files = [], sorted(glob.glob(os.path.join(ROOT, 'src', 'glossary', '*.json')))
    for f in files:
        items += json.load(open(f, encoding='utf-8'))
    return items


def problems(items):
    out = []
    cards = {c['name'] for c in json.load(open(os.path.join(ROOT, 'src', 'ygo_all.json'), encoding='utf-8'))}
    cats = {c[0] for c in CATS}
    slugs = [x.get('slug') for x in items]
    for s in {s for s in slugs if slugs.count(s) > 1}:
        out.append('%s: slug repetido' % s)
    known = set(slugs)
    for x in items:
        s = x.get('slug', '?')
        if set(x) != KEYS:
            out.append('%s: las claves tienen que ser %s' % (s, sorted(KEYS)))
            continue
        if not isinstance(s, str) or not SLUG.match(s):
            out.append('%s: slug inválido' % s)
        if x['cat'] not in cats:
            out.append('%s: categoría desconocida (%s)' % (s, x['cat']))
        for l in ('es', 'en'):
            o = x[l]
            if not isinstance(o, dict) or set(o) != {'term', 'def'} or not all(isinstance(v, str) and v.strip() for v in o.values()):
                out.append('%s.%s: tiene que ser {term, def} con texto' % (s, l))
                continue
            if len(o['term']) > N_MAX:
                out.append('%s.%s: término de más de %d caracteres' % (s, l, N_MAX))
            n = words(o['def'])
            if not D_MIN <= n <= D_MAX:
                out.append('%s.%s: la definición tiene %d palabras (%d-%d)' % (s, l, n, D_MIN, D_MAX))
            if '—' in o['term'] + o['def']:
                out.append('%s.%s: raya larga' % (s, l))
        if isinstance(x['es'], dict) and isinstance(x['en'], dict) and x['es'].get('def') == x['en'].get('def'):
            out.append('%s: la definición en inglés es igual a la española' % s)
        if re.search(r'banish|banear|baneada|baneo', json.dumps(x['es'], ensure_ascii=False), re.I):
            out.append('%s.es: se dice desterrar, no banish ni banear' % s)
        if not isinstance(x['see'], list) or not x['see']:
            out.append('%s: tiene que remitir a por lo menos un término (see)' % s)
        else:
            for r in x['see']:
                if r == s:
                    out.append('%s: se remite a sí mismo' % s)
                elif r not in known:
                    out.append('%s: remite a "%s", que no existe' % (s, r))
        if not isinstance(x['cards'], list):
            out.append('%s: cards tiene que ser una lista' % s)
        else:
            for c in x['cards']:
                if c not in cards:
                    out.append('%s: la carta "%s" no existe en la base' % (s, c))
    if len(items) < MIN_TERMS:
        out.append('el glosario tiene %d términos (mínimo %d)' % (len(items), MIN_TERMS))
    for c in cats:
        if sum(1 for x in items if x.get('cat') == c) < MIN_PER_CAT:
            out.append('la categoría %s tiene menos de %d términos' % (c, MIN_PER_CAT))
    return out


def build(items):
    items = sorted(items, key=lambda x: ([c[0] for c in CATS].index(x['cat']), x['es']['term'].lower()))
    return {'cats': [{'id': c[0], 'es': c[1], 'en': c[2]} for c in CATS],
            't': [{'s': x['slug'], 'c': x['cat'], 'n': {'es': x['es']['term'], 'en': x['en']['term']},
                   'd': {'es': x['es']['def'], 'en': x['en']['def']}, 'see': x['see'], 'cards': x['cards']} for x in items]}


def main():
    os.chdir(ROOT)
    items = load()
    bad = problems(items)
    for b in bad:
        print('FAIL ' + b)
    if bad:
        print('\n%d problemas: no escribo data/glossary.js' % len(bad))
        sys.exit(1)
    d = build(items)
    open('data/glossary.js', 'w', encoding='utf-8').write('__load("glossary",' + json.dumps(d, ensure_ascii=False, separators=(',', ':')) + ');')
    print('data/glossary.js: %d términos en %d categorías' % (len(d['t']), len(d['cats'])))


if __name__ == '__main__':
    main()
