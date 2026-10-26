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
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 42 ok')
