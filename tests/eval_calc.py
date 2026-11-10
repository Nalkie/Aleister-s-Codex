"""Eval del botón «Calcular mejores jugadas»: ¿reconoce de qué mazo se parece una lista con los datos reales del proyecto?  Sin red, sin costo.  Run from the project root:  python tests/eval_calc.py

Outcome (lo que se mide): el porcentaje de listas que el estimativo asigna al mazo correcto.
  * propia:      la receta real de cada mazo del ranking, como si la armara el usuario.  Umbral: >= 95 % acierta el mazo en primer lugar.
  * retocada:    la misma receta con 5 copias cambiadas por cartas de relleno que no están en ningún mazo.  Umbral: >= 85 %.
  * solo staples: las 15 cartas más repetidas entre los mazos (sin nada de ningún arquetipo): no debe parecerse a ninguno (base null) en >= 80 % de los formatos.
Los umbrales se fijaron mirando estos mismos datos (CALC_MIN se calibró aquí), así que son una barrera contra regresiones, no una prueba independiente.
"""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
src = open('src.html', encoding='utf-8').read()
core = re.search(r'const CALC_TRIALS=.*?\nconst CALC_PREFIX=', src, re.S)
hand = re.search(r'function handDeck\(main\)\{[^\n]*\n', src)
if not (core and hand):
    sys.exit('FAIL the calc functions are not in src.html')
code = hand.group(0) + core.group(0)[:-len('const CALC_PREFIX=')]

harness = code + r'''
const fs = require('fs');
const rec = (d) => ({main: d.recipe.main.map(x => [x[0], x[1], x[2]]), extra: d.recipe.extra.map(x => [x[0], x[1], x[2]]), side: d.recipe.side.map(x => [x[0], x[1], x[2]])});
const mkDecks = (obj, keep) => Object.entries(obj.decks).filter(([, d]) => !d.out && d.recipe && (!keep || keep(d))).map(([n, d]) => ({n, list: rec(d), share: d.share, out: false, tier: d.tier}));
const y = JSON.parse(fs.readFileSync('dl/ygmdata.json', 'utf8'));
const dl = JSON.parse(fs.readFileSync('dl/dldata.json', 'utf8'));
const x = JSON.parse(fs.readFileSync('data/ygmx.js', 'utf8').replace(/^__load\("ygmx",/, '').replace(/\);\s*$/, ''));
const sets = {tcg: mkDecks(y.tcg), gen: mkDecks(y.gen), dl: mkDecks(dl.speed).concat(mkDecks(dl.rush))};
for (const f of ['ocg', 'edison', 'goat', 'hat', 'md']) if (x[f]) sets[f] = mkDecks(x[f]);
const userOf = (d) => { const u = {main: {}, extra: {}, side: {}}; for (const s of ['main', 'extra', 'side']) for (const [n, k] of d.list[s]) u[s][n] = (u[s][n] || 0) + k; return u; };
const out = {};
for (const [f, decks] of Object.entries(sets)) {
  if (decks.length < 3) continue;
  const idf = calcIdf(decks), rank = (u) => decks.map(d => ({d, s: calcSimilarity(u, d, idf)})).sort((a, b) => b.s - a.s || b.d.share - a.d.share);
  let own = 0, pert = 0, hard = 0, minOwn = 1, minHard = 1, ownApply = 0, pertApply = 0;
  const rnd = calcRng(12345);
  for (const d of decks) {
    const u = userOf(d); const r = rank(u);
    if (r[0].d.n === d.n) own++;
    if (r[0].d.n === d.n && r[0].s >= CALC_APPLY) ownApply++;
    const sc = r.find(z => z.d.n === d.n).s; if (sc < minOwn) minOwn = sc;
    for (const swaps of [5, 15]) {
      const p = userOf(d); const names = Object.keys(p.main); let removed = 0, guard = 0;
      while (removed < swaps && guard++ < 500) { const n = names[Math.floor(rnd() * names.length)]; if (p.main[n] > 0) { p.main[n]--; removed++; } }
      p.main['Relleno'] = removed;
      const rr = rank(p);
      if (swaps === 5) { if (rr[0].d.n === d.n) pert++; if (rr[0].d.n === d.n && rr[0].s >= CALC_APPLY) pertApply++; } else { if (rr[0].d.n === d.n) hard++; const sc2 = rr.find(z => z.d.n === d.n).s; if (sc2 < minHard) minHard = sc2; }
    }
  }
  const df = {}; for (const d of decks) { const seen = new Set(); for (const s of ['main', 'extra']) for (const [n] of d.list[s]) seen.add(n); for (const n of seen) df[n] = (df[n] || 0) + 1; }
  const top = Object.entries(df).sort((a, b) => b[1] - a[1] || (a[0] < b[0] ? -1 : 1)).slice(0, 15).map(e => e[0]);
  const st = {main: {}, extra: {}, side: {}}; top.forEach(n => st.main[n] = 3);
  const r = rank(st);
  out[f] = {decks: decks.length, own: own / decks.length, pert: pert / decks.length, hard: hard / decks.length, ownApply: ownApply / decks.length, pertApply: pertApply / decks.length, minHard: minHard, minOwn: minOwn, stapleBest: r[0].s, stapleNull: r[0].s < CALC_MIN, stapleApplied: r[0].s >= CALC_APPLY};
}
console.log(JSON.stringify({min: CALC_MIN, apply: CALC_APPLY, out}));
'''
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as fh:
    fh.write(harness)
    path = fh.name
try:
    r = subprocess.run(['node', path], capture_output=True, text=True, encoding='utf-8', cwd=ROOT)
finally:
    os.unlink(path)
try:
    res = json.loads(r.stdout.strip())
except Exception:
    sys.exit('FAIL node did not run the eval: ' + (r.stderr.strip().splitlines() or ['?'])[-1][:300])
fails = []
print('CALC_MIN = %s' % res['min'])
print('%-8s %6s %8s %8s %8s %10s %8s' % ('formato', 'mazos', 'propia', 'retocada', 'fuerte', 'min fuerte', 'staples'))
tot = {'n': 0, 'own': 0, 'pert': 0, 'hard': 0, 'oa': 0, 'pa': 0}
nulls = 0
for f, m in res['out'].items():
    print('%-8s %6d %7.0f%% %7.0f%% %7.0f%% %10.2f %5.2f %s' % (f, m['decks'], m['own'] * 100, m['pert'] * 100, m['hard'] * 100, m['minHard'], m['stapleBest'], 'null' if m['stapleNull'] else 'ASIGNA'))
    tot['n'] += m['decks']; tot['own'] += m['own'] * m['decks']; tot['pert'] += m['pert'] * m['decks']; tot['hard'] += m['hard'] * m['decks']; tot['oa'] += m['ownApply'] * m['decks']; tot['pa'] += m['pertApply'] * m['decks']
    nulls += m['stapleNull']
own, pert, hard, nf = tot['own'] / tot['n'], tot['pert'] / tot['n'], tot['hard'] / tot['n'], len(res['out'])
oa, pa = tot['oa'] / tot['n'], tot['pa'] / tot['n']
print('con la ficha aplicada (parecido >= %s): propia %.1f %% | retocada %.1f %%' % (res['apply'], oa * 100, pa * 100))
print('\nTOTAL %d listas: propia %.1f %% | retocada %.1f %% | fuerte %.1f %% | solo staples sin mazo en %d de %d formatos' % (tot['n'], own * 100, pert * 100, hard * 100, nulls, nf))
for ok, msg in ((own >= 0.95, 'own list identified in first place >= 95 %'), (pert >= 0.85, 'list with 5 swapped cards identified >= 85 %'), (hard >= 0.70, 'list with 15 swapped cards identified >= 70 %'), (nulls >= 0.8 * nf, 'staples-only list matches no deck in >= 80 % of the formats'),
                (oa >= 0.95, 'own list gets its sheet applied (similarity >= CALC_APPLY) in >= 95 %'), (pa >= 0.85, 'list with 5 swapped cards still gets its sheet in >= 85 %'),
                (not any(m['stapleApplied'] for m in res['out'].values()), 'a staples-only list never gets a sheet applied'),
                (all(m['minOwn'] >= res['min'] for m in res['out'].values()), 'every real list scores above CALC_MIN against its own deck')):
    print(('ok   ' if ok else 'FAIL ') + msg)
    if not ok:
        fails.append(msg)
sys.exit(1 if fails else 0)
