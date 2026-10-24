"""Ronda 2: carta insignia en todas las filas de tier, orden por rareza en cajas, colores y animaciones por rareza, más artes alternativos,
arte lineal en los costados, ícono de Duel Links. Backup: src.before_patch17.html."""
import shutil
shutil.copy('src.html', 'src.before_patch17.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---- artworks: numbers are passcodes (YGOPRODeck), 'd:<id>' are Duel Links Meta alternate cards
rep("const imgUrl = (id,big) => `https://images.ygoprodeck.com/images/${big?'cards':'cards_small'}/${id}.jpg`;",
    "const imgUrl = (id,big) => typeof id==='string' ? `https://s3.duellinksmeta.com/cards/${id.slice(2)}_w${big?360:200}.webp` : `https://images.ygoprodeck.com/images/${big?'cards':'cards_small'}/${id}.jpg`;")
rep("const cardId = n => { n=canon(n); const c=CARDS[n]; if(!c) return 0; const a=ARTSEL[n]; return a&&(ALTS[n]||[]).includes(a)?a:c[C.ID]; };",
    "const mainId = n => { n=canon(n); const c=CARDS[n]; if(!c) return 0; const a=ALTS[n]; return a&&typeof a[0]==='number'?a[0]:c[C.ID]; };   // el passcode del arte original\n"
    "const cardId = n => { n=canon(n); const c=CARDS[n]; if(!c) return 0; const a=ARTSEL[n], al=ALTS[n]; if(a&&al&&al.includes(a)) return a; return al?al[0]:c[C.ID]; };")
rep("  return `<span class=\"cf\"${fo?` data-fo=\"${fo}\"`:''}>${thumb(n)}${src?`<img src=\"${src}\" alt=\"${esc(n)}\" loading=\"lazy\" decoding=\"async\" referrerpolicy=\"no-referrer\" onerror=\"this.remove()\">`:''}</span>`;",
    "  const c=CARDS[canon(n)], alt=c&&c[C.DID]&&!/s3\\.duellinksmeta/.test(src)?`https://s3.duellinksmeta.com/cards/${c[C.DID]}_w${big?360:200}.webp`:'';   // si YGOPRODeck no tiene la imagen, la de Duel Links Meta\n"
    "  return `<span class=\"cf\"${fo?` data-fo=\"${fo}\"`:''}>${thumb(n)}${src?`<img src=\"${src}\"${alt?` data-alt=\"${alt}\"`:''} alt=\"${esc(n)}\" loading=\"lazy\" decoding=\"async\" referrerpolicy=\"no-referrer\" onerror=\"var a=this.dataset.alt;if(a){this.removeAttribute('data-alt');this.src=a}else this.remove()\">`:''}</span>`;")
rep("title=\"${i?'Arte alternativo '+i:'Arte original'}\"><img src=\"${imgUrl(id)}\" alt=\"${i?'Arte alternativo '+i:'Arte original'}\"",
    "title=\"${i?'Arte alternativo '+i+(typeof id==='string'?' (Duel Links)':''):'Arte original'}\"><img src=\"${imgUrl(id)}\" alt=\"${i?'Arte alternativo '+i:'Arte original'}\"")
rep("else if(d.art){ setArt(d.artn,+d.art); render(); }", "else if(d.art){ setArt(d.artn,/^\\d+$/.test(d.art)?+d.art:d.art); render(); }")
rep("Array(k).fill(CARDS[n]?CARDS[n][C.ID]:0)).filter(Boolean);", "Array(k).fill(mainId(n))).filter(Boolean);")

# ---- rarity: groups, colours, order
rep("const FOIL = {C:'n',N:'n',SPR:'n',DNPR:'par',DRPR:'par',DUPR:'par',R:'r',SR:'sr',SHR:'sr',UR:'ur',PG:'ur',GUR:'ur',GMR:'ur',UtR:'ut',UL:'ut',CR:'cr',ScR:'sc',GScR:'sc',PScR:'pr',QCScR:'qc',StR:'st',GR:'gh'};",
    "const FOIL = {C:'n',N:'n',SPR:'n',DNPR:'par',DRPR:'par',DUPR:'par',R:'r',SR:'sr',SHR:'shr',UR:'ur',GUR:'gur',GMR:'gur',PG:'pg',UtR:'ut',UL:'ut',CR:'cr',ScR:'sc',GScR:'gsc',PScR:'pr',QCScR:'qc',StR:'st',GR:'gh'};\n"
    "const ffoil = (r,fmt) => fmt==='tcg' ? foil(r) : ({N:'n',R:'r',SR:'dsr',UR:'dur'}[r]||'n');          // Duel Links usa sus propios efectos\n"
    "const rchip = (r,fmt) => fmt==='tcg' ? 'rt rt-'+foil(r) : 'rr rr-'+r;\n"
    "const RAR_ORDER = ['N','C','SPR','DNPR','DRPR','DUPR','R','SR','SHR','UR','GUR','GMR','UtR','UL','PG','GR','CR','ScR','GScR','PScR','StR','QCScR'];   // de menor a mayor\n"
    "const GROUP_RANK = {n:1,par:3,r:6,sr:7,shr:8,ur:9,gur:10,ut:12,pg:13,gh:15,cr:16,sc:17,gsc:18,pr:19,st:20,qc:21};\n"
    "const rarRank = (r,fmt) => fmt==='dl' ? ({N:1,R:2,SR:3,UR:4}[r]||0) : (RAR_ORDER.indexOf(r)>=0?RAR_ORDER.indexOf(r):GROUP_RANK[foil(r)]||0);")
rep("const SETS = {fmt:'tcg',q:'',sel:null,card:null,rar:null,cq:'',rf:'all',kind:'set',limit:80,cl:SCL,data:{},loading:false};",
    "const SETS = {fmt:'tcg',q:'',sel:null,card:null,rar:null,cq:'',rf:'all',desc:false,kind:'set',limit:80,cl:SCL,data:{},loading:false};")
rep("  return {rows:fmt==='tcg'?[...rows].sort((a,b)=>a[1].localeCompare(b[1],undefined,{numeric:true})):[...rows].sort((a,b)=>NAMES[a[0]].localeCompare(NAMES[b[0]])),rarOf};",
    "  const dir=SETS.desc?-1:1;      // por defecto de menor a mayor rareza; dentro de cada rareza por número (TCG) o nombre (Duel Links)\n"
    "  const cmp=(a,b)=>dir*(rarRank(rarOf(a),fmt)-rarRank(rarOf(b),fmt))||(fmt==='tcg'?a[1].localeCompare(b[1],undefined,{numeric:true}):NAMES[a[0]].localeCompare(NAMES[b[0]]));\n"
    "  return {rows:[...rows].sort(cmp),rarOf};")
rep("<span class=\"art\">${cardImg(n,false,foil(rar))}</span><span class=\"tn\">${esc(n)}</span><span class=\"tm\"><b class=\"rr rr-${esc(rar)}\">${esc(rar)}</b>",
    "<span class=\"art\">${cardImg(n,false,ffoil(rar,fmt))}</span><span class=\"tn\">${esc(n)}</span><span class=\"tm\"><b class=\"${rchip(rar,fmt)}\">${esc(rar)}</b>")
rep("<span class=\"art\">${cardImg(n,false,foil(r[2]))}</span><b class=\"rr rr-${esc(r[2])}\">${esc(r[2])}</b>", "<span class=\"art\">${cardImg(n,false,foil(r[2]))}</span><b class=\"${rchip(r[2],'tcg')}\">${esc(r[2])}</b>")
rep("<span class=\"art\">${cardImg(n,false,foil(rar))}</span><b class=\"rr rr-${esc(rar)}\">${esc(rar)}</b>", "<span class=\"art\">${cardImg(n,false,ffoil(rar,'dl'))}</span><b class=\"${rchip(rar,'dl')}\">${esc(rar)}</b>")
rep("${cardImg(n,true,foil(SETS._cur))}", "${cardImg(n,true,ffoil(SETS._cur,fmt))}")
# order of the rarity filter, grouped grid with headings, order toggle
rep(".sort((a,b)=>(TCG_RANK[b]||RAR_RANK[b]||0)-(TCG_RANK[a]||RAR_RANK[a]||0));", ".sort((a,b)=>rarRank(b,fmt)-rarRank(a,fmt));")
rep("      <div class=\"gal sgal\">${cs.map(r=>sTile(r,sel,fmt,rarOf)).join('')}</div>",
    "      <div class=\"gal sgal\">${(()=>{ const cnt={}; for(const r of rows){ const k=rarOf(r); cnt[k]=(cnt[k]||0)+1; } let last=null; return cs.map(r=>{ const k=rarOf(r); let h=''; if(k!==last){ last=k; h=`<h4 class=\"rgh\"><b class=\"${rchip(k,fmt)}\">${esc(k)}</b>${esc(RAR_ES[k]||'')} · ${cnt[k]}</h4>`; } return h+sTile(r,sel,fmt,rarOf); }).join(''); })()}</div>")
rep("<option value=\"all\">Todas las rarezas</option>${rarList.map(", "<option value=\"all\">Todas las rarezas</option>${rarList.map(")
rep("${RAR_ES[r]?' · '+esc(RAR_ES[r]):''}</option>`).join('')}</select></div>`;",
    "${RAR_ES[r]?' · '+esc(RAR_ES[r]):''}</option>`).join('')}</select>\n        <button class=\"abtn\" data-sdesc=\"1\" title=\"Cambiar el orden de las cartas por rareza\">Orden: ${SETS.desc?'mayor a menor rareza':'menor a mayor rareza'}</button></div>`;")
rep("  else if(d.sclose){ SETS.card=null; render(); }", "  else if(d.sclose){ SETS.card=null; render(); }\n  else if(d.sdesc){ SETS.desc=!SETS.desc; SETS.cl=SCL; render(); }")
rep("Cada rareza se ve distinta: tocá una para verla en grande${fmt==='tcg'?' con su precio':''}.", "Ordenadas por rareza; cada una tiene su color y su efecto. Tocá una para verla en grande${fmt==='tcg'?' con su precio':''}.")

# ---- insignia card on every tier row (guide too)
rep("fg=i===1&&cid?`<img class=\"card-fg\" src=\"${imgUrl(cid)}\" alt=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer\" onerror=\"this.remove()\">`:'';",
    "fg=cid?`<img class=\"card-fg\" style=\"--rot:${i%2?-5:6}deg\" src=\"${imgUrl(cid)}\" alt=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer\" onerror=\"this.remove()\">`:'';")
rep("  const {e,parts}=guideEntry(d.n), art=artOf(d.art);\n  const keys=", "  const {e,parts}=guideEntry(d.n), art=artOf(d.art), cid=ARTS[d.art];\n  const fg=cid?`<img class=\"card-fg\" style=\"--rot:${i%2?-5:6}deg\" src=\"${imgUrl(cid)}\" alt=\"\" loading=\"lazy\" referrerpolicy=\"no-referrer\" onerror=\"this.remove()\">`:'';\n  const keys=")
rep("style=\"object-position:50% ${artPos(d.art)}\">`:'<div class=\"artph\"></div>'}\n    <span class=\"rank\">${i}</span><span class=\"dname\">${esc(d.n)}</span><span class=\"bar gchips\">",
    "style=\"object-position:50% ${artPos(d.art)}\">`:'<div class=\"artph\"></div>'}${fg}\n    <span class=\"rank\">${i}</span><span class=\"dname\">${esc(d.n)}</span><span class=\"bar gchips\">")

# ---- side line art + Duel Links icon
rep("<div class=\"wrap\">\n<header class=\"hero\">", "<div class=\"sideart l\" aria-hidden=\"true\"></div><div class=\"sideart r\" aria-hidden=\"true\"></div>\n<div class=\"wrap\">\n<header class=\"hero\">")
a = s.index('<svg class="glyph" viewBox="0 0 48 48" aria-hidden="true"><rect x="13" y="5"')
b = s.index('</svg>', a) + len('</svg>')
s = s[:a] + ('<svg class="glyph" viewBox="0 0 48 48" aria-hidden="true"><defs><linearGradient id="dlg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5ab0ff"/><stop offset="1" style="stop-color:var(--mc)"/></linearGradient></defs>'
             '<g stroke="url(#dlg)"><path d="M24 4.5A19.5 19.5 0 1 1 6.2 15.6"/><path d="M24 12A12 12 0 1 0 35.2 28.5"/><ellipse cx="19.5" cy="26" rx="4.6" ry="8.2" transform="rotate(35 19.5 26)"/><ellipse cx="28.5" cy="22" rx="4.6" ry="8.2" transform="rotate(35 28.5 22)"/><path d="M40 7l1.7 3.5 3.5 1.7-3.5 1.7L40 17.4l-1.7-3.5-3.5-1.7 3.5-1.7z"/></g></svg>') + s[b:]

# ---- css
rep("</style>\n\n<div class=\"sideart", """.mode[data-mode="dl"]{background-image:radial-gradient(circle at 10% 15%,rgba(80,150,255,.20),transparent 55%),linear-gradient(160deg,color-mix(in srgb,var(--surface) 92%,transparent),color-mix(in srgb,var(--surface2) 80%,transparent))}
.mode[data-mode="dl"][aria-selected="true"]{background-image:radial-gradient(circle at 10% 15%,rgba(80,150,255,.30),transparent 60%),linear-gradient(160deg,color-mix(in srgb,var(--mc) 20%,var(--surface)),var(--surface2))}

/* arte lineal en los costados (máscara: toma el color del modo) */
.sideart{position:fixed;top:110px;bottom:0;width:min(24vw,330px);pointer-events:none;z-index:-1;opacity:.15;background:var(--accent);-webkit-mask:var(--img) center bottom/contain no-repeat;mask:var(--img) center bottom/contain no-repeat;transition:background .4s}
.sideart.l{left:-24px;--img:url(art/line-aleister.png)}
.sideart.r{right:-24px;--img:url(art/line-ecclesia.png)}
@media(max-width:1240px){.sideart{display:none}}

/* insignia de cada mazo: la carta real en todas las filas */
.deck .card-fg{position:absolute;right:5%;top:50%;height:132%;aspect-ratio:59/86;translate:0 -46%;rotate:var(--rot,6deg);border-radius:6px;box-shadow:0 14px 30px -10px #000,0 0 0 1px rgba(255,255,255,.2);z-index:1;pointer-events:none;transition:rotate .5s,translate .5s;object-fit:cover}
.deck:hover .card-fg{rotate:calc(var(--rot,6deg) / 2);translate:0 -50%}
.deck.feat .card-fg{height:150%;right:6%}

/* rarezas del TCG: cada una con su color y su efecto (los efectos se mueven en la carta grande, en las rarezas del panel y al pasar el mouse) */
.rgh{grid-column:1/-1;display:flex;align-items:center;gap:var(--s2);margin:var(--s3) 0 0;font:600 .78rem var(--f-data);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.rgh::after{content:"";flex:1;height:1px;background:linear-gradient(90deg,var(--line2),transparent)}
.rt{display:inline-block;font:700 .85rem var(--f-data);padding:3px 10px;border-radius:99px;line-height:1.2;color:#10132e;background:#9aa4d6;letter-spacing:.04em}
.pv .rt{font-size:.74rem;padding:2px 8px}
.rt-n{background:linear-gradient(135deg,#f4f6ff,#c4cae3)}
.rt-par{background:linear-gradient(135deg,#a8fff0,#4ad0c0)}
.rt-r{background:linear-gradient(135deg,#a5c8ff,#5b8ff0)}
.rt-sr{background:linear-gradient(135deg,#9ff3ff,#7aa0ff 55%,#c79bff)}
.rt-shr{background:linear-gradient(135deg,#e1c2ff,#a46bff)}
.rt-ur{background:linear-gradient(135deg,#ffe99a,#ffb93b)}
.rt-gur,.rt-pg{background:linear-gradient(135deg,#ffd07a,#ff9a3c)}
.rt-ut{background:linear-gradient(135deg,#ffb27a,#ff7a3c)}
.rt-gh{background:linear-gradient(135deg,#ffffff,#d6dcee)}
.rt-cr{background:linear-gradient(135deg,#ff9fb0,#e0405f);color:#fff}
.rt-sc{background:linear-gradient(135deg,#ff9bd2,#8be4ff,#fff08a)}
.rt-gsc{background:linear-gradient(135deg,#ffe58a,#ff9bd2,#ffd25a)}
.rt-pr{background:linear-gradient(135deg,#ffa8e6,#b49bff,#8ff0ff)}
.rt-st{background:linear-gradient(135deg,#ffffff,#9fe8ff 50%,#d9b8ff);box-shadow:0 0 10px -2px #9fe8ff}
.rt-qc{background:linear-gradient(135deg,#ffd9a0,#d9902f);box-shadow:0 0 10px -2px #ffd25a}
.cf[data-fo="shr"]::before{background:conic-gradient(from 20deg at 50% 50%,rgba(190,140,255,.0),rgba(190,140,255,.45),rgba(255,255,255,.0),rgba(120,200,255,.4),rgba(190,140,255,.0));mix-blend-mode:screen}
.cf[data-fo="gur"],.cf[data-fo="pg"]{border-color:#ffb86a}
.cf[data-fo="gur"]::before,.cf[data-fo="pg"]::before{background:linear-gradient(100deg,transparent 15%,rgba(255,196,110,.95) 45%,transparent 75%) 0 0/100% 12% no-repeat,linear-gradient(130deg,transparent 10%,rgba(255,170,70,.5) 40%,rgba(255,235,170,.3) 55%,transparent 85%);mix-blend-mode:screen}
.cf[data-fo="gsc"]::before{background:repeating-linear-gradient(45deg,rgba(255,226,130,.30) 0 1px,transparent 1px 5px),repeating-linear-gradient(-45deg,rgba(255,150,210,.26) 0 1px,transparent 1px 5px),linear-gradient(135deg,rgba(255,215,110,.25),rgba(255,150,210,.2));mix-blend-mode:screen}
/* Duel Links: SR dorada con brillo, UR arcoíris con destellos (la misma animación se usa para Starlight en el TCG) */
.cf[data-fo="dsr"]{border-color:#ffd25a}
.cf[data-fo="dsr"]::before{background:linear-gradient(120deg,transparent 15%,rgba(255,215,100,.5) 40%,rgba(255,255,255,.35) 50%,rgba(255,190,60,.45) 62%,transparent 85%);mix-blend-mode:screen}
.cf[data-fo="dur"]{border-color:#b69bff}
.cf[data-fo="dur"]::before,.cf[data-fo="st"]::before{background:radial-gradient(circle,rgba(255,255,255,.95) 0 1px,transparent 1.8px) 0 0/11px 11px,radial-gradient(circle,rgba(190,230,255,.9) 0 1px,transparent 1.8px) 5px 6px/15px 15px,conic-gradient(from 0deg at 50% 60%,rgba(255,120,200,.28),rgba(120,200,255,.3),rgba(255,240,140,.28),rgba(160,255,200,.28),rgba(255,120,200,.28));mix-blend-mode:screen}
.cf[data-fo="st"]::before{background:radial-gradient(circle,rgba(255,255,255,.95) 0 1px,transparent 1.8px) 0 0/11px 11px,radial-gradient(circle,rgba(190,230,255,.9) 0 1px,transparent 1.8px) 5px 6px/15px 15px,linear-gradient(135deg,rgba(150,210,255,.22),rgba(210,160,255,.22))}
@keyframes fshine{from{background-position:-140% 0}to{background-position:240% 0}}
@keyframes fhue{to{filter:hue-rotate(360deg)}}
@keyframes ftwinkle{0%,100%{opacity:.45}50%{opacity:1}}
.bigcard .cf[data-fo]:not([data-fo="n"])::after,.pv .cf[data-fo]:not([data-fo="n"])::after{content:"";position:absolute;inset:0;z-index:3;pointer-events:none;background:linear-gradient(115deg,transparent 38%,rgba(255,255,255,.5) 50%,transparent 62%) 0 0/260% 100%;mix-blend-mode:overlay;animation:fshine 3.2s linear infinite}
.bigcard .cf[data-fo="sc"]::before,.pv .cf[data-fo="sc"]::before,.tile:hover .cf[data-fo="sc"]::before,
.bigcard .cf[data-fo="gsc"]::before,.pv .cf[data-fo="gsc"]::before,.tile:hover .cf[data-fo="gsc"]::before,
.bigcard .cf[data-fo="pr"]::before,.pv .cf[data-fo="pr"]::before,.tile:hover .cf[data-fo="pr"]::before,
.bigcard .cf[data-fo="shr"]::before,.pv .cf[data-fo="shr"]::before,.tile:hover .cf[data-fo="shr"]::before,
.bigcard .cf[data-fo="dur"]::before,.pv .cf[data-fo="dur"]::before,.tile:hover .cf[data-fo="dur"]::before,
.bigcard .cf[data-fo="sr"]::before,.pv .cf[data-fo="sr"]::before,.tile:hover .cf[data-fo="sr"]::before,
.bigcard .cf[data-fo="qc"]::before,.pv .cf[data-fo="qc"]::before,.tile:hover .cf[data-fo="qc"]::before{animation:fhue 5s linear infinite}
.bigcard .cf[data-fo="st"]::before,.pv .cf[data-fo="st"]::before,.tile:hover .cf[data-fo="st"]::before,
.bigcard .cf[data-fo="dur"]::before,.pv .cf[data-fo="dur"]::before{animation:ftwinkle 1.6s ease-in-out infinite,fhue 8s linear infinite}
.pvs{grid-template-columns:repeat(auto-fill,minmax(104px,1fr))}
@media(prefers-reduced-motion:reduce){.cf[data-fo]::before,.cf[data-fo]::after{animation:none!important}.deck .card-fg{transition:none}}
</style>

<div class="sideart""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch17 ok')
