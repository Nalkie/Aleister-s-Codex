"""Preparar el texto para traducir: frases enteras en lugar de fragmentos que se arman con piezas en español.
Backup: src.before_patch48.html."""
import shutil
shutil.copy('src.html', 'src.before_patch48.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


# «Receta más usual» / «Receta de referencia» son dos títulos distintos, no «Receta» + un adjetivo
rep("<h3>Receta ${kind==='dl'?'más usual':'de referencia'}${vbadge(l)}</h3>", "<h3>${kind==='dl'?'Receta más usual':'Receta de referencia'}${vbadge(l)}</h3>")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 48 ok')
