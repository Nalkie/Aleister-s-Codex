"""Rendimiento: las recetas de cada mazo (cientos de cartas con imagen, 12.000 nodos en la pestaña TCG) se arman recién cuando el mazo se abre o se acerca a la pantalla,
y las capas fijas del fondo pasan a su propia capa de GPU. Backup: src.before_patch41.html."""
import shutil
shutil.copy('src.html', 'src.before_patch41.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function decklist(l,kind='tcg'){", r'''const LAZYREC=[]; let LAZYIO=null;   // recetas que se arman al abrir el mazo
function decklist(l,kind='tcg'){ return `<div class="lazyrec" data-lr="${LAZYREC.push({l,kind})-1}"></div>`; }
function lazyFill(el){ const r=LAZYREC[+el.dataset.lr]; if(!r||el.dataset.done) return; el.dataset.done=1; el.outerHTML=decklistNow(r.l,r.kind); }
function lazyObserve(){
  if(LAZYIO) LAZYIO.disconnect();
  const els=document.querySelectorAll('.lazyrec');
  if(!('IntersectionObserver' in window)){ els.forEach(lazyFill); return; }
  LAZYIO=new IntersectionObserver(es=>{ for(const e of es) if(e.isIntersecting){ LAZYIO.unobserve(e.target); lazyFill(e.target); } },{rootMargin:'300px'});
  els.forEach(el=>LAZYIO.observe(el));
}
document.addEventListener('toggle',e=>{ const d=e.target; if(d&&d.tagName==='DETAILS'&&d.open) d.querySelectorAll('.lazyrec').forEach(lazyFill); },true);   // al abrir un mazo se arma su receta
function decklistNow(l,kind='tcg'){''')
rep("function render(focusId){\n  RECIPES.length=0;", "function render(focusId){\n  RECIPES.length=0; LAZYREC.length=0;")
rep("  document.querySelectorAll('details.deck').forEach(x=>{ if(openIds.has(x.dataset.id)) x.open=true; });", "  document.querySelectorAll('details.deck').forEach(x=>{ if(openIds.has(x.dataset.id)) x.open=true; });\n  lazyObserve();")
rep(".fmtbar{margin:var(--s4) 0 0}", ".fmtbar{margin:var(--s4) 0 0}\n/* capas fijas del fondo en su propia capa: no se repintan al scrollear */\n.sideart,body::before{will-change:transform;transform:translateZ(0)}\n.lazyrec{min-height:1px}")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 41 ok')
