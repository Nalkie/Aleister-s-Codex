"""Señal en rojo en la fila del mazo (antes de abrirlo) cuando su receta es anterior a las reglas actuales. Backup: src.before_patch47.html."""
import shutil
shutil.copy('src.html', 'src.before_patch47.html')
s = open('src.html', encoding='utf-8').read()
a = "/(banlist|puntos) actual/.test(x)?'u':''}\">${x}</i>`).join('');"
assert s.count(a) == 1
s = s.replace(a, a + "\n  const stale=d.list&&d.list.vk&&!d.list.post?`<i class=\"r\" title=\"${d.list.vk==='pts'?'La receta de este mazo es anterior al ajuste de puntos':'La receta de este mazo es anterior a la banlist actual'}\">${d.list.vk==='pts'?'Receta con puntos anteriores':'Receta con banlist anterior'}</i>`:'';")
b = "<span class=\"meta\">${chips}</span></summary>"
assert s.count(b) == 1
s = s.replace(b, "<span class=\"meta\">${chips}${stale}</span></summary>")
css = '''.meta i.r{color:var(--red);font-weight:700;border-color:color-mix(in srgb,var(--red) 55%,transparent);background:color-mix(in srgb,var(--red) 12%,transparent)}
.meta i.r::before{content:"";display:inline-block;width:6px;height:6px;margin-right:6px;border-radius:50%;background:var(--red);box-shadow:0 0 8px var(--red);vertical-align:1px}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 47 ok')
