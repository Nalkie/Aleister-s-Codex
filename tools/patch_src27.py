"""OCG y formatos retro con la misma lista de "Mejores mazos" que Advanced, Genesys y Duel Links (tiers, barras, receta de cada mazo), OCG en banlist,
buscador, constructor, torneos y Guía, y arreglos de la revisión: viewport móvil, solapes de tickets y de nombres, mensajes del constructor.
Datos: data/ygmx.js (tools/ygm.py + tools/formats_meta.py) y data/formats.js. Backup: src.before_patch27.html."""
import shutil
shutil.copy('src.html', 'src.before_patch27.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- FMT_RETRO antes de ymDecks (se usa al cargar) y con OCG ----------
rep("const FMT_RETRO={edison:'Edison',goat:'Goat',hat:'HAT'};\n", "")
rep("const YGM = /*__YGMDATA__*/{};", "const FMT_RETRO={ocg:'OCG',edison:'Edison',goat:'Goat',hat:'HAT'};   // formatos del TCG con su propia banlist y lista de cartas (data/formats.js)\nconst YGM = /*__YGMDATA__*/{};")

# ---------- textos ----------
rep("no hay Xyz, Péndulo ni Link, y no existe la Zona de Monstruo Adicional.'", "no hay Xyz, Péndulo ni Link, y no existe la Zona de Monstruo Adicional (la zona extra de los Link y los Péndulo).'")
rep("Las cartas se leen con su texto y rulings de la época, no con el texto actual.", "Las cartas se leen con el texto y las reglas oficiales (rulings) de la época, no con el texto actual.")
rep("const RETRO_BAN=", r'''RETRO_ES.ocg={n:'OCG',era:'Japón y Asia',
  lede:'El OCG (Official Card Game) es la versión del juego que se vende en Japón y Asia. Comparte la mayoría de las cartas con el TCG, pero sus expansiones suelen salir antes y su banlist es otra, por eso mucha gente mira el OCG para anticipar lo que va a pasar en el TCG.',
  rules:['Mismo formato de mazo que el TCG: Main Deck de 40 a 60 cartas; Extra Deck y Side Deck de hasta 15.','Banlist propia, la que publica YGOPRODeck para el OCG (hoy: 93 prohibidas, 93 limitadas y 13 semi-limitadas).','Hay cartas que solo existen en el OCG y otras que todavía no salieron ahí; el buscador y el constructor marcan cada caso.','Las listas y los resultados de torneos vienen de YuGiOh Meta.'],
  meta:'Los mazos más fuertes de hoy están en esta misma pestaña, con su receta real.'};
const RETRO_BAN=''')

# ---------- pestaña TCG: misma lista de mazos para OCG, Edison, Goat y HAT ----------
a = s.index("const fmtBar=cur=>")
b = s.index("function viewTCGAdv(){")
new = r'''const fmtBar=cur=>`<div class="seg fmtbar" role="group" aria-label="Formato del TCG">${['adv','ocg','edison','goat','hat'].map(k=>`<button data-tcgf="${k}" aria-pressed="${cur===k}">${RETRO_ES[k].n}</button>`).join('')}</div>`;
const YGMX={data:null,asked:false,decks:{}};
function ymxLoad(){ if(YGMX.asked) return; YGMX.asked=true; loadData('ygmx').then(j=>{ YGMX.data=j; YGMX.decks={}; if(['tcg','ev'].includes(mode)) render(); }).catch(()=>{ YGMX.asked=false; }); }
const ymxDecks=k=>YGMX.decks[k]||(YGMX.decks[k]=ymDecks(k,YGMX.data[k]));
const evAll=()=>(EVD||[]).concat(YGMX.data?YGMX.data.ocgEvents:[]);
function viewTCG(){
  return fmtBar(TCGF)+(TCGF==='adv'?viewTCGAdv():viewMetaFmt(TCGF));
}
function viewMetaFmt(k){
  fmLoad(); ymxLoad();
  const I=RETRO_ES[k], D=YGMX.data&&YGMX.data[k], F=FM.data&&FM.data.formats[k], retro=k!=='ocg';
  if(!D||!F) return pageHead(`Mejores mazos · ${I.n}`,I.lede)+'<p class="lede">Cargando…</p></section>';
  const all=ymxDecks(k), decks=all.filter(d=>!d.out), max=Math.max(...decks.map(d=>d.share),1);
  const withCards=decks.filter(d=>d.cards.length&&d.lists), listsTotal=withCards.reduce((a,d)=>a+d.lists,0);
  const cnt=b=>Object.values(F.ban).filter(v=>v===b).length;
  const safe=u=>/^https:\/\//.test(u||'')?u:'';
  const head=pageHead(`Mejores mazos · ${I.n}`,retro
      ?`Los arquetipos que más se juegan en ${I.n} según ${fmtNum(D.total)} mazos de ${D.events} torneos del último año. Abrí un mazo para ver su receta real y sus cartas clave.`
      :`Los arquetipos más fuertes del OCG según ${fmtNum(D.total)} decks de torneos recientes. Abrí un mazo para ver su receta real y sus cartas clave.`,
    how(retro
      ?`<p>Muestra: ${fmtNum(D.total)} mazos de ${D.events} torneos de ${I.n} entre el ${dmy(D.window[0])} y el ${dmy(D.window[1])}. Son eventos de la comunidad (no hay torneos oficiales de este formato) y los registra <a href="https://formatlibrary.com/">Format Library</a>. La barra muestra la parte de todos los mazos que jugaron, no solo los del top.</p><p>El tier usa el peso de los resultados del top cut (1.º puesto = 8, 2.º = 5, top 4 = 3, top 8 = 2): T1 con 8% o más del total, T2 con 4% o más, T3 con 2% o más.</p><p>La receta es la lista real reciente más parecida al promedio de las listas del arquetipo que llegaron al top 8. Los mazos con menos de ${5} apariciones no se muestran.</p>`
      :`<p>Muestra: ${fmtNum(D.total)} decks de torneos OCG entre el ${dmy(D.window[0])} y el ${dmy(D.window[1])}, de YuGiOh Meta.</p><p>${tierLede()}</p><p>La barra muestra la parte de los decks de la muestra. Las recetas son listas reales del OCG: pueden incluir cartas que todavía no salieron en el TCG.</p>`),
    '')+`<div class="seg mini" style="margin-top:var(--s2)"><span class="pill">${retro?'Formato desde '+dmy(F.date):'Versión de Japón y Asia'}</span><span class="pill">Banlist ${esc(retro?(RETRO_BAN[F.banlistName]||F.banlistName):'vigente')}</span><span class="pill">${F.pool.length.toLocaleString('es-AR')} cartas legales</span><span class="pill">${cnt(0)} prohibidas · ${cnt(1)} limitadas · ${cnt(2)} semi-limitadas</span></div>`;
  return head+`
  ${grouped(decks,(d,i)=>deckRow(d,i,fmt(d.share),d.share/max*100,`${d.c} de ${d.total} decks · ${d.wins} victorias · ${d.top4} top 4 · ${fmt(d.pts)} del peso de resultados`,
     `${decklist(d.list,k)}<p>${esc(d.res)}</p>${d.cards.length?`<div><h3>Cartas con más presencia (% de los decks del arquetipo)</h3>${cardChips(d.cards.slice(0,18))}</div>`:''}`))}
  </section>
  ${outsideSection(all,k,'Ganadores fuera del meta','Arquetipos que no llegan al tier 3 (menos de 2% del peso de resultados y menos de 2,5% de los decks) pero ganaron al menos un torneo en la muestra.')}
  ${secHead(`Sobre ${I.n}`,I.lede)}
    <h3 style="margin-top:var(--s3)">Cómo se juega</h3><ul class="rrules">${I.rules.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p class="lede">${esc(I.meta)}</p>
    <p style="margin:var(--s3) 0"><button class="sbtn" data-gobfmt="${k}">Ver la banlist completa</button> <button class="sbtn" data-gotab="deck" data-dkf="${k}">Armar un mazo de ${I.n}</button></p>
    ${retro?`<h3 style="margin-top:var(--s5)">Torneos recientes</h3>${F.events.length?`<div class="tbl"><table class="ptab"><thead><tr><th>Torneo</th><th>Fecha</th><th>Jugadores</th><th>Ganador</th><th>Comunidad</th></tr></thead><tbody>${F.events.map(e=>`<tr><td>${safe(e.url)?`<a href="${esc(safe(e.url))}" target="_blank" rel="noopener noreferrer">${esc(e.n)}</a>`:esc(e.n)}</td><td>${e.d?dmy(e.d):''}</td><td>${e.size||''}</td><td>${esc(e.winner||'')}</td><td>${esc(e.community||'')}</td></tr>`).join('')}</tbody></table></div>`:''}<p class="rnote">Datos de Format Library.</p>`:'<p class="rnote">Los torneos del OCG están en la pestaña Eventos.</p>'}
  </section>`;
}
'''
s = s[:a] + new + s[b:]

# ---------- ymDecks para cualquier formato ----------
rep("function ymDecks(fmt){\n  const D=YGM[fmt];", "function ymDecks(fmt,src){\n  const D=src||YGM[fmt];")
rep("const list={kind:fmt==='gen'?'gen':'tcg',name,price:w.price,", "const list={kind:fmt==='gen'?'gen':FMT_RETRO[fmt]?fmt:'tcg',name,price:w.price,")

# ---------- deckRow: arte de cartas que no están en el arte local ----------
rep("function deckRow(d,i,pctVal,barVal,metaTxt,body){\n  const art=artOf(d.art);",
    "const remoteArt=n=>{ try{ const c=CARDS[canon(n)]; return c&&c[C.ID]?`https://images.ygoprodeck.com/images/cards_cropped/${c[C.ID]}.jpg`:''; }catch(e){ return ''; } };\nfunction deckRow(d,i,pctVal,barVal,metaTxt,body){\n  const art=artOf(d.art)||(d.art?remoteArt(d.art):null);")
rep("const cid=ARTS[d.art], fg=cid?", "const cid=ARTS[d.art]||(d.art&&remoteArt(d.art)?cardId(d.art):0), fg=cid?")

# ---------- receta: límite según el formato de la lista ----------
rep("if(c&&c[C.BAN]>=0&&c[C.BAN]<3) lim++; }", "if(FMT_RETRO[kind]){ const l=fmLimit(kind,canon(n)); if(l!=null&&l>=0&&l<3) lim++; } else if(c&&c[C.BAN]>=0&&c[C.BAN]<3) lim++; }")
rep("rstat('Con límite en el TCG',`${lim}<em>cartas</em>`)", "rstat('Con límite en '+(FMT_RETRO[kind]||'el TCG'),`${lim}<em>cartas</em>`)")
rep("Las marcas rojas son cartas de la banlist del TCG.", "Las marcas rojas son cartas de la banlist ${FMT_RETRO[kind]?'de '+FMT_RETRO[kind]:'del TCG'}.")
rep("DK.fmt=r.kind==='dl'?'dl':r.kind==='gen'?'gen':'tcg';", "DK.fmt=r.kind==='dl'?'dl':r.kind==='gen'?'gen':FMT_RETRO[r.kind]?r.kind:'tcg';")

# ---------- banlist: nota del OCG ----------
rep("note=`Banlist ${RETRO_BAN[F.banlistName]||F.banlistName} del formato ${F.name}, de Format Library",
    "note=f==='ocg'?`Banlist vigente del OCG, la que publica YGOPRODeck para cada carta. Las cartas que no figuran van hasta 3 copias si existen en el OCG (${F.pool.length.toLocaleString('es-AR')} cartas).`:`Banlist ${RETRO_BAN[F.banlistName]||F.banlistName} del formato ${F.name}, de Format Library")

# ---------- constructor ----------
rep("const FMT_ES={tcg:'TCG',edison:'Edison',", "const FMT_ES={tcg:'TCG',ocg:'OCG',edison:'Edison',")
rep("${['tcg','edison','goat','hat','gen','dl'].map(f=>`<button data-dkfmt=", "${['tcg','ocg','edison','goat','hat','gen','dl'].map(f=>`<button data-dkfmt=")
rep("const acc={tcg:'#4ee1ff',edison:", "const acc={tcg:'#4ee1ff',ocg:'#4ee1ff',edison:")
rep("function viewDeck(){\n  fmLoad();\n", r'''function dkCountNote(names,q){
  const n=names.length, f=FMT_ES[DK.fmt];
  if(!n&&q&&FMT_RETRO[DK.fmt]){ const later=searchNames(NAMES.filter(x=>fmLimit(DK.fmt,x)===-1),q,()=>0).length; if(later) return `Ninguna carta de ${f} con ese nombre: ${later===1?'hay una carta que salió':'hay '+later+' cartas que salieron'} después de ese formato (o que no existe en él).`; }
  return `${n.toLocaleString('es-AR')} ${n===1?'carta':'cartas'} de ${f}, también las prohibidas (con la marca roja). Solo las que tienen arte.${q?' Acepta errores de tipeo.':''}`;
}
function viewDeck(){
  fmLoad();
''')
rep("${names.length.toLocaleString('es-AR')} cartas de ${FMT_ES[DK.fmt]}, también las prohibidas (con la marca roja). Solo las que tienen arte.${q?' Acepta errores de tipeo.':''}</p>", "${dkCountNote(names,q)}</p>")

# ---------- torneos OCG en Eventos ----------
rep("const fm=f==='gen'?'Genesys':'TCG', all=(EVD||[]).filter(e=>e.f===fm)", "const fm=f==='gen'?'Genesys':f==='ocg'?'OCG':'TCG', all=evAll().filter(e=>e.f===fm)")
rep("[['dl','Duel Links'],['tcg','TCG'],['gen','Genesys']].map(([k,t])=>`<button data-evfmt=", "[['dl','Duel Links'],['tcg','TCG'],['ocg','OCG'],['gen','Genesys']].map(([k,t])=>`<button data-evfmt=")
rep("const need=EV.fmt==='dl'?!DLI:!EVD;", "const need=EV.fmt==='dl'?!DLI:(!EVD||(EV.fmt==='ocg'&&!YGMX.data));")
rep("  loadData('events').then(j=>{ EVD=j; if(mode==='ev') render(); }).catch(()=>{});\n}", "  loadData('events').then(j=>{ EVD=j; if(mode==='ev') render(); }).catch(()=>{});\n  ymxLoad();\n}")

# ---------- render: la pestaña TCG de un formato necesita la base de cartas ----------
rep("(DBINFO||!['ex','sets','ban','deck','guide','ev'].includes(mode))", "(DBINFO||!(['ex','sets','ban','deck','guide','ev'].includes(mode)||(mode==='tcg'&&TCGF!=='adv')))")

# ---------- Guía ----------
rep("${['adv','edison','goat','hat'].map(card).join('')}", "${['adv','ocg','edison','goat','hat'].map(card).join('')}")
rep("${k==='adv'?'Ver los mejores mazos':'Ver el formato'}", "Ver los mejores mazos")
rep("El Advanced es el actual; Edison, Goat y HAT son formatos históricos que la comunidad sigue jugando con la banlist y las cartas de su época.", "El Advanced es el actual; el OCG es la versión de Japón y Asia; Edison, Goat y HAT son formatos históricos que la comunidad sigue jugando con la banlist y las cartas de su época.")

# ---------- fuentes ----------
rep("<li>Formatos retro del TCG", "<li>OCG: banlist y cartas de <a href=\"https://ygoprodeck.com/\">YGOPRODeck</a>; mazos y torneos de YuGiOh Meta. Anniversary Boxes: las listas de cartas que Duel Links Meta no incluye salen de la <a href=\"https://yugioh.fandom.com/wiki/Yu-Gi-Oh!_Wiki\">Yu-Gi-Oh! Wiki</a> (CC BY-SA). Texto de las cartas de Rush Duel: Duel Links Meta (YGOPRODeck no las publica).</li>\n  <li>Formatos retro del TCG")

# ---------- estilos y viewport ----------
rep('<meta name="claude:viewport-fit-sides" content="cover">', '<meta name="claude:viewport-fit-sides" content="cover">\n<meta name="viewport" content="width=device-width,initial-scale=1">')
rep(".fmtbar{margin:var(--s4) 0 0}", """.fmtbar{margin:var(--s4) 0 0}
.setb .schips i,.setb .stxt .chip{white-space:nowrap}
.setb .stxt{position:relative;z-index:1}
.sethero:has(.spack.tk) .shtxt{max-width:calc(100% - 210px)}
.sethero:has(.spack.vic) .shtxt{max-width:calc(100% - 180px)}""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 27 ok')
