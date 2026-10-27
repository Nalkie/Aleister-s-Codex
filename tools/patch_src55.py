"""Las dos figuras del modo día tenían el mismo ancho de columna, así que la cuadrada (mago) salía mucho más alta que la apaisada (figura alada).
Ahora las dos miden lo mismo de alto y cada una conserva su proporción; las dos apoyan en el borde de abajo.  Backup: src.before_patch55.html."""
import shutil
shutil.copy('src.html', 'src.before_patch55.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep(".sideart.day{display:none;-webkit-mask:none;mask:none;background:var(--img) center bottom/contain no-repeat;mix-blend-mode:multiply;opacity:.4}\n.sideart.day.l{--img:url(art/day-left.jpg)}\n.sideart.day.r{--img:url(art/day-right.jpg)}",
    ".sideart.day{display:none;-webkit-mask:none;mask:none;top:auto;bottom:0;height:min(62vh,580px);width:auto;mix-blend-mode:multiply;opacity:.4}\n.sideart.day.l{--img:url(art/day-left.jpg);aspect-ratio:893/900;left:-2vw;background:var(--img) left bottom/contain no-repeat}\n.sideart.day.r{--img:url(art/day-right.jpg);aspect-ratio:1000/747;right:-4vw;background:var(--img) right bottom/contain no-repeat}")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 55 ok')
