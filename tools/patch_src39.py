"""Las listas con scroll propio (buscador de cartas, cajas y sets, constructor, engines) conservan su posición al elegir un elemento: antes render() las rehacía
y volvían al principio. No se restaura al escribir en un buscador (cambia la lista) ni al cambiar de pestaña. Backup: src.before_patch39.html."""
import shutil
shutil.copy('src.html', 'src.before_patch39.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function render(focusId){\n  RECIPES.length=0;",
    "const KEEP_SCROLL='.pick,.setlist,.dkpick';   // contenedores con scroll propio\nfunction render(focusId){\n  RECIPES.length=0;\n  const keepScroll=render._mode===mode&&!focusId?[...document.querySelectorAll(KEEP_SCROLL)].map(el=>[el.className,el.scrollTop]):[];\n  render._mode=mode;")
rep("  document.querySelectorAll('details.deck').forEach(x=>{ if(openIds.has(x.dataset.id)) x.open=true; });",
    "  document.querySelectorAll('details.deck').forEach(x=>{ if(openIds.has(x.dataset.id)) x.open=true; });\n  { const now=[...document.querySelectorAll(KEEP_SCROLL)]; keepScroll.forEach(([cls,top],i)=>{ if(now[i]&&now[i].className===cls) now[i].scrollTop=top; }); }")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 39 ok')
