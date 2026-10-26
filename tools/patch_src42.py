"""Móvil: la barra de modos/herramientas y el resto de secciones se ven completas en teléfono (botones sin recortar, sin scroll lateral). Todo el CSS está en
tools/mobile.css dentro de @media(max-width:760px), así que el escritorio no cambia. Backup: src.before_patch42.html."""
import shutil
shutil.copy('src.html', 'src.before_patch42.html')
s = open('src.html', encoding='utf-8').read()
css = open('tools/mobile.css', encoding='utf-8').read()
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
# etiquetas de columna para las tablas apiladas del móvil (inofensivo en escritorio: solo un atributo data-l)
a = "  { const now=[...document.querySelectorAll(KEEP_SCROLL)]; keepScroll.forEach(([cls,top],i)=>{ if(now[i]&&now[i].className===cls) now[i].scrollTop=top; }); }"
assert s.count(a) == 1
s = s.replace(a, a + "\n  document.querySelectorAll('#app .tbl table').forEach(t=>{ const h=[...t.querySelectorAll('thead th')].map(x=>x.textContent.trim()); t.querySelectorAll('tbody tr').forEach(r=>[...r.cells].forEach((c,i)=>{ if(h[i]) c.dataset.l=h[i]; })); });")

# móvil/tablet: al elegir una carta o un set la pantalla baja al detalle (antes se abría debajo de la lista y parecía que no pasaba nada), con botón para volver a la lista
def rep(a, b):
    global s
    assert s.count(a) == 1, (s.count(a), a[:80])
    s = s.replace(a, b)

rep("  else if(d.setsel){ SETS.sel=d.setsel; SETS.cl=SCL; SETS.card=null; SETS.cq=''; SETS.rf='all'; render(); }",
    "  else if(d.setsel){ SETS.sel=d.setsel; SETS.cl=SCL; SETS.card=null; SETS.cq=''; SETS.rf='all'; render(); mobTo('#app .sethero,#app .chcard'); }\n  else if(d.mback){ const f=document.querySelector('#app .filters'); if(f) f.scrollIntoView({block:'start',behavior:'smooth'}); }")
rep("if(innerWidth<=900&&dt&&dt.getBoundingClientRect().top<0) dt.scrollIntoView({block:'start'}); } }",
    "if(innerWidth<=900&&dt) mobTo('#app .detail'); } }")
rep("const KEEP_SCROLL=", "function mobTo(sel){ if(innerWidth>900) return; setTimeout(()=>{ const t=document.querySelector(sel); if(t) t.scrollIntoView({block:'start',behavior:'smooth'}); },60); }\nconst KEEP_SCROLL=")
rep("  document.querySelectorAll('#app .tbl table')",
    "  if(innerWidth<=900&&(mode==='ex'||mode==='sets'||mode==='obt')){ const t=document.querySelector('#app .detail .hero-card,#app .sethero,#app .chcard'); if(t&&!t.closest('.sinsp')) t.insertAdjacentHTML('beforebegin','<button class=\"abtn mback\" data-mback=\"1\" style=\"margin-bottom:var(--s3)\">↑ Volver a la lista</button>'); }\n  document.querySelectorAll('#app .tbl table')")

# los textos que dicen "a la derecha" dicen "más abajo" cuando la pantalla es angosta (las columnas se apilan)
rep("verla a la derecha, con cómo conseguirla.'", "verla '+(innerWidth<=900?'más abajo':'a la derecha')+', con cómo conseguirla.'")
rep("Vacío. Buscá cartas a la derecha y tocalas", "Vacío. Buscá cartas '+(innerWidth<=900?'más abajo':'a la derecha')+' y tocalas")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 42 ok')
