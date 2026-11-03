"""Ruleta de decks: los Reemplazos pasan de carrusel de tarjetas con imagen a una lista pequeña (una línea por reemplazo: ~~carta del anime~~ → carta del TCG), en columnas que se
acomodan al ancho.  Con cualquier cantidad de reemplazos queda corta y no rompe el flujo de la página; tocar la carta abre su ficha como antes.  Backup: src.before_patch70.html."""
import re, shutil

shutil.copy('src.html', 'src.before_patch70.html')
s = open('src.html', encoding='utf-8').read()
m = open('tools/mobile.css', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


i = s.index('  const swp=sw.length?`<div class="rou-sw">')
j = s.index('\n', i)
s = s[:i] + ("  const swp=sw.length?`<div class=\"rou-sw\"><h4>Reemplazos · ${sw.length}</h4><ul class=\"rou-swl\">${sw.map(([a,b])=>`<li><button class=\"rou-sw1\" data-card=\"${esc(canon(b))}\" "
             "title=\"${esc(a)} → ${esc(b)} · No existe en el TCG\"><s>${esc(a)}</s><span aria-hidden=\"true\"> → </span><b>${esc(b)}</b></button></li>`).join('')}</ul></div>`:'';") + s[j:]

i = s.index('.rou-swrow{display:flex')
j = s.index('.rou-swn{grid-area:n')
j = s.index('\n', j) + 1
s = s[:i] + (".rou-swl{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:2px var(--s4)}\n"
             ".rou-sw1{display:block;width:100%;text-align:left;background:none;border:0;border-radius:var(--r1,6px);padding:3px var(--s2);cursor:pointer;color:var(--fg);font:500 .82rem/1.35 var(--f-body);overflow-wrap:anywhere}\n"
             ".rou-sw1:hover{background:var(--surface)} .rou-sw1 s{color:var(--muted);text-decoration-color:var(--red);text-decoration-thickness:1.5px} .rou-sw1 span{color:var(--accent);font-weight:800} .rou-sw1 b{font-weight:700}\n") + s[j:]
rep("  .rou-sw1{width:240px}\n", "")
m2 = m.replace("  .rou-sw1{width:240px}\n", "")
assert m2 != m
open('tools/mobile.css', 'w', encoding='utf-8').write(m2)
for k in ('rou-swrow', 'rou-swart', 'rou-swn', 'rou-swa'):
    assert k not in s, k
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 70 ok')
