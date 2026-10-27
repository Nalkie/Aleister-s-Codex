"""El idioma ya vive en el núcleo de traducción (LANG, patch 49): se quita la copia provisoria del aviso (patch 43). Backup: src.before_patch50.html."""
import shutil
shutil.copy('src.html', 'src.before_patch50.html')
s = open('src.html', encoding='utf-8').read()
a = "let LANG='es';\nconst tr=k=>"
assert s.count(a) == 1
s = s.replace(a, "const tr=k=>")
s = s.replace("/* textos traducibles: para sumar un idioma se agrega otro objeto en I18N y se cambia LANG */", "/* textos de los avisos: el inglés sale del diccionario (tools/i18n_en.json), no hace falta otro objeto aquí */")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 50 ok')
