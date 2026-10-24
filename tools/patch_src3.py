"""Patch src.html: TCG/Genesys/Duel Links decks come from the pipeline (YuGiOh Meta and Duel Links Meta APIs),
tiers are computed or taken from the API, 'outside the meta' winners section, DL availability wording.
Run once from build/ (backs src.html up first)."""
import re, shutil

shutil.copy('src.html', 'src.before_patch3.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, cnt)


def cut(start_marker, end_marker, new):
    global s
    i = s.index(start_marker)
    j = s.index(end_marker, i)
    s = s[:i] + new + s[j:]


# ---------- data: TCG + Genesys ----------
cut("/* ---------- DATOS TCG ---------- */", "const TCG_ENGINES = [", r'''/* ---------- DATOS TCG Y GENESYS (API de YuGiOh Meta) ---------- */
const YGM = /*__YGMDATA__*/{};   // arquetipos, uso, resultados y recetas reales
const BUILT = /*__BUILT__*/'';
const TIERS = {T1:['t-1','Tier 1','el más fuerte'],T2:['t-2','Tier 2','top cut frecuente'],T3:['t-3','Tier 3','juega y a veces llega'],R:['t-r','Poco resultado','por debajo del tier 3'],N:['t-n','Sin tier','Duel Links Meta no lo clasifica']};
const slug = x => x.toLowerCase().replace(/[^a-z0-9]+/g,'-');
function resText(d){
  const bits=[]; if(d.wins) bits.push(`${d.wins} ${d.wins===1?'victoria':'victorias'}`); if(d.top4) bits.push(`${d.top4} top 4`);
  const l=d.last;
  return `${bits.join(' · ')||'Sin top 4 todavía'} en ${d.c} decks de la muestra.${l?` Último resultado: ${l.place||'puesto'} en ${l.event} (${l.date}).`:''}`;
}
function ymDecks(fmt){
  const D=YGM[fmt];
  return Object.entries(D.decks).map(([name,d])=>{
    const w=d.who;
    const list={kind:fmt==='gen'?'gen':'tcg',price:w.price,
      who:`${w.author} · ${w.event}${w.place?', '+w.place:''} (${w.date}). Es la lista real reciente más parecida al promedio de ${d.sample} decks del arquetipo.`,
      main:d.recipe.main.map(([n,k,p])=>[canon(n),k,p]),extra:d.recipe.extra.map(([n,k,p])=>[canon(n),k,p]),side:d.recipe.side.map(([n,k,p])=>[canon(n),k,p])};
    const o={id:fmt+'-'+slug(name),n:name,tier:d.out?'R':(d.tier||'R'),out:d.out,c:d.n,lists:d.sample,share:d.share,total:D.total,pts:d.pts,wins:d.wins,top4:d.top4,last:d.last,art:d.art,
      cards:d.cards.map(([n,p])=>[canon(n),p]),list};
    o.res=resText(o); return o;
  }).sort((a,b)=>b.c-a.c);
}
const TCG_DECKS = ymDecks('tcg');
const GEN_DECKS = ymDecks('gen');
''')
# remove the old hand-made Genesys block
cut("/* ---------- DATOS GENESYS ---------- */", "/* ---------- DATOS DUEL LINKS", "")

# ---------- data: Duel Links ----------
cut("const DL_META = {", "const DL_FMT = ", "")
cut("function dlDecks(fmt){", "const DL_ENGINES = [", r'''function dlDecks(fmt){
  const D=DLD[fmt];
  return Object.entries(D.decks).map(([type,d])=>{
    const seen=new Map();
    for(const sec of ['main','extra','side']) for(const [nm,k,pr] of d.recipe[sec]) if(!seen.has(canon(nm))) seen.set(canon(nm),pr);
    const w=d.who;
    const list={kind:'dl',who:`${w.author||'Anónimo'} · ${w.event||'torneo comunitario'}${w.place?', '+w.place:''} · ${w.date}. La lista real reciente más parecida al promedio de ${d.n} decks.`,
      main:d.recipe.main.map(([n,k,pr])=>[canon(n),k,pr]),extra:d.recipe.extra.map(([n,k,pr])=>[canon(n),k,pr]),side:d.recipe.side.map(([n,k,pr])=>[canon(n),k,pr]),
      gems:w.gems,usd:w.usd,skill:w.skill,url:w.url,gemsMed:d.gemsMed,usdMed:d.usdMed,n:d.n};
    const o={id:'dl-'+fmt+'-'+slug(type),type,n:type.replace(/ ?: Rush!/,' (Rush)'),tier:d.out?'N':(d.tier?'T'+d.tier:'N'),out:d.out,lists:d.n,c:d.n,share:d.share,total:D.total,pts:d.pts,wins:d.wins,top4:d.top4,last:d.last,
      art:d.art||null,skill:d.skill,skillPct:d.skillPct,gemsMed:d.gemsMed,usdMed:d.usdMed,cards:[...seen].map(([nm,pr])=>[nm,pr]),list};
    o.res=resText(o); return o;
  }).sort((a,b)=>b.lists-a.lists);
}
const DL_SPEED = dlDecks('speed');
const DL_RUSH = dlDecks('rush');
''')

# ---------- views ----------
cut("/* ---------- VISTAS ---------- */", "/* ---------- BANLIST POR FORMATO", r'''/* ---------- VISTAS ---------- */
const DAYS = {tcg:42,gen:42};
function outsideSection(decks,kind,title,lede){
  const out=decks.filter(d=>d.out).sort((a,b)=>b.wins-a.wins||b.top4-a.top4||b.c-a.c);
  if(!out.length) return '';
  const max=Math.max(...out.map(d=>d.share));
  return `<section><h2>${title}</h2><p class="lede">${lede}</p>
    <div class="t-n"><div class="tierbar">Ganaron sin ser meta <small>${out.length} arquetipos</small></div>
    ${out.map((d,i)=>deckRow(d,i+1,`${d.wins} ${d.wins===1?'victoria':'victorias'}`,Math.min(100,d.wins*25),`${d.c} decks en la muestra (${fmt(d.share)}) · ${d.top4} top 4`,
      `${kind==='dl'?decklist(d.list,'dl'):decklist(d.list,kind)}<p>${esc(d.res)}</p>`)).join('')}</div></section>`;
}
function tierLede(){ return 'Tier calculado con el peso de resultados de los últimos 42 días de datos (1.º puesto = 8, 2.º = 5, top 4 = 3, top 8 = 2, top 16 = 1): T1 con 8% o más del total, T2 con 4% o más, T3 con 2% o más.'; }
function viewTCG(){
  const all=TCG_DECKS, decks=all.filter(d=>!d.out);
  const max=Math.max(...decks.map(d=>d.share));
  const D=YGM.tcg, withCards=decks.filter(d=>d.cards.length&&d.lists);
  const listsTotal=withCards.reduce((a,d)=>a+d.lists,0);
  return `
  <section style="margin-top:32px"><h2>Mejores mazos</h2>
  <p class="lede">Muestra: ${D.total} decks de torneos TCG entre el ${YGM.window[0]} y el ${YGM.window[1]} (WCQ Regionals, YCS, WCS y torneos comunitarios; sin OCG ni Genesys). ${tierLede()} El % de la barra es la parte de los decks. Abrí un mazo para ver su receta real y sus cartas clave.</p>
  <div class="note">El último torneo cargado en YuGiOh Meta es del ${YGM.asof}: la banlist del 18 oct todavía no aparece en estos resultados. Los arquetipos híbridos (por ejemplo Dark Magician Chaos Ritual) se cuentan aparte, como los publica la fuente.</div>
  ${grouped(decks,(d,i)=>deckRow(d,i,fmt(d.share),d.share/max*100,`${d.c} de ${d.total} decks · ${d.wins} victorias · ${d.top4} top 4 · ${fmt(d.pts)} del peso de resultados`,
     `${decklist(d.list,'tcg')}<p>${esc(d.res)}</p>${d.cards.length?`<div><h3>Cartas con más presencia (% de los decks del arquetipo)</h3>${cardChips(d.cards.slice(0,18))}</div>`:''}`))}
  </section>
  ${outsideSection(all,'tcg','Ganadores fuera del meta','Arquetipos que no llegan al tier 3 (menos de 2% del peso de resultados y menos de 2,5% de los decks) pero ganaron al menos un torneo en la muestra. Sirven para ver qué sorprende al meta.')}
  <section><h2>Cartas más usadas</h2><p class="lede">Calculado sobre los ${listsTotal} decks de los ${withCards.length} arquetipos del ranking, solo cartas presentes en 2 o más mazos. Tocá una carta para ver todas sus estrategias.</p>${topCards('tcg')}</section>
  <section><h2>Motores y arquetipos</h2><p class="lede">Combinaciones vistas en resultados recientes (TCG y OCG, que suele adelantar al TCG), analizadas a mano el 21 oct. La última columna dice dónde más funciona cada uno.</p>${enginesTable(TCG_ENGINES)}</section>`;
}
function viewGEN(){
  const all=GEN_DECKS, decks=all.filter(d=>!d.out);
  const max=Math.max(...decks.map(d=>d.share));
  const D=YGM.gen;
  return `
  <section style="margin-top:32px"><h2>Mejores mazos en Genesys</h2>
  <p class="lede">Genesys es el formato por puntos: cada carta tiene un costo y la lista suma un tope de 100. Muestra: ${D.total} decks de torneos Genesys entre el ${YGM.window[0]} y el ${YGM.window[1]}. ${tierLede()} Cada receta marca los puntos de sus cartas.</p>
  <div class="note">Los puntos son los de la lista de julio más el ajuste de aniversario del 5 oct. Una receta puede sumar más de 100 si el torneo usó los puntos anteriores al ajuste.</div>
  ${grouped(decks,(d,i)=>deckRow(d,i,fmt(d.share),d.share/max*100,`${d.c} de ${d.total} decks · ${d.wins} victorias · ${d.top4} top 4`,
     `${decklist(d.list,'gen')}<p>${esc(d.res)}</p>`))}
  </section>
  ${outsideSection(all,'gen','Ganadores fuera del meta','Arquetipos de Genesys sin tier que ganaron al menos un torneo en la muestra.')}`;
}
let dlFormat='speed';
function viewDL(){
  const all = dlFormat==='speed'?DL_SPEED:DL_RUSH;
  const list = all.filter(d=>!d.out);
  const D=DLD[dlFormat];
  const max=Math.max(...list.map(d=>d.share));
  const render=(d,i)=>deckRow(d,i,fmt(d.share),d.share/max*100,
    `${d.lists} de ${d.total} decks recientes · ${d.wins} victorias · ${d.top4} top 4`,
    `${decklist(d.list,'dl')}<p>${esc(d.res)}</p>`);
  const sorted=[...list].sort((a,b)=>b.share-a.share);
  const body = dlFormat==='speed'
    ? grouped(sorted,render)
    : `<div class="t-n"><div class="tierbar">Ranking por uso <small>Rush no tiene tiers</small></div>${sorted.map((d,i)=>render(d,i+1)).join('')}</div>`;
  const costRows=sorted.map(d=>`<tr><td><strong>${esc(d.n)}</strong></td><td class="big">${d.gemsMed!=null?fmtNum(d.gemsMed):'s/d'}</td><td class="big">${d.usdMed?'US$ '+d.usdMed:'0'}</td><td>${d.lists}</td><td>${esc(d.skill||'')} (${d.skillPct}%)</td></tr>`);
  return `
  <div class="seg" role="group" aria-label="Formato de Duel Links">
    <button id="f-speed" aria-pressed="${dlFormat==='speed'}" data-f="speed">Speed Duel</button>
    <button id="f-rush" aria-pressed="${dlFormat==='rush'}" data-f="rush">Rush Duel</button>
  </div>
  <section style="margin-top:20px"><h2>Mejores mazos · ${DL_FMT[dlFormat]}</h2>
  <p class="lede">${dlFormat==='speed'?'Los tiers son los que publica Duel Links Meta para cada arquetipo.':'Duel Links Meta no asigna tiers en Rush.'} El % es la parte de los ${D.total} decks publicados en Duel Links Meta entre el ${DLD.window[0]} y el ${DLD.window[1]}. Abrí un mazo para ver su receta con copias, rareza y cómo conseguir cada carta.</p>
  <div class="note">La receta es el deck real reciente más parecido al promedio del arquetipo. El % de cada carta es en cuántos decks del arquetipo aparece. Solo se listan arquetipos con al menos ${dlFormat==='speed'?8:3} decks o con una victoria. ${dlFormat==='rush'?'Las cartas de Rush Duel no están en la base de imágenes.':''}</div>
  ${body}</section>
  ${outsideSection(all,'dl','Ganadores fuera del meta',dlFormat==='speed'?'Arquetipos sin tier y con menos de 2% de la muestra que ganaron al menos un torneo.':'Arquetipos con menos de 3% de la muestra que ganaron al menos un torneo.')}
  <section><h2>Cuánto cuesta armarlo</h2><p class="lede">Mediana de gemas y de dinero real que Duel Links Meta estima para armar cada arquetipo (cuenta cartas que solo salen de estructuras y cajas de pago).</p>
  ${tbl(['Mazo','Gemas (mediana)','Dinero real (mediana)','Decks','Skill más usada'],costRows)}</section>
  ${dlFormat==='speed'?`
  <section><h2>Cartas más usadas</h2><p class="lede">Porcentaje de los ${D.total} decks recientes donde aparece cada carta, calculado con las recetas de cada arquetipo.</p>${topCards('dl')}</section>
  <section><h2>Motores y arquetipos</h2><p class="lede">Cruces que se ven en las recetas.</p>${enginesTable(DL_ENGINES)}</section>`:''}`;
}

''')

# decklist price for YuGiOh Meta recipes
rep("    cost=`<p class=\"cost\"><strong>Valor aproximado:</strong> US$ ${t.toFixed(0)} en TCGplayer${miss?` (sin precio para ${miss} cartas)`:''}. Precio por carta a la derecha; las marcas en rojo son cartas de la banlist del TCG.</p>`;",
    "    if(l.price) t=l.price;\n    cost=`<p class=\"cost\"><strong>Valor aproximado:</strong> US$ ${t.toFixed(0)}${l.price?' (precios de YuGiOh Meta)':' en TCGplayer'}${miss&&!l.price?` (sin precio para ${miss} cartas)`:''}. Precio por carta a la derecha; las marcas en rojo son cartas de la banlist del TCG.</p>`;")

# header: dynamic data dates
rep('<div class="asof">Datos del 21 oct 2026 · Lista de baneos de oct 2026 ya en juego</div>', '<div class="asof" id="asof"></div>')
rep("const h=location.hash.slice(1); if(MODES[h]) mode=h;",
    "$('#asof').textContent=`TCG y Genesys: datos hasta el ${YGM.asof} · Duel Links: hasta el ${DLD.asof} · página generada el ${BUILT}`;\nconst h=location.hash.slice(1); if(MODES[h]) mode=h;")

# DL availability wording
rep("  const dl = d<0 ? '<b>No existe en Duel Links</b>'", "  const dl = (d<0||d===5) ? `<b>Aún no disponible</b><span class=\"hint\">${(c[C.FL]&1)?'La carta existe en el TCG pero todavía no salió en Duel Links.':'No está en Duel Links.'}</span>`")
rep("  const dl=d<0?'–':d<=3?banIcon(d,dlTip(d)):'libre';", "  const dl=(d<0||d===5)?'–':d<=3?banIcon(d,dlTip(d)):'libre';")
rep("<div class=\"lim ${d>=0&&d<=3?'hot':''}\"><small>Duel Links</small>${dl}</div>", "<div class=\"lim ${d>=0&&d<=3?'hot':''}\"><small>Duel Links</small>${dl}</div>")

# footer
rep("<li>TCG: <a href=\"https://www.yugiohmeta.com/top-decks\">YuGiOhMeta</a> (584 listas TCG del último mes), <a href=\"https://kotacards.com/\">KotaCards</a> (tiers del 2 oct, cartas y listas por mazo), <a href=\"https://roadoftheking.com/ocg-2026-10-metagame-report-1/\">Road of the King</a> (OCG, 190 mazos del 1 al 7 oct).</li>",
    "<li>TCG y Genesys: API pública de <a href=\"https://www.yugiohmeta.com/top-decks\">YuGiOh Meta</a> (decks de torneos con puesto, copias y precios). Los tiers se calculan con los resultados de los últimos 42 días de datos. La tabla de motores se armó a mano con <a href=\"https://roadoftheking.com/ocg-2026-10-metagame-report-1/\">Road of the King</a> (OCG) y KotaCards.</li>")
m = re.search(r"<li>Genesys: top cuts de .*?</li>", s)
assert m
s = s.replace(m.group(0), "<li>Genesys: decks de torneos Genesys de la misma API de YuGiOh Meta. Puntos: ver la nota de puntos Genesys más abajo.</li>", 1)
open('src.html', 'w', encoding='utf-8').write(s)
print('patched', len(s))
