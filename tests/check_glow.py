"""Gate: nada de brillos sueltos (halos que se derraman, manchas, sombras oscuras en el tema claro).  Run from the project root:  python tests/check_glow.py

Nació de un informe: «aparece un brillo anómalo sin razón aparente».  Un crítico recorrió toda la página y probó cuatro orígenes:
  1. .tier::before: halo de 340 px que, con el tier plegado (60 px), se derramaba sobre los tiers y títulos de abajo
  2. .rstat::after: círculo claro en la esquina de cada tarjeta de estadística (se leía como mancha)
  3. .deck .dname / .deck .pct: sombra de texto de tinta oscura con color fijo, que en el tema claro ensuciaba el texto
  4. .chtxt (cabecera de la tarjeta de «Otras vías»): lo mismo en el celular con el tema claro
  5. body: segundo degradado radial (velo violeta a la izquierda): anclado al 26 % de la altura caía a miles de px del inicio; anclado arriba quedaba sobre la silueta. Se eliminó
  6. .sideart.l: silueta con brillo celeste a la izquierda, fija a la ventana: acompañaba todo el scroll en vez de quedar solo arriba
Cada uno queda cerrado por una regla que este test exige.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
fails = []


def ok(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


src = open('src.html', encoding='utf-8').read().replace('\r\n', '\n')

ok('.tier:not([open])::before{display:none}' in src and 'height:min(340px,100%)' in src, 'el halo del tier no se dibuja plegado y nunca pasa del alto del tier')
ok('.rstat::after' not in src, 'las tarjetas de estadística no llevan el círculo claro de la esquina')
ok(src.count('--tsh:') == 3 and '--tsh:255,255,255' in src and src.count('--tsh:4,7,22') == 2, 'el color de la sombra de texto es una variable: claro en el tema claro, tinta en los dos modos oscuros (3 definiciones)')
shadows = re.findall(r'(\.deck \.dname,\.deck \.pct|\.setb:has\(\.spack\.vic\) \.stxt b,\.chtxt h3|\.chcard \.chtxt)\{text-shadow:([^}]*)\}', src)
ok(len(shadows) == 3 and all('var(--tsh)' in s for _, s in shadows), 'las sombras de texto de los títulos de mazo y de la tarjeta de «Otras vías» usan --tsh, no un color oscuro fijo (%d reglas)' % len(shadows))
ok(not re.search(r'text-shadow:[^;}]*rgba\((4|5),\s?(7|8),\s?(22|25)', src), 'no queda ninguna sombra de texto con la tinta oscura escrita a mano')

m = re.search(r"body\{background:(.*?)var\(--bg\)", src, re.S)
bgd = m.group(1) if m else ''
ok(bool(m) and bgd.count('radial-gradient') == 1 and 'at 88% -140px' in bgd, 'el body tiene un solo degradado radial (el resplandor de arriba a la derecha, detrás del círculo): sin velo violeta a la izquierda')

ok(re.search(r'\.sideart\{position:fixed', src) is not None and '.sideart.l{left:-5vw;' in src and not re.search(r'\.sideart\.l\{[^}]*position:absolute', src), 'las dos siluetas (.sideart.l y .sideart.r) son fijas y acompañan el scroll: la izquierda no se ancla al inicio de la página')

print('failed:', len(fails))
sys.exit(1 if fails else 0)
