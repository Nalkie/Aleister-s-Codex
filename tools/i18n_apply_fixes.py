"""Aplica las correcciones de los revisores (tools/i18n_parts/crit_out_N.json) al diccionario, validando cada una.
  python tools/i18n_apply_fixes.py
Una corrección que rompe marcadores, etiquetas o espacios se rechaza y se avisa.  Las claves están en i18n_en.json o en i18n_static.json."""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import i18n_check

files = {'main': os.path.join(HERE, 'i18n_en.json'), 'static': os.path.join(HERE, 'i18n_static.json')}
data = {k: json.load(open(p, encoding='utf-8')) for k, p in files.items()}
applied = rejected = unknown = 0
for f in sorted(glob.glob(os.path.join(HERE, 'i18n_parts', 'crit_out_*.json'))):
    for k, v in json.load(open(f, encoding='utf-8')).items():
        where = next((w for w in data if k in data[w]), None)
        if not where:
            print('clave desconocida', os.path.basename(f), repr(k[:60]))
            unknown += 1
            continue
        p = i18n_check.problems(k, v)
        if p:
            print('rechazada', os.path.basename(f), repr(k[:60]), p)
            rejected += 1
            continue
        if data[where][k] != v:
            data[where][k] = v
            applied += 1
for w, p in files.items():
    json.dump(data[w], open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0, sort_keys=True)
print('aplicadas %d, rechazadas %d, claves desconocidas %d' % (applied, rejected, unknown))
