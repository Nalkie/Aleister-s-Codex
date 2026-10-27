"""Valida traducciones al inglés.

  python tools/i18n_check.py tools/i18n_parts/in_00.json tools/i18n_parts/out_00.json     un lote
  python tools/i18n_check.py --dict                                                       el diccionario completo contra la página

Cada traducción tiene que conservar, igual que el original: los marcadores {0} {1}..., las etiquetas HTML (y sus atributos, salvo el texto de
title / placeholder / aria-label / alt), las entidades (&amp; ...), y los espacios del principio y del final.  Además avisa si quedó español.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import i18n

TAG = re.compile(r'<[^>]+>')
ATTR_TEXT = re.compile(r'((?:title|placeholder|aria-label|alt)=")[^"]*(")')
PH = re.compile(r'\{\d+\}')
ENT = re.compile(r'&#?\w+;')


def shape(s):
    tags = [ATTR_TEXT.sub(r'\1\2', t) for t in TAG.findall(s)]
    return sorted(PH.findall(s)), tags, sorted(ENT.findall(s))


def problems(key, tr):
    out = []
    if not isinstance(tr, str) or not tr.strip():
        return ['vacía']
    a, b = shape(key), shape(tr)
    if a[0] != b[0]:
        out.append('marcadores {n} distintos: %s -> %s' % (a[0], b[0]))
    if a[1] != b[1]:
        out.append('etiquetas HTML distintas')
    if a[2] != b[2]:
        out.append('entidades distintas')
    if (key[:1].isspace(), key[-1:].isspace()) != (tr[:1].isspace(), tr[-1:].isspace()):
        out.append('espacios al principio o al final distintos')
    if '${' in tr or '`' in tr:
        out.append('contiene ${ o `')
    if re.search(r'[áéíóúñ¿¡]', TAG.sub(' ', tr)):
        out.append('quedó español (tildes)')
    return out


def check_pair(inp, outp):
    src = json.load(open(inp, encoding='utf-8'))
    got = json.load(open(outp, encoding='utf-8'))
    bad = 0
    for r in src:
        k = r['key']
        if k not in got:
            print('FALTA', repr(k[:80]))
            bad += 1
            continue
        p = problems(k, got[k])
        if p:
            bad += 1
            print('ERROR', repr(k[:70]), '->', repr(got[k][:70]), '|', '; '.join(p))
    extra = [k for k in got if k not in {r['key'] for r in src}]
    for k in extra:
        print('SOBRA', repr(k[:80]))
        bad += 1
    print('%s: %d textos, %d con problemas' % (os.path.basename(outp), len(src), bad))
    return bad


if __name__ == '__main__':
    if sys.argv[1:2] == ['--dict']:
        d = i18n.load_dict()
        bad = sum(1 for k, v in d.items() if problems(k, v))
        for k, v in d.items():
            p = problems(k, v)
            if p:
                print('ERROR', repr(k[:70]), '|', '; '.join(p))
        print('diccionario: %d entradas, %d con problemas' % (len(d), bad))
        sys.exit(1 if bad else 0)
    sys.exit(1 if check_pair(sys.argv[1], sys.argv[2]) else 0)
