"""One-off patch of src.html for: rename, recipes on deck open, DL data from the Duel Links Meta API,
TCG print/price info, DL acquisition info. Run from build/ once."""
import re

p = 'src.html'
s = open(p, encoding='utf-8').read()


def sub1(pattern, repl, flags=re.S, count=1):
    global s
    s, n = re.subn(pattern, lambda m: repl, s, count=count, flags=flags)
    assert n == 1, pattern[:60]


# ---- A. rename ----
sub1(r"<title>[^<]*</title>", "<title>Aleister's Codex</title>")
sub1(r'<div class="kicker">.*?</div>\n  <h1>.*?</h1>',
     '<div class="kicker"><span class="gem"></span>Reporte de meta · <span id="hmode">TCG</span></div>\n  <h1>Aleister\'s <em>Codex</em></h1>')

# ---- B. DL data section ----
DL_SECTION = r'''/* ---------- DATOS DUEL LINKS (API de Duel Links Meta) ---------- */
const DLD = /*__DLDATA__*/{};   // recetas, uso y obtención por carta
const DL_META = {
 'Memento':{n:'Memento',tier:'T1',power:35.5,ev:4,art:'Mementomictlan Tecuhtlica - Creation King',res:'Ganó 2 torneos (Starry Cup #192 y Quantum Dailies #569) y Starry Cup #202 del 20 oct.'},
 'Centur-Ion':{n:'Centur-Ion',tier:'T1',power:10.5,ev:3,art:'Centur-Ion Primera',res:'Ganó Pro Arab Tournament #19.'},
 'Branded':{n:'Branded',tier:'T2',power:21.5,ev:5,art:'Albion the Branded Dragon',res:'Ganó Duel Links UX Stadium #8. Subió de T2 a T1 el 5 oct y volvió a T2.'},
 'Vaalmonica':{n:'Vaalmonica',tier:'T2',power:15.0,ev:8,art:'Vaalmonica, the Agathokakological Voice',res:'El más presente en top 4 (8 de 13 torneos). Ganó Suisen Weekly #221.'},
 'Horus':{n:'Horus',tier:'T3',power:21.5,ev:2,art:'Horus the Black Flame Deity',res:'Segundo en poder, pero poca presencia en torneos recientes.'},
 'Snake-Eye':{n:'Snake-Eye',tier:'T3',power:17.0,ev:7,art:'Snake-Eye Ash',res:'Ganó 3 torneos (el que más), incluido Duel Links Grand Prix #156 (78 jugadores).'},
 'Shining Sarcophagus':{n:'Shining Sarcophagus',tier:'T3',power:8.5,ev:2,art:'Shining Sarcophagus',res:'Su lista es de Dark Magician con Shining Sarcophagus.'},
 'Dark Magician':{n:'Dark Magician',tier:'T3',power:6.5,ev:1,art:'Dark Magician',res:'Ganó Speed Duel Dynasty #63.'},
 'Stardust / Synchron':{n:'Stardust / Synchron',tier:'N',power:8.0,ev:2,art:'Stardust Dragon',res:''},
 'Mathmech':{n:'Mathmech',tier:'N',art:'Mathmech Circular',res:'Ganó Sky Striker Cup #101.'},
 'HEROs':{n:'HEROs',tier:'N',art:'Elemental HERO Neos',res:'Ganó Starry Cup #191.'},
 'Infernity':{n:'Infernity',tier:'N',art:'Infernity Launcher',res:''},
 'Cyber Dragon':{n:'Cyber Dragon',tier:'N',art:'Cyber Dragon',res:''},
 'Destiny HEROs':{n:'Destiny HEROs',tier:'N',art:'Destiny HERO - Malicious',res:'Ganó Meta Weekly #443.'},
 'Rokket':{n:'Rokket',tier:'N',art:'Rokket',res:'Ganó Starry Cup #190.'},
 'Swordsoul':{n:'Swordsoul',tier:'N',art:'Swordsoul of Mo Ye',res:''},
 'Marincess':{n:'Marincess',tier:'N',art:'Marincess Sea Horse',res:''},
 'Labrynth':{n:'Labrynth',tier:'N',art:'Lady Labrynth of the Silver Castle',res:''},
 'Blackwings':{n:'Blackwings',tier:'N',art:'Blackwing - Gale the Whirlwind',res:''},
 'Resonators':{n:'Resonators',tier:'N',art:'Red-Eyes Dark Dragoon',res:''},
 'Wyrms : Rush!':{n:'Wyrms',tier:'N',power:21.5,res:'Líder del ranking de poder Rush.'},
 'Ether Dragon':{n:'Ether Dragon',tier:'N',power:15.0,ev:4,res:'Ganó 3 de 4 torneos Rush. Usa soporte de Ultimate Flag y Star Protector\'s Protection.'},
 'Dark Magician: Rush!':{n:'Dark Magician (Rush)',tier:'N',power:7.0,ev:3,art:'Dark Magician',res:'Top 4 en 3 de 4 torneos.'},
 'Voidvelg':{n:'Voidvelg',tier:'N',power:6.0,res:''},
 'Meteor Dragon':{n:'Meteor Dragon',tier:'N',power:4.0,res:''}
};
const DL_FMT = {speed:'Speed Duel',rush:'Rush Duel'};
const fmtNum = n => n==null ? '' : n.toLocaleString('es-AR');
function dlDecks(fmt){
  const D=DLD[fmt];
  return Object.entries(D.decks).map(([type,d])=>{
    const m=DL_META[type]||{};
    const seen=new Map();
    for(const sec of ['main','extra','side']) for(const [nm,k,pr] of d.recipe[sec]) if(!seen.has(canon(nm))) seen.set(canon(nm),pr);
    const w=d.who;
    const list={kind:'dl',who:`${w.author||'Anónimo'} · ${w.event||'torneo comunitario'} · ${w.date}. La lista real reciente más parecida al promedio de ${d.n} decks.`,
      main:d.recipe.main.map(([n,k,pr])=>[canon(n),k,pr]),extra:d.recipe.extra.map(([n,k,pr])=>[canon(n),k,pr]),side:d.recipe.side.map(([n,k,pr])=>[canon(n),k,pr]),
      gems:w.gems,usd:w.usd,skill:w.skill,url:w.url,gemsMed:d.gemsMed,usdMed:d.usdMed,n:d.n};
    return {id:'dl-'+fmt+'-'+type.toLowerCase().replace(/[^a-z0-9]+/g,'-'),type,n:m.n||type,tier:m.tier||'N',lists:d.n,share:d.share,total:D.total,power:m.power,ev:m.ev,art:m.art||null,res:m.res||'',
      skill:d.skill,skillPct:d.skillPct,gemsMed:d.gemsMed,usdMed:d.usdMed,cards:[...seen].map(([nm,pr])=>[nm,pr]),list};
  }).sort((a,b)=>b.lists-a.lists);
}
const DL_SPEED = dlDecks('speed');
const DL_RUSH = dlDecks('rush');
const DL_EVENTS = {speed:13,rush:4};
const DL_ENGINES = [
 {id:'d-ed',n:'Extra Deck compartido',txt:'Las mismas cartas de Extra Deck (I:P Masquerena, S:P Little Knight, Knightmare Phoenix…) aparecen en las recetas de muchos mazos distintos.',
  cards:N(['I:P Masquerena','S:P Little Knight','Knightmare Phoenix','Underworld Goddess of the Closed World','Super Starslayer TY-PHON - Sky Crisis']),works:['Memento','Vaalmonica','Snake-Eye','Horus','Dark Magician','Shining Sarcophagus','Centur-Ion (TY-PHON)']},
 {id:'d-generic',n:'Interacción genérica',txt:'Cartas que casi todas las recetas incluyen.',
  cards:N(['Droll & Lock Bird','Mulcharmy Fuwalos','Nibiru, the Primal Being','Forbidden Droplet','Hey, Trunade!','Lava Golem']),works:['Memento','Centur-Ion','Branded','Vaalmonica','Snake-Eye','Horus','Dark Magician']},
 {id:'d-bystial',n:'Bystial',txt:'Bystial Druiswurm aparece en tres mazos; Saronir y Magnamhut en Branded.',
  cards:N(['Bystial Druiswurm','Bystial Saronir','Bystial Magnamhut']),works:['Branded','Vaalmonica (Druiswurm)','Horus (Druiswurm)']},
 {id:'d-branded',n:'Paquete Branded',txt:'Solo Branded lo lista entre los mazos revisados.',
  cards:N(['Branded Fusion','Branded Opening','Albion the Branded Dragon','Super Polymerization']),works:['Branded']},
 {id:'d-dm',n:'Paquete Dark Magician',txt:'Las recetas de Dark Magician y de Shining Sarcophagus comparten núcleo.',
  cards:N(['Dark Magician','Dark Magician Girl','Dark Magical Curtain','The Gaze of Timaeus','Shining Sarcophagus','Red-Eyes Dark Dragoon','Dark Magician of Destruction']),works:['Dark Magician','Shining Sarcophagus','Horus (Dark Magical Curtain)']}
];

/* obtención de cartas en Duel Links */
const SET_ES = {'Main Box':'Caja principal','Mini Box':'Mini caja','Structure Deck':'Estructura','Structure Deck EX':'Estructura EX','Structure Deck Special':'Estructura especial','Selection Box':'Caja de selección','Selection Box Mini':'Caja de selección mini','Selection Box Super Mini':'Caja de selección super mini','Deck Build Box':'Deck Build Box','Pickup Box':'Pickup Box'};
const OTHER_ES = {'Acquirable with Tickets':'Tickets','Acquirable with UR Tickets':'Ticket UR (Dream)','Acquirable with SR Tickets':'Ticket SR (Dream)','Card Trader':'Card Trader','Ex Card Trader':'Ex Card Trader','Character Deck Respect Orb Exchange':'Canje de Respect Orbs','Ranked Duels Ticket':'Ticket de duelos clasificatorios','Special Set':'Set especial','Special Campaigns':'Campaña especial','Choose Your Gift Campaign Ticket':'Ticket de regalo','Gift Campaign':'Campaña de regalo','Lifetime Missions':'Misiones permanentes'};
const TICKETS = new Set(['Acquirable with Tickets','Acquirable with UR Tickets','Acquirable with SR Tickets']);
const TRADERS = new Set(['Card Trader','Ex Card Trader']);
function dlBadge(n){
  const i=DLD.cards[n]; if(!i) return '';
  if(i.c.length) return 'Gratis · personaje';
  const free=i.o.filter(([nm])=>nm&&!TICKETS.has(nm)&&!TRADERS.has(nm)&&nm!=='Special Set'&&/Event|Missions|Ranked|Respect|Campaign|Gift/.test(nm));
  if(free.length) return 'Gratis · evento';
  if(i.o.some(([nm])=>nm==='Acquirable with UR Tickets')) return 'Ticket UR';
  if(i.o.some(([nm])=>nm==='Acquirable with SR Tickets')) return 'Ticket SR';
  if(i.o.some(([nm])=>TICKETS.has(nm))) return 'Tickets';
  const t=i.s.map(x=>x[1]||'');
  if(t.some(x=>/^Structure/.test(x))) return 'Estructura';
  if(t.some(x=>/Selection/.test(x))) return 'Caja de selección';
  if(i.s.length) return 'Paquete';
  if(i.o.some(([nm])=>TRADERS.has(nm))) return 'Card Trader';
  return 'Especial';
}
const PAID = /^Structure|Selection/;
function dlInfoHtml(n){
  const i=DLD.cards[n]; if(!i) return `<div class="fmt">Duel Links · cómo conseguirla</div><p class="eff">Sin datos: la carta no figura en las recetas de Duel Links leídas.</p>`;
  const sets=i.s.map(([nm,t,k])=>`<span>${esc(nm)} · ${esc(SET_ES[t]||t||'')}${k?' ×'+k:''}</span>`).join('');
  const chars=i.c.slice(0,8).map(([nm])=>`<span>${esc(nm)}</span>`).join('')+(i.c.length>8?`<span>+${i.c.length-8} más</span>`:'');
  const oth=i.o.map(([nm,k])=>`<span>${esc(OTHER_ES[nm]||nm||'')}${k>1?' ×'+k:''}</span>`).join('');
  const paid=i.s.some(([,t])=>PAID.test(t||''));
  return `<div class="fmt">Duel Links · cómo conseguirla</div>
   <div class="chips"><span class="chip">Rareza ${esc(i.r||'?')}</span>${i.rel?`<span class="chip">Salió ${esc(i.rel)}</span>`:''}<span class="chip">${esc(dlBadge(n))}</span></div>
   ${sets?`<div class="tags"><span><b>Cajas y estructuras</b></span>${sets}</div>`:''}
   ${chars?`<div class="tags" style="margin-top:6px"><span><b>Subiendo personaje</b></span>${chars}</div>`:''}
   ${oth?`<div class="tags" style="margin-top:6px"><span><b>Otras vías</b></span>${oth}</div>`:''}
   ${paid?'<p class="eff" style="margin-top:6px">Las estructuras y cajas de selección suelen venderse con dinero real o gemas; la fuente no publica el precio de cada una.</p>':''}`;
}

'''
sub1(r"/\* ---------- DATOS DUEL LINKS ---------- \*/.*?(?=/\* ---------- ÍNDICE CARTA)", DL_SECTION)

# ---- C. decklist + rows ----
DECKLIST = r'''function rowExtra(kind,n,pr){
  if(kind==='dl'){ const i=DLD.cards[n]; return `<span class="ex">${i&&i.r?`<em class="rar">${esc(i.r)}</em>`:''}${pr!=null?`<i class="pr">${pr}%</i>`:''}<u class="bdg">${esc(dlBadge(n))}</u></span>`; }
  const c=CARDS[canon(n)]; return c&&c[8]!=null?`<span class="ex"><i class="pr">$${c[8]}</i></span>`:'';
}
function decklist(l,kind='tcg'){
  const sec=(t,arr)=>{ if(!arr.length) return ''; const tot=arr.reduce((a,x)=>a+x[1],0);
    return `<div class="dsec"><h4>${t} · ${tot} cartas</h4><div class="dcol">${arr.map(([n,k,pr])=>`<button class="drow" data-card="${esc(n)}"><b>${k}</b>${thumb(n)}<span class="nm">${esc(n)}</span>${rowExtra(kind,n,pr)}</button>`).join('')}</div></div>`; };
  let cost='';
  if(kind==='dl'){
    cost=`<p class="cost"><strong>Costo estimado de esta lista (Duel Links Meta):</strong> ${l.gems!=null?fmtNum(l.gems)+' gemas':'sin dato'}${l.usd?' + US$ '+l.usd+' de dinero real':' (sin gasto de dinero real)'}.
      Mediana de los ${l.n} decks del arquetipo: ${l.gemsMed!=null?fmtNum(l.gemsMed)+' gemas':'sin dato'}${l.usdMed?' + US$ '+l.usdMed:''}. Skill: ${esc(l.skill||'sin skill')}.</p>`;
  } else {
    let t=0,miss=0; for(const s of ['main','extra','side']) for(const [n,k] of l[s]){ const c=CARDS[canon(n)]; if(c&&c[8]!=null) t+=c[8]*k; else miss+=k; }
    cost=`<p class="cost"><strong>Valor aproximado:</strong> US$ ${t.toFixed(0)} en TCGplayer${miss?` (sin precio para ${miss} cartas)`:''}. Precio por carta a la derecha; referencia de mercado, varía por rareza e impresión.</p>`;
  }
  return `<div class="recipe"><h3>Receta ${kind==='dl'?'más usual':'de referencia'}</h3><p class="lede" style="margin:0 0 6px">${esc(l.who)}</p>${cost}<div class="decklist">${sec('Main Deck',l.main)}${sec('Extra Deck',l.extra)}${sec('Side Deck',l.side)}</div></div>`;
}
'''
sub1(r"function decklist\(l\)\{.*?\n\}\n(?=function tbl)", DECKLIST)

# ---- D. topCards ----
TOP = r'''function topCards(f){
  const {byCard}=INDEX[f];
  const withStats = FORMATS[f].decks.filter(d=>d.cards.length&&d.lists);
  const total = withStats.reduce((a,d)=>a+d.lists,0);
  const rows=Object.entries(byCard).map(([name,uses])=>{
    const du=uses.filter(u=>u.s.kind==='mazo' && u.p!=null);
    const score = du.reduce((a,u)=>a+u.s.lists*u.p/100,0);
    return {name,du,score};
  }).filter(r=>r.du.length>=2).sort((a,b)=>b.score-a.score||b.du.length-a.du.length||a.name.localeCompare(b.name)).slice(0,14);
  const head = [`Carta`,f==='tcg'?'% de listas analizadas':'% de decks recientes','Mazos donde aparece'];
  return tbl(head,rows.map(r=>`<tr><td><button class="tcard" data-card="${esc(r.name)}">${thumb(r.name)}<span>${esc(r.name)}</span></button></td>
    <td class="big">${fmt(r.score/total*100)}</td>
    <td><div class="tags">${r.du.map(u=>`<span>${esc(u.s.name)}${u.p<100?' '+u.p+'%':''}</span>`).join('')}</div></td></tr>`));
}
'''
sub1(r"function topCards\(f\)\{.*?\n\}\n(?=\n/\* ---------- VISTAS)", TOP)

# ---- E. TCG deck row body: recipe first ----
old = "`${d.res?`<p>${esc(d.res)}</p>`:''}${d.cards.length?`<div><h3>Cartas clave (% de las listas del mazo)</h3>${cardChips(d.cards)}</div>`:''}${d.list?decklist(d.list):''}`"
new = "`${d.list?decklist(d.list,'tcg'):''}${d.res?`<p>${esc(d.res)}</p>`:''}${d.cards.length?`<div><h3>Cartas clave (% de las listas del mazo)</h3>${cardChips(d.cards)}</div>`:''}`"
assert old in s; s = s.replace(old, new)
old = "${d.list?decklist(d.list):'<p>Sin lista publicada en las fuentes leídas.</p>'}"
new = "${d.list?decklist(d.list,'tcg'):'<p>Sin lista publicada en las fuentes leídas.</p>'}"
assert old in s; s = s.replace(old, new)

# ---- F. viewDL ----
VIEWDL = r'''let dlFormat='speed';
function viewDL(){
  const list = dlFormat==='speed'?DL_SPEED:DL_RUSH;
  const D=DLD[dlFormat];
  const max=Math.max(...list.map(d=>d.share));
  const render=(d,i)=>deckRow(d,i,fmt(d.share),d.share/max*100,
    `${d.lists} de ${d.total} decks recientes${d.power!=null?` · ${d.power} puntos de poder`:''}${d.ev?` · top 4 en ${d.ev} de ${DL_EVENTS[dlFormat]} torneos`:''}`,
    `${decklist(d.list,'dl')}${d.res?`<p>${esc(d.res)}</p>`:''}`);
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
  <p class="lede">${dlFormat==='speed'?'Agrupados por tier de Duel Links Meta (19 oct).':'Duel Links Meta no asigna tiers en Rush.'} El % es la parte de los ${D.total} decks de top publicados en Duel Links Meta entre el ${DLD.window[0]} y el ${DLD.window[1]}. Abrí un mazo para ver su receta con copias, rareza y cómo conseguir cada carta.</p>
  <div class="note">La receta es el deck real reciente más parecido al promedio del arquetipo. El % de cada carta es en cuántos decks del arquetipo aparece. Solo se listan arquetipos con al menos ${dlFormat==='speed'?8:3} decks. ${dlFormat==='rush'?'Las cartas de Rush Duel no están en la base de imágenes.':''}</div>
  ${body}</section>
  <section><h2>Cuánto cuesta armarlo</h2><p class="lede">Mediana de gemas y de dinero real que Duel Links Meta estima para armar cada arquetipo (cuenta cartas que solo salen de estructuras y cajas de pago).</p>
  ${tbl(['Mazo','Gemas (mediana)','Dinero real (mediana)','Decks','Skill más usada'],costRows)}</section>
  ${dlFormat==='speed'?`
  <section><h2>Cartas más usadas</h2><p class="lede">Porcentaje de los ${D.total} decks recientes donde aparece cada carta, calculado con las recetas de cada arquetipo.</p>${topCards('dl')}</section>
  <section><h2>Motores y arquetipos</h2><p class="lede">Cruces que se ven en las recetas.</p>${enginesTable(DL_ENGINES)}</section>`:''}`;
}
'''
sub1(r"let dlFormat='speed';\nfunction viewDL\(\)\{.*?\n\}\n(?=\n/\* ---------- BUSCADOR)", VIEWDL)

# ---- G. card detail: TCG print/price and DL info ----
old = "  const total=usedCount(n);\n  return `<div class=\"detail\">"
new = """  const total=usedCount(n);
  const tp = c[6] ? `<div class="fmt">TCG · expansión, rarezas y precio</div>
    <p class="eff">Primera impresión: ${esc(c[6][0])} (${esc(c[6][1])}), ${esc(c[6][2])}. ${c[10]} impresiones en total.</p>
    <div class="chips">${c[7].map(r=>`<span class="chip">${esc(r)}</span>`).join('')}</div>
    <p class="eff">${c[8]!=null?'≈ US$ '+c[8]+' (TCGplayer)':'Sin precio TCGplayer'}${c[9]!=null?' · ≈ € '+c[9]+' (Cardmarket)':''}. Precio de referencia, varía por rareza e impresión.</p>` : '';
  sec = tp + sec + dlInfoHtml(n);
  return `<div class="detail">"""
assert old in s; s = s.replace(old, new)

# ---- H. css additions ----
css = """.recipe{display:grid;gap:8px}
.recipe h3{font-size:1.05rem;color:var(--tc);letter-spacing:.1em;text-transform:uppercase}
.cost{margin:0;font-size:.9rem;background:var(--surface2);border-left:3px solid var(--accent);padding:6px 10px}
.drow .nm{flex:1;min-width:0;overflow-wrap:anywhere}
.drow .ex{display:flex;gap:6px;align-items:center;flex:none;font:500 .72rem var(--f-data)}
.drow em.rar{font-style:normal;border:1px solid var(--line);padding:0 4px;color:var(--accent2)}
.drow i.pr{font-style:normal;color:var(--muted)}
.drow u.bdg{text-decoration:none;border:1px solid var(--line);padding:0 5px;color:var(--muted)}
"""
s = s.replace(".subd{border", css + ".subd{border", 1)
s = s.replace(".dcol{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr))", ".dcol{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr))")

# ---- I. footer ----
old = "<li>Cartas, arte y textos:"
new = "<li>Duel Links, recetas y cómo se obtiene cada carta: API pública de <a href=\"https://www.duellinksmeta.com/\">Duel Links Meta</a> (decks de top del 15 sep al 21 oct). Los nombres de las vías de obtención (tickets, Card Trader, eventos) vienen de esa fuente. El costo en gemas y dinero real es la estimación de esa fuente por mazo; el precio de cada estructura o caja no está publicado.</li>\n    <li>TCG, expansión, rarezas y precios: YGOPRODeck (precios de TCGplayer y Cardmarket, referencia de mercado).</li>\n    <li>Cartas, arte y textos:"
assert old in s; s = s.replace(old, new, 1)
s = s.replace("Duel Links: <a href=\"https://www.duellinksmeta.com/tier-list\">Duel Links Meta</a> (tier list del 19 oct) y su <a href=\"https://www.duellinksmeta.com/articles/competitive/tournament-analysis/2026/october/1\">resumen semanal</a> (13 torneos Speed y 4 Rush).",
              "Duel Links: tier list del 19 oct y <a href=\"https://www.duellinksmeta.com/articles/competitive/tournament-analysis/2026/october/1\">resumen semanal</a> de Duel Links Meta (13 torneos Speed y 4 Rush).")
s = s.replace("<li>La \"lista de referencia\" es la lista de top cut más reciente que publica KotaCards para cada mazo. Ninguna fuente publica la lista estadísticamente más común. Duel Links Meta no publica copias en texto.</li>",
              "<li>TCG: la receta es la lista de top cut más reciente que publica KotaCards para cada mazo; ninguna fuente publica la lista estadísticamente más común. Duel Links: la receta es el deck real reciente más parecido al promedio del arquetipo.</li>")
s = s.replace("<li>Los % de cartas son sobre las listas de KotaCards analizadas (9 mazos, 143 listas), no sobre todo el formato.</li>",
              "<li>TCG: los % de cartas son sobre las listas de KotaCards analizadas (9 mazos, 143 listas), no sobre todo el formato.</li>")
open(p, 'w', encoding='utf-8').write(s)
print('src patched', len(s))
