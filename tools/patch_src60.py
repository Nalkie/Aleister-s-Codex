"""Precio real de TCGplayer de cada versión: el más bajo en venta y, si no hay publicaciones, el de mercado (src/tcgprices.json -> tools/prices.py).
La fuente queda en el sexto lugar de la impresión (0 = más bajo en venta, 1 = mercado) y el título del precio la dice.  Backup: src.before_patch60.html."""
import shutil
shutil.copy('src.html', 'src.before_patch60.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep("const own=nz(p[3]); if(own) return {u:own,est:0};", "const own=nz(p[3]); if(own) return {u:own,est:0,src:p[5]};")
rep("const tip=!v.est?'Precio de esta versión en TCGplayer':", "const tip=!v.est?(v.src===0?'Precio más bajo en venta en TCGplayer':v.src===1?'Precio de mercado de TCGplayer (esta versión no tiene publicaciones a la venta)':'Precio de esta versión en TCGplayer'):")
rep(":'Precio en TCGplayer';", ":'Precio en TCGplayer (el de su versión más barata)';")
rep("""   ${FXR.ars?`<p class="rnote">Dólar blue (venta)""", """   <p class="rnote">El precio de TCGplayer de la carta es el de su versión más barata: cada versión tiene el suyo más abajo.</p>
   ${FXR.ars?`<p class="rnote">Dólar blue (venta)""")
open('src.html', 'w', encoding='utf-8').write(s)

r = open('tools/refresh.py', encoding='utf-8').read()
a = "'src/prices.json', 'src/fx_ars.json',"
assert r.count(a) == 1
r = r.replace(a, "'src/prices.json', 'src/fx_ars.json', 'src/tcgprices.json',")
b = "steps.append(('tools/tcgp.py', '--refresh'))"
assert r.count(b) == 1
r = r.replace(b, b + "\n        steps.append(('tools/fetch_tcg_prices.py',))      # unos 70 minutos: un pedido por página de cada expansión")
open('tools/refresh.py', 'w', encoding='utf-8').write(r)
print('patch 60 ok')
