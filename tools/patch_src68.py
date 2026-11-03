"""Ruleta de decks: el resultado ya no ensancha la página.  `.rou-res` era una grilla sin columnas definidas: su columna implícita crecía hasta el ancho del contenido, y la fila de
Reemplazos (un carrusel con overflow-x:auto de tarjetas de 268px) la estiraba más que la ventana (1396px en 1280), rompiendo el diseño y con scroll horizontal en toda la página.
Ahora la columna es minmax(0,1fr): el carrusel scrollea por dentro.  Backup: src.before_patch68.html."""
import shutil

shutil.copy('src.html', 'src.before_patch68.html')
s = open('src.html', encoding='utf-8').read()
a = ".rou-res{--accent:var(--sc,var(--ac-tool));display:grid;gap:var(--s4);"
assert s.count(a) == 1
s = s.replace(a, ".rou-res{--accent:var(--sc,var(--ac-tool));display:grid;grid-template-columns:minmax(0,1fr);gap:var(--s4);")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 68 ok')
