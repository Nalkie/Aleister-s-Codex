"""Personajes (Cajas y sets): la fila de la lista pasa a la lógica de los tiers (arte del personaje translúcido que se desvanece + carta insignia inclinada)
y al elegir un personaje aparece una tarjeta de personaje (retrato enmarcado, mundos, datos y carta insignia) en vez del arte cortado.
Carta insignia = la carta que más define al personaje: rareza, fuentes (mazo inicial 3, drop 2, mazo de personaje 1, nivel 1) y prioridad a monstruos.
Backup: src.before_patch29.html."""
import shutil
shutil.copy('src.html', 'src.before_patch29.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function boxMedia(s,fmt,rep){", r'''const CHAR_SRC={'Starter Deck':3,'Drop':2,'Character Deck':1}, CHAR_RAR={UR:4,SR:3,R:2,N:1};
function charFlag(sel){   // carta insignia de un personaje
  if(sel._flag!==undefined) return sel._flag;
  const w=new Map();
  for(const r of sel.k){ const n=NAMES[r[0]], sub=r[2]||''; w.set(n,(w.get(n)||0)+(CHAR_SRC[sub]||(/^Level/.test(sub)?1:0.5))); }
  let best=null,bs=-1;
  for(const [n,x] of w){ const c=CARDS[n]; if(!c||!c[C.ID]) continue; const sc=(CHAR_RAR[dlRar(n)]||0)*10+x*3+((c[C.CAT]==='m'||c[C.CAT]==='e')?6:0); if(sc>bs){ bs=sc; best=n; } }
  return sel._flag=best;
}
const charFg=sel=>{ const f=charFlag(sel); return f?`<img class="cfg" src="${imgUrl(cardId(f))}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">`:''; };
function charCard(sel){   // tarjeta del personaje elegido
  const c=DLI&&DLI.chars&&DLI.chars[sel.n], f=charFlag(sel), art=charVic(sel.n), por=c&&c.p?'https://s3.duellinksmeta.com'+c.p:'', worlds=(c&&c.w)||[];
  return `<div class="chcard">
    ${art?`<img class="chbg" src="${art}" alt="" referrerpolicy="no-referrer" onerror="this.remove()">`:''}
    ${por?`<div class="chport"><img src="${por}" alt="${esc(sel.n)}" referrerpolicy="no-referrer" onerror="this.parentNode.remove()"></div>`:''}
    <div class="chtxt"><small>Personaje${worlds.length?' · '+worlds.map(esc).join(' · '):''}</small><h3>${esc(sel.n)}</h3>
      <div class="schips"><i>${sel.k.length} cartas</i>${c?`<i>${c.s.length} habilidades</i>`:''}</div>
      ${f?`<p class="chflag">Carta insignia: <b>${esc(f)}</b></p>`:''}</div>
    ${f?`<img class="chfg" src="${imgUrl(cardId(f),true)}" alt="${esc(f)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">`:''}
  </div>`;
}
function boxMedia(s,fmt,rep){''')
a = s.index("  if(fmt==='dl'&&s.kind==='char'&&charVic(s.n)) return `")
b = s.index("`;", a) + 2
old = s[a:b]
assert old.endswith("</span>`;"), old[-40:]
s = s[:a] + old[:-len("</span>`;")] + "</span>${charFg(s)}`;" + s[b:]

rep("    const hero=`<div class=\"sethero${fmt==='tcg'||sel.kind!=='set'?' pack':''}\">${boxMedia(sel,fmt,rn)}<div class=\"shtxt\"><small>${fmt==='tcg'?'Expansión del TCG':esc(KIND_ES[sel.kind]||'')}</small><h3>${esc(sel.n)}</h3></div></div>",
    "    const hero=`${fmt==='dl'&&sel.kind==='char'?charCard(sel):`<div class=\"sethero${fmt==='tcg'||sel.kind!=='set'?' pack':''}\">${boxMedia(sel,fmt,rn)}<div class=\"shtxt\"><small>${fmt==='tcg'?'Expansión del TCG':esc(KIND_ES[sel.kind]||'')}</small><h3>${esc(sel.n)}</h3></div></div>`}")

rep(".fmtbar{margin:var(--s4) 0 0}", """.fmtbar{margin:var(--s4) 0 0}
/* personajes: fila con arte translúcido y carta insignia, como los tiers */
.setb.setb:has(.spack.vic){min-height:100px}
.setb.setb .spack.vic{width:100%;right:0}
.setb.setb .spack.vic img{right:auto;left:26%;top:-26px;height:165%;opacity:.4;-webkit-mask-image:linear-gradient(to right,transparent,#000 22%,#000 72%,transparent);mask-image:linear-gradient(to right,transparent,#000 22%,#000 72%,transparent);filter:drop-shadow(-4px 3px 10px rgba(0,0,0,.45))}
.setb .cfg{position:absolute;right:12px;top:50%;height:116%;aspect-ratio:59/86;translate:0 -47%;rotate:7deg;border-radius:6px;object-fit:cover;box-shadow:0 14px 26px -10px #000,0 0 0 1px rgba(255,255,255,.22);z-index:-1;pointer-events:none;transition:rotate .45s,translate .45s}
.setb:hover .cfg,.setb[aria-pressed="true"] .cfg{rotate:3deg;translate:0 -50%}
.setb.setb:has(.spack.vic) .stxt,.sgrid .setb.setb:has(.spack.vic) .stxt{max-width:calc(100% - 118px)}
.setb:has(.spack.vic) .stxt b,.chtxt h3{text-shadow:0 2px 10px rgba(5,8,25,.85)}
/* tarjeta de personaje */
.chcard{position:relative;isolation:isolate;display:flex;align-items:center;gap:var(--s4);min-height:200px;padding:var(--s4) var(--s5);border-radius:var(--r);border:1px solid color-mix(in srgb,var(--accent) 45%,var(--line2));overflow:hidden;background:linear-gradient(115deg,color-mix(in srgb,var(--accent) 16%,var(--surface)),var(--surface) 62%)}
.chbg{position:absolute;left:26%;top:-8%;height:122%;width:auto;max-width:none;opacity:.34;z-index:-1;pointer-events:none;-webkit-mask-image:linear-gradient(to right,transparent,#000 25%,#000 70%,transparent);mask-image:linear-gradient(to right,transparent,#000 25%,#000 70%,transparent)}
.chport{flex:none;width:118px;border-radius:12px;overflow:hidden;border:2px solid var(--accent);background:var(--surface2);box-shadow:0 14px 28px -12px #000,0 0 0 1px rgba(255,255,255,.12)}
.chport img{display:block;width:100%;height:auto}
.chtxt{display:grid;gap:var(--s2);min-width:0;max-width:52%}
.chtxt small{font:500 .7rem var(--f-data);letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.chtxt h3{font:800 clamp(1.4rem,3vw,2rem) var(--f-display);letter-spacing:-.02em;line-height:1.1}
.chflag{margin:0;color:var(--muted);font-size:.85rem}
.chflag b{color:var(--fg)}
.chfg{position:absolute;right:4%;top:50%;height:128%;aspect-ratio:59/86;translate:0 -47%;rotate:7deg;border-radius:10px;object-fit:cover;box-shadow:0 22px 44px -14px #000,0 0 0 1px rgba(255,255,255,.22);z-index:1;pointer-events:none;transition:rotate .5s,translate .5s}
.chcard:hover .chfg{rotate:3deg;translate:0 -50%}
/* la tarjeta se adapta al ancho que tiene (con la vista previa abierta queda angosta): la carta insignia se achica y nunca tapa el nombre */
.chcard{container-type:inline-size}
@container (max-width:600px){.chfg{height:94%;right:2.5%;top:53%}.chtxt{max-width:calc(100% - 290px)}.chtxt h3{font-size:1.3rem}.chport{width:96px}}
@container (max-width:470px){.chfg{display:none}.chtxt{max-width:none}.chport{width:84px}}
@media(max-width:760px){.chfg{display:none}.chtxt{max-width:none}.chport{width:84px}}
@media(prefers-reduced-motion:reduce){.setb .cfg,.chfg{transition:none}}""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 29 ok')
