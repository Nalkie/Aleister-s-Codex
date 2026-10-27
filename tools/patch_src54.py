"""Modo día: las figuras de los costados cambian por otras dos (art/day-left.jpg, art/day-right.jpg), con sus propios colores.
El fondo blanco de las imágenes desaparece con mix-blend-mode:multiply sobre el fondo claro.  En modo noche siguen las de línea de siempre.
Los originales están en art_originals/ (no se publican).  Backup: src.before_patch54.html."""
import shutil
shutil.copy('src.html', 'src.before_patch54.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep('<div class="sideart l" aria-hidden="true"></div><div class="sideart r" aria-hidden="true"></div>',
    '<div class="sideart l night" aria-hidden="true"></div><div class="sideart r night" aria-hidden="true"></div><div class="sideart l day" aria-hidden="true"></div><div class="sideart r day" aria-hidden="true"></div>')
css = '''/* modo día: otras dos figuras en los costados */
.sideart.day{display:none;-webkit-mask:none;mask:none;background:var(--img) center bottom/contain no-repeat;mix-blend-mode:multiply;opacity:.4}
.sideart.day.l{--img:url(art/day-left.jpg)}
.sideart.day.r{--img:url(art/day-right.jpg)}
html[data-theme="light"] .sideart.day{display:block}
html[data-theme="light"] .sideart.night{display:none}
@media not all and (prefers-color-scheme: dark){html:not([data-theme]) .sideart.day{display:block}html:not([data-theme]) .sideart.night{display:none}}
@media(max-width:1240px){.sideart.day{opacity:.28}}
@media(max-width:1000px){.sideart.day{display:none!important}}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 54 ok')
