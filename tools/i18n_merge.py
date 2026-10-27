"""Junta los lotes traducidos (tools/i18n_parts/out_NN.json) en el diccionario tools/i18n_en.json.

  python tools/i18n_merge.py            agrega las entradas nuevas y valida todo el diccionario
Las entradas que ya estaban no se pisan (para cambiar una, editala en tools/i18n_en.json).  out_static.json (HTML fijo) va a tools/i18n_static.json.
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import i18n_check


def merge(pattern, target):
    path = os.path.join(HERE, target)
    cur = json.load(open(path, encoding='utf-8')) if os.path.exists(path) else {}
    added, bad = 0, 0
    for f in sorted(glob.glob(os.path.join(HERE, 'i18n_parts', pattern))):
        for k, v in json.load(open(f, encoding='utf-8')).items():
            if k in cur:
                continue
            p = i18n_check.problems(k, v)
            if p:
                print('rechazada', os.path.basename(f), repr(k[:60]), p)
                bad += 1
                continue
            cur[k] = v
            added += 1
    json.dump(cur, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
    print('%s: +%d (rechazadas %d), total %d' % (target, added, bad, len(cur)))


if __name__ == '__main__':
    merge('out_[0-9]*.json', 'i18n_en.json')
    merge('out_static*.json', 'i18n_static.json')
