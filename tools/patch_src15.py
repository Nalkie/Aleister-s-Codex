"""Guía: how to play, deck types, meta strategies explained, key cards and a glossary, for people new to the game."""
import shutil
shutil.copy('src.html', 'src.before_patch15.html')
s = open('src.html', encoding='utf-8').read()
data = open('tools/guide_data.js', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:70]
    s = s.replace(a, b)


js = data + r'''
const GD={tab:'basics',fmt:'tcg'};
const GTABS=[['basics','Cómo se juega'],['types','Tipos de mazo'],['decks','Estrategias del meta'],['cards','Cartas clave'],['gloss','Glosario']];
const DIFF=['','Fácil de aprender','Intermedio','Avanzado'];
const reEsc=x=>x.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
function guideEntry(name){
  if(GUIDE.decks[name]) return {e:GUIDE.decks[name],parts:[]};
  const parts=Object.keys(GUIDE.decks).filter(k=>new RegExp('(^|[^A-Za-z])'+reEsc(k)+'([^A-Za-z]|$)','i').test(name)).sort((a,b)=>b.length-a.length);
  const uniq=[]; for(const k of parts) if(!uniq.some(u=>u.includes(k))) uniq.push(k);
  if(uniq.length>=2) return {e:{k:'Híbrido',d:Math.max(...uniq.map(k=>GUIDE.decks[k].d)),e:GUIDE.hybrid,keys:[]},parts:uniq};
  if(uniq.length===1) return {e:Object.assign({},GUIDE.decks[uniq[0]],{e:'Variante de '+uniq[0]+'. '+GUIDE.decks[uniq[0]].e}),parts:[]};
  return {e:{k:'',d:0,e:GUIDE.fallback,keys:[]},parts:[]};
}
function guideCards(arr){
  return `<div class="cgrid">${arr.filter(c=>CARDS[canon(c)]).map(c=>`<button class="cc" data-card="${esc(canon(c))}">${thumb(canon(c))}<span class="n">${esc(canon(c))}</span></button>`).join('')}</div>`;
}
function guideDeck(d,i,f){
  const {e,parts}=guideEntry(d.n), art=artOf(d.art);
  const keys=(e.keys&&e.keys.length?e.keys:d.cards.slice(0,6).map(c=>c[0]));
  const dots=e.d?`<span class="dots" title="${DIFF[e.d]}">${[1,2,3].map(x=>`<i class="${x<=e.d?'on':''}"></i>`).join('')}</span>`:'';
  return `<details class="deck gdeck" data-id="${esc(d.id||d.n)}"><summary>${art?`<img class="art-bg" src="${art}" alt="" loading="lazy">`:'<div class="artph"></div>'}
    <span class="rank">${i}</span><span class="dname">${esc(d.n)}</span><span class="bar gchips">${e.k?`<i class="gk">${esc(e.k)}</i>`:''}${e.d?`<i>${DIFF[e.d]}</i>`:''}${dots}</span></summary>
    <div class="body"><p class="geff">${esc(e.e)}</p>
      ${parts.length?`<div class="gparts">${parts.map(k=>`<div><b>${esc(k)}</b><span>${esc(GUIDE.decks[k].e)}</span></div>`).join('')}</div>`:''}
      <h4 class="gh">${e.keys&&e.keys.length?'Cartas clave':'Cartas que más usa'}</h4>${guideCards(keys)}
      <p><button class="abtn" data-gomode="${f}">Ver receta y tier en ${FORMATS[f].label}</button></p></div></details>`;
}
function viewGuide(){
  const head=pageHead('Guía para empezar','Si recién llegás al juego: cómo se juega, qué tipos de mazo hay, qué hace cada estrategia del meta y las cartas que vas a ver en todos lados.');
  const tabs=`<div class="seg gtabs" role="group" aria-label="Secciones de la guía">${GTABS.map(([k,t])=>`<button data-gtab="${k}" aria-pressed="${GD.tab===k}">${t}</button>`).join('')}</div>`;
  let body='';
  if(GD.tab==='basics') body=`<div class="gsteps">${GUIDE.basics.map((b,i)=>`<div class="gstep"><span class="gnum">${i+1}</span><div><h3>${esc(b.t)}</h3><p>${esc(b.p)}</p></div></div>`).join('')}</div>`;
  else if(GD.tab==='types') body=`<div class="gtypes">${GUIDE.types.map(t=>`<div class="gtype"><h3>${esc(t.n)}</h3><p>${esc(t.e)}</p>${t.ex.length?`<div class="schips">${t.ex.map(x=>`<i>${esc(x)}</i>`).join('')}</div>`:''}</div>`).join('')}</div>`;
  else if(GD.tab==='decks'){
    const f=GD.fmt, ds=FORMATS[f].decks.filter(d=>d.cards&&d.cards.length);
    let k=0, out='';
    for(const t of ['T1','T2','T3','R','N']){ const g=ds.filter(d=>d.tier===t); if(!g.length) continue;
      out+=`<div class="tier ${TIERS[t][0]}"><div class="tierhead"><span class="crest">${ROMAN[t]}</span><span class="ttxt"><b>${TIERS[t][1]}</b><small>${TIERS[t][2]}</small></span><span class="tcount">${g.length} ${g.length===1?'mazo':'mazos'}</span></div>${g.map(d=>guideDeck(d,++k,f)).join('')}</div>`; }
    body=`<div class="seg" role="group" aria-label="Juego">${Object.keys(FORMATS).map(x=>`<button data-gfmt="${x}" aria-pressed="${f===x}">${FORMATS[x].label}</button>`).join('')}</div>
      <p class="lede">Una explicación corta de cada mazo del meta. La dificultad es una guía, no una regla.</p>${out}`;
  }
  else if(GD.tab==='cards'){
    const roles=[...new Set(GUIDE.cards.map(c=>c.r))];
    body=roles.map(r=>{ const items=GUIDE.cards.filter(c=>c.r===r&&CARDS[canon(c.n)]); return items.length?`<div class="bgrp"><h3>${esc(r)}</h3><div class="gcards">${items.map(c=>`<button class="gcard" data-card="${esc(canon(c.n))}">${cardImg(canon(c.n))}<span><b>${esc(canon(c.n))}</b><small>${esc(c.s)}</small></span></button>`).join('')}</div></div>`:''; }).join('');
  }
  else body=`<dl class="gloss">${GUIDE.glossary.map(([t,d])=>`<div><dt>${esc(t)}</dt><dd>${esc(d)}</dd></div>`).join('')}</dl>`;
  return head+tabs+`<div class="gbody">${body}</div></section>`;
}
'''
rep("const MODES = {tcg:['TCG',viewTCG],gen:['Genesys',viewGEN],dl:['Duel Links',viewDL],ex:['Cartas',viewEX],sets:['Cajas y sets',viewSets],deck:['Constructor',viewDeck],ban:['Banlist',viewBan]};",
    js + "const MODES = {tcg:['TCG',viewTCG],gen:['Genesys',viewGEN],dl:['Duel Links',viewDL],ex:['Cartas',viewEX],sets:['Cajas y sets',viewSets],deck:['Constructor',viewDeck],guide:['Guía',viewGuide],ban:['Banlist',viewBan]};")
rep("!['ex','sets','ban','deck'].includes(mode)", "!['ex','sets','ban','deck','guide'].includes(mode)")
rep('document.body.className=mode==="deck"?"dkmode":mode;', 'document.body.className=mode==="deck"?"dkmode":mode==="guide"?"gdmode":mode;')
rep('body.dkmode{--accent:var(--ac-tool)}', 'body.dkmode,body.gdmode{--accent:var(--ac-tool)}')
i = s.index('<button class="tool" role="tab" id="tab-ban"')
s = s[:i] + '<button class="tool" role="tab" id="tab-guide" data-mode="guide"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5 C4 4 5 3.5 6 3.5 H19 V18 H6 C5 18 4 18.5 4 19.5 Z"/><path d="M4 19.5 C4 20.5 5 21 6 21 H19 V18"/><path d="M9 8 H15 M9 12 H13"/></svg>Guía</button>\n    ' + s[i:]
rep("  else if(d.rv){", "  else if(d.gtab){ GD.tab=d.gtab; render(); }\n  else if(d.gfmt){ GD.fmt=d.gfmt; render(); }\n  else if(d.gomode){ mode=d.gomode; render(); window.scrollTo(0,0); }\n  else if(d.rv){")
css = '''
/* guía */
.gtabs{margin-top:var(--s4)}
.gbody{margin-top:var(--s5)}
.gsteps{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:var(--s3)}
.gstep{display:flex;gap:var(--s4);padding:var(--s4) var(--s5);border-radius:var(--r);border:1px solid var(--line2);background:linear-gradient(150deg,color-mix(in srgb,var(--accent) 11%,var(--surface)),var(--surface))}
.gnum{flex:none;width:38px;height:38px;border-radius:12px;display:grid;place-items:center;font:800 1rem var(--f-display);color:var(--bg);background:linear-gradient(140deg,color-mix(in srgb,var(--accent) 60%,#fff),var(--accent));box-shadow:0 8px 22px -8px var(--accent)}
.gstep h3,.gtype h3{margin:0 0 6px;font:700 1.05rem var(--f-display)}
.gstep p,.gtype p{margin:0;color:var(--muted);font-size:.92rem;line-height:1.55}
.gtypes{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:var(--s3)}
.gtype{padding:var(--s5);border-radius:var(--r);border:1px solid var(--line2);background:var(--surface);display:grid;gap:var(--s3);align-content:start}
.gchips{display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.gchips i{font-style:normal;font:500 .7rem var(--f-data);padding:2px 9px;border-radius:99px;border:1px solid var(--line2);color:var(--muted);background:color-mix(in srgb,var(--surface) 70%,transparent)}
.gchips i.gk{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 50%,transparent)}
.dots{display:inline-flex;gap:3px}
.dots i{width:8px;height:8px;padding:0;border-radius:50%;border:1px solid var(--line2);background:transparent}
.dots i.on{background:var(--accent);border-color:var(--accent)}
.gdeck .geff{margin:0 0 var(--s3);font-size:1rem;line-height:1.6}
.gh{margin:var(--s4) 0 var(--s2);font:600 .72rem var(--f-data);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.gparts{display:grid;gap:var(--s2);margin:var(--s3) 0}
.gparts div{padding:var(--s3) var(--s4);border-radius:var(--r2);border:1px solid var(--line2);background:var(--surface2);display:grid;gap:2px}
.gparts span{color:var(--muted);font-size:.88rem}
.gcards{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:var(--s3)}
.gcard{display:flex;gap:var(--s4);text-align:left;padding:var(--s3);border-radius:var(--r2);border:1px solid var(--line2);background:var(--surface);cursor:pointer;align-items:flex-start;transition:border-color .15s,transform .15s}
.gcard:hover{border-color:var(--accent);transform:translateY(-2px)}
.gcard .cf{flex:none;width:68px}
.gcard > span:last-child{display:grid;gap:4px}
.gcard small{color:var(--muted);font-size:.84rem;line-height:1.45}
.gloss{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:var(--s3);margin:0}
.gloss div{padding:var(--s4) var(--s5);border-radius:var(--r2);border:1px solid var(--line2);background:var(--surface)}
.gloss dt{font:700 1rem var(--f-display);margin-bottom:4px;color:var(--accent)}
.gloss dd{margin:0;color:var(--muted);font-size:.92rem;line-height:1.5}
</style>'''
i = s.rindex('</style>')
s = s[:i] + css.lstrip('\n') + s[i + 8:]
open('src.html', 'w', encoding='utf-8').write(s)
print('patched', len(s))
