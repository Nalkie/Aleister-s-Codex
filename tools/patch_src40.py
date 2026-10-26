"""Sin pantallazos vacíos: al redibujar una vista la página se encogía un instante (por ejemplo mientras mostraba "Cargando…") y, si estabas abajo, quedaba a la vista solo el fondo
con el arte lineal y el degradé, el "brillo extraño". Ahora #app conserva su alto durante ese momento. Backup: src.before_patch40.html."""
import shutil
shutil.copy('src.html', 'src.before_patch40.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function render(focusId){\n  RECIPES.length=0;",
    "function render(focusId){\n  RECIPES.length=0;\n  { const app=document.getElementById('app'); if(app){ app.style.minHeight=app.offsetHeight+'px'; clearTimeout(render._mh); render._mh=setTimeout(()=>{ app.style.minHeight=''; },1100); } }   // la página no se encoge mientras se redibuja")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 40 ok')
