"""Ruleta de decks: el selector de series (seis series más «Todas») dejaba el último botón solo en una segunda línea, dentro de una píldora.  Ahora es un contenedor redondeado de ancho
completo con una grilla de 12 columnas: cuatro botones arriba y tres abajo, parejos.  En el teléfono sigue siendo una
sola fila con scroll horizontal.  Backup: src.before_patch74.html."""
import shutil

shutil.copy('src.html', 'src.before_patch74.html')
s = open('src.html', encoding='utf-8').read()
a = ".rou-ser{margin:0;max-width:100%}\n.rou-ser button{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}"
assert s.count(a) == 1
b = (".rou-ser{margin:0;width:100%;max-width:100%;border-radius:var(--r2);gap:var(--s1);display:grid;grid-template-columns:repeat(12,minmax(0,1fr))}
"
     ".rou-ser button{display:inline-flex;align-items:center;justify-content:center;gap:6px;white-space:nowrap;grid-column:span 4;padding:0 10px}
"
     ".rou-ser button:nth-child(-n+4){grid-column:span 3}")
s = s.replace(a, b)
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 74 ok')
