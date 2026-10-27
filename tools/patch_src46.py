"""Corrección del patch 44/45: Edison, Goat y HAT (formatos históricos, sin fecha de referencia) no llevan insignia ni aviso rojo.
La clase de insignia (vk) solo existe cuando los datos traen la fecha en que rigen las reglas actuales (ref). Backup: src.before_patch46.html."""
import shutil
shutil.copy('src.html', 'src.before_patch46.html')
s = open('src.html', encoding='utf-8').read()
a = "vk:fmt==='gen'?'pts':'ban'"
assert s.count(a) == 2, s.count(a)
s = s.replace(a, "vk:D.ref?(fmt==='gen'?'pts':'ban'):''")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 46 ok')
