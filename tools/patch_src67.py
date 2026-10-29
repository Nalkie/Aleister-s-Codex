"""Ruleta de decks: se saca la franja de Fidelidad y Legalidad del resultado (barra de fidelidad, aviso de cartas que no existen, una línea por formato con «Mejor para jugar»
y «Qué cartas pasan el límite»): era invasiva y no sumaba.  Queda el duelista, los Reemplazos, la leyenda y la receta; en los mazos temáticos, la base del mazo en una línea;
las cartas del anime que no existen en el TCG van en un desplegable.  Se borran rouLegal, rouBest, ROU_FMTS, rouLegalBadges y su CSS.  Backup: src.before_patch67.html."""
import re
import shutil

shutil.copy('src.html', 'src.before_patch67.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (s.count(a), a[:90])
    s = s.replace(a, b)


def cut(start, end):
    """Borra desde `start` (incluido) hasta `end` (excluido); ambos deben ser únicos."""
    global s
    assert s.count(start) == 1 and s.count(end) == 1, (start[:60], end[:60])
    i, j = s.index(start), s.index(end)
    assert i < j
    s = s[:i] + s[j:]


# ---- JS: helpers de legalidad que ya nadie usa
cut('function rouLegal(cards,lim){', 'const ROU_FACE=')
cut('function rouBest(rows){', 'const rouArc=')
rep("const ROU_FMTS=[['tcg','TCG Advanced'],['md','Master Duel'],['edison','Edison'],['goat','Goat'],['hat','HAT']];\n", '')
cut('function rouLegalBadges(d){', 'function rouResult(d){')

# ---- JS: el resultado sin la franja
rep("// lo de abajo: fidelidad y legalidad en una franja, los reemplazos con imagen y la receta", "// lo de abajo: los reemplazos con imagen y la receta")
cut("  const nx=mis.length?", "  const miss=mis.length?")
rep("""const miss=mis.length?`<details class="rou-more"><summary>Ver cuáles</summary>""",
    """const miss=mis.length?`<details class="rou-more"><summary>${mis.length} ${mis.length===1?'carta del anime no existe':'cartas del anime no existen'} en el TCG</summary>""")
rep("  const lg=rouLegalBadges(d);\n", '')
cut("  const all=[...d.main,...d.extra], tot=all.reduce", "  return `<section class=\"rou-res")
rep("""<div class="rou-strip">${fid}<div class="rou-leg"><h4>Legalidad</h4>${lg.html}${lg.det?how(lg.det,'Qué cartas pasan el límite'):''}</div></div>
    ${swp}${miss}""",
    """${them?`<p class="rou-basis" lang="es">${LANG==='en'?'<span class="rou-es">ES</span> ':''}${esc(d.basis||'')}</p>`:''}
    ${swp}${miss}""")

# ---- CSS
cut('.rou-strip{display:grid', '.rou-basis{margin:0')
rep(".rou-basis{margin:0;font-size:.92rem;max-width:70ch}\n.rou-leg .rnote{margin-top:var(--s2)}\n", ".rou-basis{margin:0;font-size:.92rem;max-width:70ch}\n")
cut('.rou-lgl{list-style:none', '.rou-es{font:600')
s = re.sub(r"\.rou-lg\.(ok|warn|bad|wait)\{[^\n]*\n", '', s)
rep(".rou-fl{margin:0 0 var(--s2);font-size:.84rem} .rou-fl .lnk{font-size:.84rem}\n", '')
rep(".rou-strip{grid-template-columns:minmax(0,1fr)}}", "}")
rep("  .rou-strip{grid-template-columns:minmax(0,1fr);padding:var(--s3)}\n  .rou-lg b{min-width:96px}\n", '')

rep(", repl=new Set((d.swapped||[]).map(x=>x[0])), noRep=mis.filter(x=>!repl.has(x));", ';')   # ya sin uso

# lo que quedó sin usar tiene que haberse ido entero
for k in ('rou-strip', 'rou-lgl', '.rou-lg.', 'class="rou-lg', '.rou-lg b', 'rouLegal', 'rouBest', 'ROU_FMTS', 'rou-fid', 'rou-nx', 'rou-pc', 'rou-fl', 'rou-best', 'rou-leg'):
    assert k not in s, k
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 67 ok')
