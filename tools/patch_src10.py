"""Box explorer: art-backed rows and hero header with the box's most representative card, plus a hexagram favicon."""
import shutil, re
shutil.copy('src.html','src.before_patch10.html')
s=open('src.html',encoding='utf-8').read()
def rep(a,b):
    global s
    assert s.count(a)==1,a[:80]
    s=s.replace(a,b)

# favicon: unicursal hexagram in a circle
fav=("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 48 48'%3E%3Crect width='48' height='48' rx='12' fill='%230b1030'/%3E"
     "%3Ccircle cx='24' cy='24' r='19' fill='none' stroke='%234ee1ff' stroke-width='1.8'/%3E"
     "%3Cpath d='M24 8 L37.9 32 L10.1 16 L24 40 L37.9 16 L10.1 32 Z' fill='none' stroke='%23b78bff' stroke-width='2.6' stroke-linejoin='round'/%3E%3C/svg%3E")
rep('<title>Aleister\'s Codex</title>','<title>Aleister\'s Codex</title>\n<link rel="icon" type="image/svg+xml" href="%s">'%fav)

js = r'''const RAR_RANK={UR:4,SR:3,R:2,N:1};
const TCG_RANK={QCScR:9,StR:9,GScR:8,PScR:8,ScR:7,UtR:7,GMR:7,CR:6,UR:6,GUR:6,PG:6,SHR:5,SR:4,SPR:3,R:2,C:1};
function boxRep(s,fmt){
  if(s._rep!==undefined) return s._rep;
  let best=null,bs=-1;
  for(const r of s.k){
    const n=NAMES[r[0]], c=CARDS[n]; if(!c||!c[C.ID]) continue;
    let sc;
    if(fmt==='tcg') sc=(TCG_RANK[r[2]]||0)*1000+Math.min(r[3]||0,500)+(c[C.FL]&8?200:0)-(c[C.CAT]>=3?0:0);
    else { const i=DLD.cards[n]; sc=((i&&RAR_RANK[i.r])||0)*1000+(c[C.FL]&8?300:0)+(r[1]||0); }
    if(sc>bs){ bs=sc; best=n; }
  }
  return s._rep=best;
}
function boxArt(n){
  const c=n&&CARDS[n]; if(!c) return '';
  return `<span class="sart">${thumb(n)}${c[C.ID]?`<img src="https://images.ygoprodeck.com/images/cards_cropped/${c[C.ID]}.jpg" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.remove()">`:''}</span>`;
}
'''
rep("function viewSets(){", js+"function viewSets(){")

rep("""<span>${esc(s.n)}</span><small>${fmt==='tcg'?esc((s.d>TODAY?'próximo · ':'')+(s.d||'').slice(0,7)):esc((SET_ES[s.t]||s.t||'')+(s.rel?' · '+s.rel.slice(0,7):''))}</small></button>""",
    """${boxArt(boxRep(s,fmt))}<span class="stxt"><b>${esc(s.n)}</b><span class="schips"><i>${fmt==='tcg'?esc((s.d>TODAY?'próximo · ':'')+(s.d||'').slice(0,7)||'sin fecha'):esc((SET_ES[s.t]||s.t||'')+(s.rel?' · '+s.rel.slice(0,7):''))}</i><i>${s.k.length} cartas</i></span></span></button>""")

rep("""right=`<div class="detail"><h3>${esc(sel.n)}</h3>
      <p class="eff">${fmt==='tcg'?`${esc(sel.d||'sin fecha')} · ${sel.k.length} cartas de nuestra base`:`${esc(SET_ES[sel.t]||sel.t||'')}${sel.rel?' · '+esc(sel.rel):''} · ${sel.k.length} cartas`}</p>""",
    """const rn=boxRep(sel,fmt);
    const tops=fmt==='tcg'?sel.k.reduce((a,r)=>r[3]>(a?a[3]:0)?r:a,null):null;
    const rs=(l,v)=>`<div class="rstat"><small>${l}</small><b>${v}</b></div>`;
    const hero=`<div class="sethero">${boxArt(rn)}<div class="shtxt"><small>${fmt==='tcg'?'Expansión del TCG':esc(KIND_ES[sel.kind]||'')}</small><h3>${esc(sel.n)}</h3></div></div>
      <div class="rstats">${fmt==='tcg'?rs('Salida',esc(sel.d||'sin fecha'))+(sel.code?rs('Código',esc(sel.code)):'')+rs('Cartas',sel.k.length)+(tops?rs('La más cara',`$${tops[3]}<em>${esc(NAMES[tops[0]])}</em>`):''):rs('Tipo',esc(SET_ES[sel.t]||sel.t||KIND_ES[sel.kind]))+(sel.rel?rs('Salida',esc(sel.rel)):'')+rs('Cartas',sel.k.length)}</div>`;
    right=`<div class="detail">${hero}""")

css='''
/* cajas y sets */
.setlist{gap:var(--s2);padding-right:4px}
.setb{position:relative;isolation:isolate;overflow:hidden;min-height:76px;padding:var(--s3) var(--s4);justify-content:flex-start;border-radius:var(--r2);background:linear-gradient(100deg,color-mix(in srgb,var(--accent) 9%,var(--surface)),var(--surface) 50%)}
.setb .stxt{display:grid;gap:6px;min-width:0;max-width:62%}
.setb .stxt b{font:700 .95rem var(--f-display);letter-spacing:-.01em;line-height:1.2;overflow-wrap:anywhere}
.schips{display:flex;flex-wrap:wrap;gap:5px}
.schips i{font-style:normal;font:500 .66rem var(--f-data);padding:2px 8px;border-radius:99px;border:1px solid var(--line2);color:var(--muted);background:color-mix(in srgb,var(--surface) 70%,transparent)}
.sart{position:absolute;right:0;top:0;bottom:0;width:58%;z-index:-1;pointer-events:none;-webkit-mask-image:linear-gradient(90deg,transparent,#000 55%);mask-image:linear-gradient(90deg,transparent,#000 55%)}
.sart img,.sart .th{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:50% 25%;filter:saturate(1.2) contrast(1.05);transition:transform .7s cubic-bezier(.2,.7,.2,1)}
.sart .th{background-size:cover!important;background-position:center!important;border:0!important;border-radius:0!important;aspect-ratio:auto}
.setb:hover .sart img{transform:scale(1.08)}
.setb::after{content:"";position:absolute;right:0;bottom:0;width:46%;height:100%;z-index:-1;background:radial-gradient(circle at 100% 100%,color-mix(in srgb,var(--accent) 30%,transparent),transparent 62%);pointer-events:none}
.sethero{position:relative;isolation:isolate;overflow:hidden;min-height:170px;border-radius:var(--r);display:flex;align-items:flex-end;padding:var(--s5);background:linear-gradient(120deg,color-mix(in srgb,var(--accent) 14%,var(--surface2)),var(--surface2));border:1px solid var(--line2)}
.sethero .sart{width:70%;-webkit-mask-image:linear-gradient(90deg,transparent,#000 50%),linear-gradient(0deg,transparent,#000 40%);mask-image:linear-gradient(90deg,transparent,#000 50%);}
.sethero::after{content:"";position:absolute;inset:0;z-index:-1;background:radial-gradient(circle at 100% 100%,color-mix(in srgb,var(--accent) 38%,transparent),transparent 60%)}
.sethero .shtxt{max-width:60%;display:grid;gap:4px}
.sethero small{font:500 .68rem var(--f-data);letter-spacing:.14em;text-transform:uppercase;color:var(--accent)}
.sethero h3{margin:0;font:800 1.5rem var(--f-display);letter-spacing:-.02em;line-height:1.15;overflow-wrap:anywhere}
.rstat em{display:block;font:500 .7rem var(--f-data);font-style:normal;color:var(--muted);margin:0;overflow-wrap:anywhere}
@media(max-width:760px){.setb .stxt{max-width:70%}.sethero .shtxt{max-width:75%}.sethero h3{font-size:1.2rem}}
</style>'''
i=s.rindex('</style>'); s=s[:i]+css.lstrip('\n')+s[i+8:]
open('src.html','w',encoding='utf-8').write(s)
