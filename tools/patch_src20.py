"""Ronda 5: personajes con secciones separadas (Cartas / Habilidades) y habilidades legibles, paneles con secciones plegables, íconos de tickets
reemplazables por fotos (art/tickets/<nombre>.png) y distintivo Rush. Backup: src.before_patch20.html."""
import shutil
shutil.copy('src.html', 'src.before_patch20.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- tickets: optional real photo on top of the drawn icon, Rush badge ----------
rep("""function boxMedia(s,fmt,rep){
  const u=boxUrl(s,fmt);
  if(fmt==='dl'&&s.kind==='other') return `<span class="spack tk">${ticketIcon(s.n)}</span>`;""",
    """const TKSLUG=[[/UR Tickets/,'ur'],[/SR Tickets/,'sr'],[/Acquirable with Tickets/,'normal'],[/Ranked/,'ranked'],[/Anniversary/,'anniversary'],[/Gift|Campaign/,'gift'],[/Card Trader/,'trader'],[/Mission|Bingo|Lifetime/,'mission'],[/Special Set/,'special'],[/Event|Tournament|Grand Prix|Scramble|Quest|Chronicles|Carnival|Circuit/,'event']];
const tkSlug=name=>(TKSLUG.find(x=>x[0].test(name))||[0,'generic'])[1];
function boxMedia(s,fmt,rep){
  const u=boxUrl(s,fmt);
  if(fmt==='dl'&&s.kind==='other') return `<span class="spack tk">${ticketIcon(s.n)}<img class="tkimg" src="art/tickets/${tkSlug(s.n)}${s.rush?'-rush':''}.png" alt="" onerror="if(!this.dataset.r){this.dataset.r=1;this.src='art/tickets/${tkSlug(s.n)}.png'}else this.remove()"></span>${s.rush?'<i class="rushb">Rush</i>':''}`;""")

# ---------- characters: sections ----------
a = s.index("function charInfo(name){")
b = s.index("function evDL(){")
s = s[:a] + r'''const CT={tab:'cards',q:''};      // pestaña de un personaje: Cartas o Habilidades
const isec=(t,h,open=true)=>h?`<details class="isec"${open?' open':''}><summary>${t}</summary><div>${h}</div></details>`:'';
const howOf=h=>{ const m=/^Level (\d+)$/.exec(h||''); return m?[+m[1],'Subiendo de nivel','Nivel '+m[1]]:({Drop:[100,'Farmeo en la Puerta (Gate)','Drop'],'Character Deck':[101,'Duelos de personaje','Character Deck'],'Starter Deck':[102,'Mazo inicial','Inicial']}[h]||[103,'Otras formas',h||'—']); };
function charTabs(name){
  const c=DLI&&DLI.chars[name], src=(SETS.data.dl||[]).find(x=>x.kind==='char'&&x.n===name);
  return `<div class="seg mini ctabs" role="group" aria-label="Sección del personaje"><button data-cttab="cards" aria-pressed="${CT.tab==='cards'}">Cartas${src?' · '+src.k.length:''}</button><button data-cttab="skills" aria-pressed="${CT.tab==='skills'}">Habilidades${c?' · '+c.s.length:''}</button></div>`;
}
function charSkills(name){        // habilidades que enseña el personaje: tarjetas separadas por forma de obtención
  if(!DLI){ loadEv(); return '<p class="rnote">Cargando habilidades…</p>'; }
  const c=DLI.chars[name]; if(!c||!c.s.length) return '<p class="dkempty">Este personaje no enseña habilidades en los datos de Duel Links Meta.</p>';
  const q=CT.q.trim(), list=c.s.filter(x=>!q||matchText(q,x[0]+' '+x[1]));
  const groups={}; for(const sk of list){ const h=howOf(sk[2]); (groups[h[0]]=groups[h[0]]||{t:h[1],rows:[]}).rows.push([sk,h]); }
  const keys=Object.keys(groups).map(Number).sort((a,b)=>(a<100&&b<100?a-b:a-b));
  const levels=keys.filter(k=>k<100);
  const out=[]; if(levels.length) out.push(['Subiendo de nivel',levels.flatMap(k=>groups[k].rows)]);
  for(const k of keys.filter(k=>k>=100)) out.push([groups[k].t,groups[k].rows]);
  return `<div class="filters"><label class="sr" for="ctq">Buscar habilidad</label><input id="ctq" type="search" placeholder="Buscar entre las ${c.s.length} habilidades de ${esc(name)}" value="${esc(CT.q)}" autocomplete="off" spellcheck="false"></div>
    ${out.map(([t,rows])=>`<h4 class="rgh">${esc(t)} · ${rows.length}</h4><div class="skgrid">${rows.map(([sk,h])=>`<article class="skl"><header><b>${esc(sk[0])}</b>${sk[3]?'<i class="chip">Rush</i>':''}</header><p>${esc(sk[1])}</p><footer><span class="how h${h[0]<100?'lv':h[0]}">${esc(h[2])}</span></footer></article>`).join('')}</div>`).join('')||'<p class="dkempty">Ninguna habilidad coincide con la búsqueda.</p>'}`;
}
''' + s[b:]

# sets view: heroTop / tabs / cards or skills
rep("    const info=fmt==='dl'&&sel.kind==='char'?charInfo(sel.n):'';\n    mid=`<div class=\"detail sbox\">${hero}${info}\n      <p class=\"lede\"",
    "    const isChar=fmt==='dl'&&sel.kind==='char', hi=hero.indexOf('<div class=\"filters\">'), heroTop=hero.slice(0,hi), filt=hero.slice(hi);\n    if(isChar&&!DLI) loadEv();\n    mid=`<div class=\"detail sbox\">${heroTop}${isChar?charTabs(sel.n):''}${isChar&&CT.tab==='skills'?charSkills(sel.n):`${filt}\n      <p class=\"lede\"")
rep("data-smore=\"1\">Mostrar más</button></p>`:''}</div>`;", "data-smore=\"1\">Mostrar más</button></p>`:''}`}</div>`;")

# Eventos > personajes
rep("</p></div></div>${rewards}${charInfo(sel)}</div>`;", "</p></div></div>${charTabs(sel)}${CT.tab==='skills'?charSkills(sel):rewards}</div>`;")
rep("  else if(d.sclose){ SETS.card=null; render(); }", "  else if(d.sclose){ SETS.card=null; render(); }\n  else if(d.cttab){ CT.tab=d.cttab; CT.q=''; render(); }")
rep("  else if(id==='evq'){ EV.q=e.target.value; render('evq'); }", "  else if(id==='evq'){ EV.q=e.target.value; render('evq'); }\n  else if(id==='ctq'){ CT.q=e.target.value; render('ctq'); }")
rep("else if(d.evchar){ EV.char=d.evchar; render(); }", "else if(d.evchar){ EV.char=d.evchar; CT.q=''; render(); }")

# ---------- inspector sections ----------
rep("""    ${here}
    <div class="fmt">Banlist por formato</div>${limitChips(n)}
    <div id="sx-tail"></div>""", """    ${isec(fmt==='tcg'?'Rarezas en esta expansión':'En esta caja',here)}
    ${isec('Banlist por formato',limitChips(n))}
    <div id="sx-tail"></div>""")
rep("  if(SETS.fmt==='dl'){ $('#sx-tail').innerHTML=dlBlock(n,d); return; }", "  if(SETS.fmt==='dl'){ $('#sx-tail').innerHTML=isec('Cómo conseguirla',dlBlock(n,d)); return; }")
rep("  $('#sx-tail').innerHTML=versionsBlock(n,d)+tcgBlock(n,d,true);", "  $('#sx-tail').innerHTML=isec('Versiones de la carta',versionsBlock(n,d))+isec('Todas las impresiones',tcgBlock(n,d,true),false);")
rep("  $('#dx-tail').innerHTML=dlBlock(n,d)+versionsBlock(n,d)+tcgBlock(n,d);", "  $('#dx-tail').innerHTML=isec('Duel Links · cómo conseguirla',dlBlock(n,d))+isec('Versiones de la carta',versionsBlock(n,d))+isec('TCG · expansiones, rarezas y precio',tcgBlock(n,d),false);")

# ---------- css ----------
rep("</style>\n\n<div class=\"sideart", """.ctabs{margin:var(--s3) 0 var(--s2)}
.ctabs button{font-size:.9rem;min-height:38px;padding:0 var(--s5)}
.skgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:var(--s3);margin:var(--s2) 0 var(--s4)}
.skl{display:grid;gap:var(--s2);align-content:start;padding:var(--s4);border-radius:var(--r2);border:1px solid var(--line2);background:linear-gradient(160deg,color-mix(in srgb,var(--accent) 8%,var(--surface)),var(--surface))}
.skl header{display:flex;justify-content:space-between;gap:var(--s2);align-items:flex-start}
.skl header b{font:700 .98rem var(--f-display);line-height:1.25;overflow-wrap:anywhere}
.skl p{margin:0;font-size:.92rem;line-height:1.6;color:var(--fg);opacity:.9}
.skl footer{display:flex;gap:6px;flex-wrap:wrap}
.how{font:600 .7rem var(--f-data);letter-spacing:.04em;padding:3px 10px;border-radius:99px;border:1px solid var(--line2);color:var(--muted)}
.how.hlv{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 55%,transparent);background:color-mix(in srgb,var(--accent) 10%,transparent)}
.how.h100{color:var(--t1);border-color:color-mix(in srgb,var(--t1) 55%,transparent);background:color-mix(in srgb,var(--t1) 10%,transparent)}
.how.h101{color:var(--accent2);border-color:color-mix(in srgb,var(--accent2) 55%,transparent)}
.isec{border:1px solid var(--line);border-radius:var(--r2);background:color-mix(in srgb,var(--surface) 70%,transparent);margin:var(--s2) 0}
.isec > summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;padding:var(--s2) var(--s4);font:600 .78rem var(--f-data);letter-spacing:.1em;text-transform:uppercase;color:var(--accent)}
.isec > summary::-webkit-details-marker{display:none}
.isec > summary::after{content:"+";font-size:1.1rem}
.isec[open] > summary::after{content:"−"}
.isec > div{padding:0 var(--s4) var(--s4);display:grid;gap:var(--s2)}
.isec > div > .fmt:first-child{display:none}
.spack.tk{position:absolute}
.spack.tk .tkimg{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;filter:drop-shadow(0 6px 8px rgba(0,0,0,.4))}
.rushb{position:absolute;right:12px;bottom:8px;z-index:1;font:700 .6rem var(--f-data);letter-spacing:.08em;padding:1px 8px;border-radius:99px;background:var(--accent);color:var(--bg)}
</style>

<div class=\"sideart""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch20 ok')
