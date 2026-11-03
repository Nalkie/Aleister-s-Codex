"""patch 78 (2026-11-03): tournament summary.  The first row of an event is shown as "1.º" even when YuGiOh Meta did not publish the winning deck (80 events), and a Top 4 (3.5) read
"Top 3.5".  Run once from the project root:  python tools/patch_src78.py   (backup: src.before_patch78.html)"""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'src.html')
t = open(P, encoding='utf-8').read()
if not os.path.exists(os.path.join(ROOT, 'src.before_patch78.html')):
    shutil.copy2(P, os.path.join(ROOT, 'src.before_patch78.html'))
PAIRS = [("const row=e=>{ const w=e.top[0]; return", "const row=e=>{ const w=e.top.find(r=>r[0]===1); return"),
         (":'<small>Sin resultados publicados</small>'}</span></summary>", ":e.top.length?'<small>Mazo ganador sin publicar</small>':'<small>Sin resultados publicados</small>'}</span></summary>"),
         ("${pl===1?'1.º':'Top '+pl}", "${pl===1?'1.º':'Top '+(pl===3.5?4:pl)}")]
for old, new in PAIRS:
    assert t.count(old) == 1, old
    t = t.replace(old, new)
open(P, 'w', encoding='utf-8').write(t)
p = os.path.join(ROOT, 'tools/i18n_en.json')
j = open(p, encoding='utf-8').read()
add = '"<small>Mazo ganador sin publicar</small>": "<small>Winning deck not published</small>",\n'
if add not in j:
    k = '"<small>Sin resultados publicados</small>"'
    j = j.replace(k, add + k, 1)
    open(p, 'w', encoding='utf-8').write(j)
print('ok')
