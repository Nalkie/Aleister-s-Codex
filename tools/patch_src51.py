"""Frases que se armaban pegando fragmentos en español (no se pueden traducir pieza por pieza) pasan a ser plantillas completas,
y los puestos de torneo que vienen en los datos («2.º puesto») se muestran en inglés.  Backup: src.before_patch51.html."""
import shutil

shutil.copy('src.html', 'src.before_patch51.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("${FMT_RETRO[kind]?'de '+FMT_RETRO[kind]:'del TCG'}", "${FMT_RETRO[kind]?`de ${FMT_RETRO[kind]}`:'del TCG'}")
rep("${i.c.length>1?' y '+(i.c.length-1)+' personaje'+(i.c.length>2?'s':'')+' más':''}", "${i.c.length>2?` y ${i.c.length-1} personajes más`:i.c.length>1?' y 1 personaje más':''}")
rep("'Mazo con '+s.cards.length+' cartas distintas'+(s.lists?' · % sobre '+s.lists+' listas':'')+'.'",
    "(s.lists?`Mazo con ${s.cards.length} cartas distintas · % sobre ${s.lists} listas.`:`Mazo con ${s.cards.length} cartas distintas.`)")
# puestos que vienen en los datos
rep("${l.place||'puesto'}", "${PL(l.place)||'puesto'}")
rep("${w.place?', '+w.place:''}", "${w.place?', '+PL(w.place):''}", 2)
rep("function __t(a){", """function PL(p){          // «1.º puesto» (viene en los datos) -> «1st place»
  if(LANG!=='en'||!p) return p;
  const m=/^(\\d+)\\.º puesto$/.exec(p); if(!m) return p;
  const n=+m[1], s=n%100>=11&&n%100<=13?'th':({1:'st',2:'nd',3:'rd'}[n%10]||'th');
  return n+s+' place';
}
function __t(a){""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 51 ok')
