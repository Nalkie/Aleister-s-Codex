"""Personajes: el arte de victoria (512x512, fondo transparente) sale del recuadro en las listas y en la ficha, en vez del retrato enmarcado.
Sin arte de victoria se usa el retrato de antes. Backup: src.before_patch22.html."""
import shutil
shutil.copy('src.html', 'src.before_patch22.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# helper: victory art of a character (needs DLI, the info file that loads on demand)
rep("function boxMedia(s,fmt,rep){",
    "const charVic=n=>{ const c=typeof DLI!=='undefined'&&DLI&&DLI.chars&&DLI.chars[n]; return c&&c.v?'https://s3.duellinksmeta.com'+c.v.split('/').map(encodeURIComponent).join('/'):''; };\n"
    "function boxMedia(s,fmt,rep){")
rep("  const u=boxUrl(s,fmt);\n",
    "  const u=boxUrl(s,fmt);\n  if(fmt==='dl'&&s.kind==='char'&&!DLI) loadEv();   // el arte de victoria viene del archivo de info de Duel Links\n")
rep("  if(fmt==='dl'&&s.kind==='char'&&u) return",
    "  if(fmt==='dl'&&s.kind==='char'&&charVic(s.n)) return `<span class=\"spack char vic\"><img src=\"${charVic(s.n)}\" alt=\"\" loading=\"lazy\" decoding=\"async\" referrerpolicy=\"no-referrer\" onerror=\"this.parentNode.remove()\"></span>`;\n"
    "  if(fmt==='dl'&&s.kind==='char'&&u) return")
# list in Eventos > Personajes
rep("<span class=\"spack char\">${c.p?`<img src=\"https://s3.duellinksmeta.com${c.p}\" alt=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer\" onerror=\"this.remove()\">`:''}</span>",
    "<span class=\"spack char${c.v?' vic':''}\">${c.v||c.p?`<img src=\"https://s3.duellinksmeta.com${c.v||c.p}\" alt=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer\" onerror=\"this.remove()\">`:''}</span>")
# detail card
rep("${c.p?`<span class=\"cportrait\"><img src=\"https://s3.duellinksmeta.com${c.p}\" alt=\"${esc(sel)}\" referrerpolicy=\"no-referrer\"></span>`:''}",
    "${c.v?`<span class=\"cvic\"><img src=\"https://s3.duellinksmeta.com${c.v}\" alt=\"${esc(sel)}\" referrerpolicy=\"no-referrer\"></span>`:c.p?`<span class=\"cportrait\"><img src=\"https://s3.duellinksmeta.com${c.p}\" alt=\"${esc(sel)}\" referrerpolicy=\"no-referrer\"></span>`:''}")
# css
rep(".cportrait img{display:block;width:100%;height:auto}",
    """.cportrait img{display:block;width:100%;height:auto}
/* arte de victoria: sale del recuadro, se inclina al pasar el mouse y deja ver la cara */
.setb:has(.spack.vic){min-height:96px}
.setb .spack.vic{right:0;top:0;bottom:0;translate:none;width:46%;height:100%;display:block;z-index:-1;overflow:visible;pointer-events:none}
.setb .spack.vic img{position:absolute;right:-14px;top:-30px;height:172%;width:auto;max-width:none;object-fit:contain;object-position:right top;
  filter:drop-shadow(-6px 4px 12px rgba(0,0,0,.5));transform-origin:80% 30%;transition:transform .45s cubic-bezier(.2,.7,.2,1)}
.setb:hover .spack.vic img,.setb[aria-pressed="true"] .spack.vic img{transform:scale(1.1) rotate(-2.5deg) translate(-4px,2px)}
.setb:has(.spack.vic) .stxt{max-width:calc(100% - 96px)}
.sgrid .setb:has(.spack.vic) .stxt{max-width:calc(100% - 96px)}
.sethero.pack .spack.vic{width:50%;right:0}
.sethero.pack .spack.vic img{height:150%;top:-20px;right:0}
.hero-card .cvic{flex:none;width:170px;height:150px;position:relative;margin-right:var(--s3)}
.hero-card .cvic img{position:absolute;left:-8px;bottom:0;width:190px;height:190px;max-width:none;object-fit:contain;filter:drop-shadow(0 8px 14px rgba(0,0,0,.5));transition:transform .5s cubic-bezier(.2,.7,.2,1)}
.hero-card:hover .cvic img{transform:scale(1.06) rotate(-2deg)}
@media(prefers-reduced-motion:reduce){.setb .spack.vic img,.hero-card .cvic img{transition:none}.setb:hover .spack.vic img{transform:none}}
@media(max-width:760px){.setb .spack.vic{width:40%}.hero-card .cvic{width:120px;height:110px}.hero-card .cvic img{width:140px;height:140px}}""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 22 ok')
