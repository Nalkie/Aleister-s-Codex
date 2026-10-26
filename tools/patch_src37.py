"""1) Pestaña "Motores": todos los motores que se usan en cada modo (TCG, OCG, Genesys, Duel Links Speed y Rush) de un vistazo, con cuánto se juegan y por qué sirven.
2) Buscador de cartas: al tocar una carta de la lista no vuelve al inicio, se queda donde estabas. 3) "No es jugable" en lugar de "No existe en el formato".
Datos: data/engines.js (tools/fetch_engines.py + tools/engines.py). Backup: src.before_patch37.html."""
import shutil
shutil.copy('src.html', 'src.before_patch37.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- 3) "No es jugable" ----------
rep("l<0?'<b>No existe en el formato</b>':", "l<0?`<b>No es jugable</b><span class=\"hint\">${k==='ocg'?'Todavía no salió en el OCG.':'Salió después de este formato.'}</span>`:")
rep("const tcg = b<0 ? '<b>No existe en el TCG</b>'", "const tcg = b<0 ? '<b>No es jugable</b><span class=\"hint\">Todavía no salió en el TCG: solo está en el OCG o en Duel Links.</span>'")
rep("g===-2 ? '<b>No existe en Genesys</b>'", "g===-2 ? '<b>No es jugable</b><span class=\"hint\">No existe en Genesys.</span>'")

# ---------- 2) el buscador conserva la posición ----------
rep("else if(d.card){ const was=mode; goCard(d.card); render(); if(was!=='ex') window.scrollTo(0,0); else { const dt=document.querySelector('.detail'); if(dt&&dt.getBoundingClientRect().top<0) dt.scrollIntoView({block:'start'}); } }",
    "else if(d.card){ const was=mode, y=window.scrollY; goCard(d.card); render(); if(was!=='ex') window.scrollTo(0,0); else { window.scrollTo(0,y); const dt=document.querySelector('.detail'); if(innerWidth<=900&&dt&&dt.getBoundingClientRect().top<0) dt.scrollIntoView({block:'start'}); } }")

# ---------- 1) pestaña Motores ----------
a = s.index('<button class="tool" role="tab" id="tab-obt"')
b = s.index('</button>', a) + len('</button>')
s = s[:b] + '\n    <button class="tool" role="tab" id="tab-eng" data-mode="eng"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="3"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1"/></svg>Motores</button>' + s[b:]
rep("body.ex,body.sets,body.obt,body.ban,body.ev{--accent:var(--ac-tool)}", "body.ex,body.sets,body.obt,body.eng,body.ban,body.ev{--accent:var(--ac-tool)}")
rep("obt:['Obtención',viewSets],", "obt:['Obtención',viewSets],eng:['Motores',viewEngines],")
rep("['ex','sets','obt','ban','deck','guide','ev'].includes(mode)||(mode==='tcg'&&TCGF!=='adv')", "['ex','sets','obt','eng','ban','deck','guide','ev'].includes(mode)||(mode==='tcg'&&TCGF!=='adv')")
rep("  else if(d.srf){", "  else if(d.engm){ ENG.mode=d.engm; ENG.sel=null; render(); }\n  else if(d.engcard!==undefined){ const [en,cn]=d.engcard.split('|'); ENG.sel={e:en,c:cn}; render(); }\n  else if(d.engclose){ ENG.sel=null; render(); }\n  else if(d.srf){")
rep("/* ---------- BANLIST ---------- */", r'''/* ---------- ENGINES ---------- */
const ENG={mode:'tcg',data:null,asked:false,sel:null};
const ENG_MODES=[['tcg','TCG'],['ocg','OCG'],['gen','Genesys'],['speed','Duel Links · Speed'],['rush','Duel Links · Rush']];
function engLoad(){ if(ENG.asked) return; ENG.asked=true; loadData('engines').then(j=>{ ENG.data=j; if(mode==='eng') render(); }).catch(()=>{ ENG.asked=false; }); }
function engWhy(e){
  const p=[];
  if(e.archN>=3) p.push(`Se splashea en ${e.archN} arquetipos distintos (${e.archs.slice(0,3).map(a=>a[0]).join(', ')}${e.archN>3?'…':''}): sirve en muchos mazos y no solo en uno.`);
  else if(e.archN>=1) p.push(`Sostiene a ${e.archs.slice(0,2).map(a=>a[0]).join(' y ')}.`);
  if(e.wins) p.push(`${e.wins} ${e.wins===1?'victoria':'victorias'} de torneo con él en la muestra.`);
  return p.join(' ');
}
function engInsp(D){   // vista previa de la carta elegida y cómo funciona su engine
  const s=ENG.sel; if(!s) return '';
  const e=s.e?(D.engines.find(x=>x.n===s.e)||(D.more||[]).find(x=>x.n===s.e)):null, row=e?e.pack.find(p=>p[0]===s.c):null, n=s.c;
  if(!CARDS[n]) return '';
  const how=e?`<h4 class="engh">Cómo funciona ${esc(e.n)}</h4>
    <p class="engwhy">Lo forman ${e.pack.length} cartas. Lo juegan ${e.decks} decks (${fmt(e.share)}) de ${e.archN} ${e.archN===1?'arquetipo':'arquetipos'}${e.archs.length?': '+e.archs.slice(0,4).map(a=>esc(a[0])+' ('+a[1]+')').join(', '):''}${e.wins?` y suma ${e.wins} ${e.wins===1?'victoria':'victorias'} de torneo`:''}.</p>
    <ol class="engsteps">${e.pack.map(([c,p,k,t])=>`<li><button class="lnk${c===n?' on':''}" data-engcard="${esc(e.n)}|${esc(c)}">${esc(c)}</button> <span class="mini">${p}% de los decks · ×${k}</span>${t?`<br><span class="engt">${esc(t)}</span>`:''}</li>`).join('')}</ol>`
    :`<p class="rnote">Es un staple: la juega mucha gente en mazos de cualquier arquetipo, no forma parte de un engine.</p>`;
  return `<aside class="einsp"><div class="sihead"><h3>${esc(n)}</h3><button class="abtn" data-engclose="1">Cerrar</button></div>
    ${row?`<p class="rnote">Parte del engine <b>${esc(e.n)}</b> · en el ${row[1]}% de los decks que lo juegan · ${row[2]} copias en promedio</p>`:''}
    <div class="einspimg"><img src="${imgUrl(cardId(n),true)}" alt="${esc(n)}" referrerpolicy="no-referrer" onerror="this.remove()"><div class="einspinfo"><div id="ei-chips" class="chips"></div><div id="ei-stats"></div></div></div>
    <p class="eff" id="ei-eff">Cargando…</p>
    <p><button class="sbtn" data-card="${esc(n)}">Ver en el buscador de cartas</button></p>
    ${how}</aside>`;
}
async function fillEngInsp(n){
  let d; try{ d=await getDetail(n); }catch(e){ const el=$('#ei-eff'); if(el) el.textContent='No se pudo cargar el detalle de la carta.'; return; }
  if(mode!=='eng'||!ENG.sel||ENG.sel.c!==n||!$('#ei-eff')) return;
  $('#ei-eff').textContent=d.d||'';
  $('#ei-chips').innerHTML=d.ty?`<span class="chip">${esc(d.ty)}</span>`:'';
  $('#ei-stats').innerHTML=monsterStats(d);
}
function viewEngines(){
  engLoad();
  const seg=`<div class="seg" role="group" aria-label="Modo">${ENG_MODES.map(([k,t])=>`<button data-engm="${k}" aria-pressed="${ENG.mode===k}">${t}</button>`).join('')}</div>`;
  const head=pageHead('Engines en cada modo','Un engine es un grupo selecto de cartas de un arquetipo que se splashea (se mete) en mazos de otros arquetipos: Bystial, Horus, Sky Striker con Engage! y Widow Anchor... Acá ves cuáles se usan hoy en cada modo, cuánto, y qué cartas lo forman. Tocá una carta para ver su efecto y cómo funciona el engine. Las cartas sueltas que juega casi todo el mundo (hand traps, Pot of Greed...) no son engines: son staples y están aparte, al final.',
    how('<p>Qué mazos juegan cada engine: en TCG, OCG y Genesys salen de las etiquetas de YuGiOh Meta sobre los decks de torneos recientes; en Duel Links, de los engines de Duel Links Meta (el mazo cuenta cuando tiene al menos la mitad de las cartas que lo identifican).</p><p>Hay dos tipos de engine. Los que se definen por nombre (The Fallen &amp; The Virtuous, Bystial, Ars Magna, K9, Kashtira, Sinful Spoils) se cuentan siempre: un mazo los juega cuando tiene al menos 2 de sus cartas (1 en Ars Magna), y si casi no se usan figuran abajo con su número real. Todos los engines que definen YuGiOh Meta y Duel Links Meta se cuentan, aunque se usen poco: arriba están los que juegan 5 o más mazos y 1% o más, y en «Más engines» el resto con su número real. Los demás son grupos de cartas que aparecen juntas (cada una en el 60% o más de los mazos de la otra) en al menos 3 arquetipos, o engines de Duel Links Meta y YuGiOh Meta con su arquetipo; en ese caso solo cuentan los mazos que los splashean y se miden entre ellos.</p><p>"Cómo funciona" lista las cartas del engine con el texto de su efecto, más en cuántos mazos y arquetipos se juega. Son datos de la muestra, no una opinión.</p>','Cómo se calcula'))+seg;
  const D=ENG.data&&ENG.data.modes[ENG.mode];
  if(!D) return head+'<p class="lede">Cargando…</p></section>';
  const E=D.engines, max=Math.max(...E.map(e=>e.share),1);
  const glance=E.length?`<div class="engstrip">${E.slice(0,10).map(e=>`<span class="pill"><b>${esc(e.n)}</b> ${fmt(e.share)}</span>`).join('')}</div>`:'';
  const tile=(en,n,p,k,tt)=>`<button class="tile ptile${ENG.sel&&ENG.sel.c===n&&ENG.sel.e===en?' on':''}" data-engcard="${esc(en)}|${esc(n)}" title="${esc(n)}${tt}"><span class="art">${cardImg(n,false)}</span><span class="tn">${esc(n)}</span><span class="tm"><b class="vv">${p}%</b>${k?`<b class="vv">×${k}</b>`:''}</span></button>`;
  const row=e=>`<article class="engcard"><div class="engmain"><h3>${esc(e.n)}</h3>
        <div class="bar" style="--tc:var(--accent)"><span class="track"><span class="fill" style="width:${(e.share/max*100).toFixed(1)}%"></span></span><span class="pct">${fmt(e.share)}</span></div>
        <div class="schips"><i>${e.decks} ${e.decks===1?'deck lo juega':'decks lo juegan'}</i>${e.splash&&e.splash!==e.decks?`<i>${e.splash} lo splashean</i>`:''}<i>${e.archN} ${e.archN===1?'arquetipo':'arquetipos'}</i>${e.wins?`<i>${e.wins} ${e.wins===1?'victoria':'victorias'}</i>`:''}</div>
        <p class="engwhy">${esc(engWhy(e))}</p>
        <h4 class="engh">Cartas del engine · ${e.pack.length}</h4>
        <div class="gal packgal">${e.pack.filter(([n])=>CARDS[n]).map(([n,p,k])=>tile(e.n,n,p,k,` · en el ${p}% de los decks con este engine · ${k} copias en promedio`)).join('')}</div>
        <p class="rnote">% = decks con este engine que la juegan · ×N = copias en promedio. Tocá una carta para ver cómo funciona.</p></div></article>`;
  const stap=D.staples&&D.staples.length?`${secHead('Staples (no son engines)',`Cartas sueltas que juegan muchísimos mazos sin formar un paquete: el % es la parte de los ${fmtNum(D.total)} decks que las juega. Sirven en cualquier arquetipo, por eso no cuentan como engine.`)}
      <div class="gal packgal">${D.staples.filter(x=>CARDS[x.n]).map(x=>tile('',x.n,x.pct,0,'')).join('')}</div></section>`:'';
  const moreL=(D.more||[]).filter(x=>x.decks>0), low=moreL.length?`${secHead(`Más engines · ${moreL.length}`,`Engines que hoy juegan menos de 5 mazos o menos del 1% de la muestra de este modo. El número de decks es real: sirve para saber que existen y cuánto se ven. Abrí uno para ver sus cartas.`)}
      <div class="engmore">${moreL.map(e=>`<details class="engm"><summary><b>${esc(e.n)}</b><span class="pill">${e.decks} ${e.decks===1?'deck':'decks'} · ${fmt(e.share)}</span>${e.archs&&e.archs.length?`<span class="mini">${e.archs.slice(0,3).map(a=>esc(a[0])).join(' · ')}</span>`:''}</summary>
        <div class="gal packgal">${e.pack.filter(([n])=>CARDS[n]).map(([n,p,k])=>tile(e.n,n,p,k,` · en el ${p}% de los decks con este engine`)).join('')}</div></details>`).join('')}</div></section>`:'';
  let extra='';
  if(ENG.mode==='speed') extra=`${secHead('Paquetes a mano','Paquetes que se ven en las recetas, analizados a mano.')}${enginesTable(DL_ENGINES.filter(e=>!['d-ed','d-generic'].includes(e.id)))}</section>`;
  else if(ENG.mode==='tcg') extra=`${secHead('Combinaciones a mano','Engines que cruzan arquetipos, analizados a mano el 21 de octubre. La última columna dice dónde más funciona cada uno.')}${enginesTable(TCG_ENGINES)}</section>`;
  const main=`${glance}<p class="lede" style="margin-top:var(--s3)">${E.length?`${E.length} engines en ${fmtNum(D.total)} decks entre el ${dmy(D.window[0])} y el ${dmy(D.window[1])}.`:'No hay engines con datos suficientes en este modo (Duel Links Meta define muy pocos en Rush).'}</p>
    <div class="englist">${E.map(row).join('')}</div>${low}${stap}${extra}`;
  const insp=ENG.sel?engInsp(D):'';
  return head+(insp?`<div class="enggrid"><div>${main}</div>${insp}</div>`:main)+'</section>';
}

/* ---------- BANLIST ---------- */''')
rep(".fmtbar{margin:var(--s4) 0 0}", """.fmtbar{margin:var(--s4) 0 0}
.engstrip{display:flex;flex-wrap:wrap;gap:var(--s2);margin:var(--s3) 0}
.engstrip .pill b{font-weight:700}
.englist{display:grid;gap:var(--s3)}
.engcard{position:relative;display:flex;gap:var(--s4);align-items:flex-start;padding:var(--s4);border:1px solid var(--line);border-radius:var(--r);background:linear-gradient(115deg,color-mix(in srgb,var(--accent) 9%,var(--surface)),var(--surface) 60%);overflow:hidden}
.engmain{display:grid;gap:var(--s2);min-width:0;flex:1}
.engmain h3{font:800 1.15rem var(--f-display);letter-spacing:-.01em}
.engwhy{margin:0;color:var(--fg)}
.engtxt{margin:0;color:var(--muted);font-size:.84rem}
.engtxt b{color:var(--fg)}
.engcards{display:flex;flex-wrap:wrap;gap:var(--s2)}
.enggrid{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(320px,.95fr);gap:var(--s5);align-items:start}
.einsp{position:sticky;top:132px;max-height:calc(100vh - 150px);overflow-y:auto;overflow-x:hidden;display:grid;gap:var(--s3);align-content:start;padding:var(--s4);border:1px solid var(--line2);border-radius:var(--r);background:linear-gradient(150deg,color-mix(in srgb,var(--accent) 8%,var(--surface)),var(--surface))}
.einspimg{display:flex;gap:var(--s3);align-items:flex-start}
.einspimg img{width:132px;flex:none;border-radius:8px;box-shadow:0 14px 26px -10px #000}
.einspinfo{display:grid;gap:var(--s2);min-width:0}
.engsteps{margin:0;padding-left:1.2em;display:grid;gap:var(--s3)}
.engsteps li::marker{color:var(--accent);font-weight:700}
.engsteps .lnk.on{color:var(--accent);font-weight:700}
.engt{color:var(--muted);font-size:.8rem;line-height:1.4}
@media(max-width:1000px){.enggrid{grid-template-columns:1fr}.einsp{position:fixed;left:8px;right:8px;bottom:8px;top:auto;max-height:80vh;z-index:55;box-shadow:0 0 0 100vmax rgba(0,0,0,.55),0 30px 80px -20px var(--accent)}}
.packgal{grid-template-columns:repeat(auto-fill,minmax(92px,1fr))}
.packgal .tn{font-size:.62rem}
.engmore{display:grid;gap:var(--s2)}
.engm{border:1px solid var(--line);border-radius:var(--r2);background:var(--surface);padding:var(--s2) var(--s3)}
.engm summary{display:flex;align-items:center;gap:var(--s3);cursor:pointer;flex-wrap:wrap}
.engm summary b{font:700 .95rem var(--f-display)}
.engm[open] summary{margin-bottom:var(--s3)}
.engh{margin:var(--s2) 0 0;font:700 .8rem var(--f-data);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}""")
rep("if((mode==='sets'||mode==='obt')&&SETS.card) fillSInsp(SETS.card);", "if((mode==='sets'||mode==='obt')&&SETS.card) fillSInsp(SETS.card);\n  if(mode==='eng'&&ENG.sel) fillEngInsp(ENG.sel.c);")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 37 ok')
