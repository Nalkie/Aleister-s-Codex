"""Guía: tab de invocaciones, mazos con plan/jugada/puntos débiles/fuentes, Rush Duel, cartas con su estado de banlist."""
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("\nconst GD={tab:'basics',fmt:'tcg'};", "\n/*__GUIDEX__*/\nconst GD={tab:'basics',fmt:'tcg'};")
rep("const GTABS=[['basics','Cómo se juega'],['types','Tipos de mazo'],", "const GTABS=[['basics','Cómo se juega'],['summons','Invocaciones'],['types','Tipos de mazo'],")

a = s.index("function guideCards(arr){")
b = s.index("function viewGuide(){")
s = s[:a] + r'''function banNote(n){               // estado de banlist de una carta en los tres formatos
  const c=CARDS[canon(n)]; if(!c) return '';
  const b=c[C.BAN], d=c[C.DL], g=c[C.GEN], t=[];
  if(b===0) t.push(['TCG: prohibida',1]); else if(b===1) t.push(['TCG: limitada',0]); else if(b===2) t.push(['TCG: semi-limitada',0]);
  if(d===0) t.push(['Duel Links: prohibida',1]); else if(d>=1&&d<=3) t.push([`Duel Links: límite ${d}`,0]);
  if(g>0) t.push([g+' pts Genesys',0]);
  return t.length?`<span class="gbans">${t.map(([x,h])=>`<i class="${h?'bad':''}">${x}</i>`).join('')}</span>`:'';
}
function guideCards(arr){
  return `<div class="cgrid">${arr.filter(c=>CARDS[canon(c)]).map(c=>`<button class="cc" data-card="${esc(canon(c))}">${thumb(canon(c))}<span class="n">${esc(canon(c))}${banNote(c)}</span></button>`).join('')}</div>`;
}
const gsec=(t,p)=>p?`<h4 class="gh">${t}</h4><p class="gp">${esc(p)}</p>`:'';
const gdecks=f=>f==='rush'?DL_RUSH:FORMATS[f].decks;
const GFMT={tcg:'TCG',gen:'Genesys',dl:'Duel Links · Speed Duel',rush:'Duel Links · Rush Duel'};
function guideDeck(d,i,f){
  const {e,parts}=guideEntry(d.n), art=artOf(d.art);
  const keys=(e.keys&&e.keys.length?e.keys:d.cards.slice(0,6).map(c=>c[0]));
  const dots=e.d?`<span class="dots" title="${DIFF[e.d]}">${[1,2,3].map(x=>`<i class="${x<=e.d?'on':''}"></i>`).join('')}</span>`:'';
  const src=e.src&&e.src.length?`<p class="gsrc">Fuentes: ${e.src.map(([t,u])=>`<a href="${esc(u)}" target="_blank" rel="noopener noreferrer">${esc(t)}</a>`).join(' · ')}</p>`:'';
  return `<details class="deck gdeck" data-id="${esc(d.id||d.n)}"><summary>${art?`<img class="art-bg" src="${art}" alt="" loading="lazy" style="object-position:50% ${artPos(d.art)}">`:'<div class="artph"></div>'}
    <span class="rank">${i}</span><span class="dname">${esc(d.n)}</span><span class="bar gchips">${e.k?`<i class="gk">${esc(e.k)}</i>`:''}${e.d?`<i>${DIFF[e.d]}</i>`:''}${dots}</span></summary>
    <div class="body"><p class="geff">${esc(e.e)}</p>
      ${parts.length?`<div class="gparts">${parts.map(k=>`<div><b>${esc(k)}</b><span>${esc(GUIDE.decks[k].e)}</span></div>`).join('')}</div>`:''}
      ${gsec('Cómo funciona',e.plan)}${gsec('Jugada típica y notas',e.combo)}${gsec('Puntos débiles',e.weak)}
      <h4 class="gh">${e.keys&&e.keys.length?'Cartas clave':'Cartas que más usa'} · las marcas rojas son cartas prohibidas</h4>${guideCards(keys)}
      ${src}
      <p><button class="abtn" data-gomode="${f==='rush'?'dl':f}"${f==='rush'?' data-gofmt="rush"':f==='dl'?' data-gofmt="speed"':''}>Ver receta ${f==='rush'?'':'y tier '}en ${GFMT[f]}</button></p></div></details>`;
}
''' + s[b:]

# viewGuide: summons tab, rush format, richer cards tab
rep("""  if(GD.tab==='basics') body=`<div class="gsteps">""", """  if(GD.tab==='summons') body=`<p class="lede">Cómo funciona cada forma de invocar, con sus variantes y ejemplos de mazos que las usan. Las invocaciones del Extra Deck (Fusión, Sincro, Xyz, Péndulo y Link) son todas Invocaciones Especiales.</p><div class="gsum">${GUIDE.summons.map(g=>`<section class="gsm"><h3>${esc(g.n)}</h3><p class="gintro">${esc(g.intro)}</p>${g.items.map(([t,p])=>`<div class="gitem"><b>${esc(t)}</b><p>${esc(p)}</p></div>`).join('')}</section>`).join('')}</div>`;
  else if(GD.tab==='basics') body=`<div class="gsteps">""")
rep("""    const f=GD.fmt, ds=FORMATS[f].decks.filter(d=>d.cards&&d.cards.length);
    let k=0, out='';
    for(const t of ['T1','T2','T3','R','N']){ const g=ds.filter(d=>d.tier===t); if(!g.length) continue;""",
"""    const f=GD.fmt, ds=gdecks(f).filter(d=>d.cards&&d.cards.length);
    let k=0, out='';
    if(f==='rush') out=`<div class="tier t-n"><div class="tierhead"><span class="crest">R</span><span class="ttxt"><b>Ranking por uso</b><small>Rush no tiene tiers</small></span><span class="tcount">${ds.length} mazos</span></div>${ds.map(d=>guideDeck(d,++k,f)).join('')}</div>`;
    else for(const t of ['T1','T2','T3','R','N']){ const g=ds.filter(d=>d.tier===t); if(!g.length) continue;""")
rep("""${Object.keys(FORMATS).map(x=>`<button data-gfmt="${x}" aria-pressed="${f===x}">${FORMATS[x].label}</button>`).join('')}</div>
      <p class="lede">Una explicación corta de cada mazo del meta. La dificultad es una guía, no una regla.</p>${out}`;""",
"""${['tcg','gen','dl','rush'].map(x=>`<button data-gfmt="${x}" aria-pressed="${f===x}">${GFMT[x]}</button>`).join('')}</div>
      <p class="lede">Cómo funciona cada mazo del meta: el plan, una jugada típica, sus puntos débiles y las guías de jugadores en las que se basa. La dificultad es una guía, no una regla. Donde las fuentes eran escasas, el texto lo dice.</p>${out}`;""")
rep("""${items.map(c=>`<button class="gcard" data-card="${esc(canon(c.n))}">${cardImg(canon(c.n))}<span><b>${esc(canon(c.n))}</b><small>${esc(c.s)}</small></span></button>`).join('')}""",
    """${items.map(c=>`<button class="gcard" data-card="${esc(canon(c.n))}">${cardImg(canon(c.n))}<span><b>${esc(canon(c.n))}</b>${banNote(c.n)}<small>${esc(c.s)}</small></span></button>`).join('')}""")
rep("""    const roles=[...new Set(GUIDE.cards.map(c=>c.r))];
    body=roles.map(""", """    const roles=[...new Set(GUIDE.cards.map(c=>c.r))];
    body=`<p class="lede">Las cartas que más vas a ver, con su estado en cada formato. Las que figuran como prohibidas no se pueden jugar en ese formato: se muestran igual porque hay que conocerlas.</p>`+roles.map(""")

# go-to-mode with a format
rep("  else if(d.gomode){ mode=d.gomode; render(); window.scrollTo(0,0); }", "  else if(d.gomode){ mode=d.gomode; if(d.gofmt) dlFormat=d.gofmt; render(); window.scrollTo(0,0); }")

# css
rep("</style>\n\n<div class=\"wrap\">", """.gbans{display:flex;flex-wrap:wrap;gap:4px;margin:3px 0}
.gbans i{font-style:normal;font:500 .62rem var(--f-data);padding:1px 7px;border-radius:99px;border:1px solid var(--line2);color:var(--muted)}
.gbans i.bad{color:var(--red);border-color:color-mix(in srgb,var(--red) 60%,transparent);background:color-mix(in srgb,var(--red) 10%,transparent)}
.gp{margin:0 0 var(--s2);color:var(--fg);font-size:.94rem;line-height:1.6;max-width:80ch}
.gsrc{margin:var(--s3) 0 0;font-size:.82rem;color:var(--muted)}
.gsum{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:var(--s3)}
.gsm{margin:0;padding:var(--s5);border-radius:var(--r);border:1px solid var(--line2);background:linear-gradient(150deg,color-mix(in srgb,var(--accent) 9%,var(--surface)),var(--surface));display:grid;gap:var(--s3);align-content:start}
.gsm h3{font-size:1.15rem;color:var(--accent)}
.gintro{margin:0;color:var(--muted);font-size:.92rem}
.gitem{padding-top:var(--s2);border-top:1px solid var(--line)}
.gitem b{font:700 .9rem var(--f-display)}
.gitem p{margin:2px 0 0;color:var(--muted);font-size:.9rem;line-height:1.55}
</style>

<div class="wrap">""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch16b ok')
