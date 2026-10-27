"""Enlaces profundos, arreglo: el scroll al mazo o a la sección se perdía cuando un render posterior (carga de datos) reemplazaba el DOM.
Ahora el destino se reaplica en cada render hasta que pasan 4 s o el usuario toca la página (rueda, teclado, toque, clic).  Backup: src.before_patch62.html."""
import shutil

shutil.copy('src.html', 'src.before_patch62.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


old_start = s.index("function routePending(){")
old_end = s.index("function routeView(v){")
new = r"""function routePending(){                   // abre el mazo o baja a la sección del enlace; se repite en cada render hasta que el usuario toma el control
  const p=ROUTE.pending; if(!p) return;
  if(!p.t0) p.t0=Date.now();
  let el=null;
  if(p.deck){
    el=[...document.querySelectorAll('details.deck')].find(x=>x.dataset.slug===p.deck);
    if(el) el.open=true;
  } else if(p.view&&p.view!=='meta') el=document.getElementById('view-'+p.view);
  if(el){ p.found=true; setTimeout(()=>{ if(ROUTE.pending===p) el.scrollIntoView({block:'start'}); },120); }
  if(Date.now()-p.t0>4000||(!el&&++p.tries>12)) ROUTE.pending=null;
}
['wheel','touchstart','keydown','mousedown'].forEach(ev=>window.addEventListener(ev,()=>{ ROUTE.pending=null; },{passive:true,capture:true}));
"""
s = s[:old_start] + new + s[old_end:]
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 62 ok')
