"""Textos en español que no están en los scripts: dos rótulos de CSS y etiquetas que vienen en los datos.  Backup: src.before_patch52.html.
  * CSS: .tools::before («Herramientas») y .deck.feat::after («Más jugado») pasan a variables que cambian con <html lang>.
  * Datos: «· cartas farmeables» (fuentes de Duel Links) se traduce al cargar; «Otra vía» y «Personaje» pasan por SET_ES."""
import shutil

shutil.copy('src.html', 'src.before_patch52.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep('.tools::before{content:"Herramientas";', '.tools::before{content:var(--i-tools);')
rep('.deck.feat::after{content:"Más jugado";', '.deck.feat::after{content:var(--i-feat);')
rep("body.tcg{--accent:var(--ac-tcg)}", ':root{--i-tools:"Herramientas";--i-feat:"Más jugado"}\nhtml[lang="en"]{--i-tools:"Tools";--i-feat:"Most played"}\nbody.tcg{--accent:var(--ac-tcg)}')
rep("window.__load = (name,obj)=>{ DATAP[name]=obj; };",
    "window.__load = (name,obj)=>{ DATAP[name]=(LANG==='en'&&/^(sets-dl|c\\d+)$/.test(name))?JSON.parse(JSON.stringify(obj).replace(/ · cartas farmeables/g,' · farmable cards')):obj; };")
rep("'Pickup Box':'Pickup Box'};", "'Pickup Box':'Pickup Box','Otra vía':'Otra vía','Personaje':'Personaje'};")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 52 ok')
