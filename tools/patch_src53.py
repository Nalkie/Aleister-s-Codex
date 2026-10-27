"""Frase armada con fragmentos («hay una carta que salió» / «hay N cartas que salieron») -> dos plantillas completas, traducibles. Backup: src.before_patch53.html."""
import shutil
shutil.copy('src.html', 'src.before_patch53.html')
s = open('src.html', encoding='utf-8').read()
a = "return `Ninguna carta de ${f} con ese nombre: ${later===1?'hay una carta que salió':'hay '+later+' cartas que salieron'} después de ese formato (o que no existe en él).`;"
assert s.count(a) == 1
b = "return later===1?`Ninguna carta de ${f} con ese nombre: hay una carta que salió después de ese formato (o que no existe en él).`:`Ninguna carta de ${f} con ese nombre: hay ${later} cartas que salieron después de ese formato (o que no existen en él).`;"
s = s.replace(a, b)
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 53 ok')
