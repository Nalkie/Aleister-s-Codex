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
rep("  else if(d.srf){", "  else if(d.engm){ ENG.mode=d.engm; render(); }\n  else if(d.srf){")
rep("/* ---------- BANLIST ---------- */", r'''/* ---------- MOTORES ---------- */
const ENG={mode:'tcg',data:null,asked:false};
const ENG_MODES=[['tcg','TCG'],['ocg','OCG'],['gen','Genesys'],['speed','Duel Links · Speed'],['rush','Duel Links · Rush']];
function engLoad(){ if(ENG.asked) return; ENG.asked=true; loadData('engines').then(j=>{ ENG.data=j; if(mode==='eng') render(); }).catch(()=>{ ENG.asked=false; }); }
function engWhy(e){
  const p=[];
  if(e.archN>=3) p.push(`Se splashea en ${e.archN} arquetipos distintos (${e.archs.slice(0,3).map(a=>a[0]).join(', ')}${e.archN>3?'…':''}): sirve en muchos mazos y no solo en uno.`);
  else if(e.archN>=1) p.push(`Sostiene a ${e.archs.slice(0,2).map(a=>a[0]).join(' y ')}.`);
  if(e.wins) p.push(`${e.wins} ${e.wins===1?'victoria':'victorias'} de torneo con él en la muestra.`);
  return p.join(' ');
}
function viewEngines(){
  engLoad();
  const seg=`<div class="seg" role="group" aria-label="Modo">${ENG_MODES.map(([k,t])=>`<button data-engm="${k}" aria-pressed="${ENG.mode===k}">${t}</button>`).join('')}</div>`;
  const head=pageHead('Engines en cada modo','Un engine es un paquete de cartas que se mete (se splashea) en mazos de arquetipos distintos. Acá ves cuáles se usan hoy en cada modo, cuánto, y qué cartas lo forman. Las cartas sueltas que juega casi todo el mundo (hand traps, Pot of Greed...) no son engines: son staples y están aparte, al final.',
    how('<p>Qué mazos juegan cada engine: en TCG, OCG y Genesys salen de las etiquetas de YuGiOh Meta sobre los decks de torneos recientes; en Duel Links, de los engines de Duel Links Meta (el mazo cuenta cuando tiene al menos la mitad de las cartas que lo identifican).</p><p>Las cartas que lo forman se miden: entran las que juegan al menos el 55% de los decks con ese engine y, además, mucho más que los decks que no lo juegan (así no entra una carta que todo el mundo usa). Un engine tiene que tener al menos 3 cartas así; una etiqueta de una sola carta suelta es un staple.</p><p>"Por qué sirve" cuenta en cuántos arquetipos se juega y cuántas victorias tiene. No es una opinión: son datos de la muestra.</p>','Cómo se calcula'))+seg;
  const D=ENG.data&&ENG.data.modes[ENG.mode];
  if(!D) return head+'<p class="lede">Cargando…</p></section>';
  const E=D.engines, max=Math.max(...E.map(e=>e.share),1);
  const glance=E.length?`<div class="engstrip">${E.slice(0,10).map(e=>`<span class="pill"><b>${esc(e.n)}</b> ${fmt(e.share)}</span>`).join('')}</div>`:'';
  const row=e=>`<article class="engcard"><div class="engmain"><h3>${esc(e.n)}</h3>
        <div class="bar" style="--tc:var(--accent)"><span class="track"><span class="fill" style="width:${(e.share/max*100).toFixed(1)}%"></span></span><span class="pct">${fmt(e.share)}</span></div>
        <div class="schips"><i>${e.decks} de ${D.total} decks</i><i>${e.archN} ${e.archN===1?'arquetipo':'arquetipos'}</i>${e.wins?`<i>${e.wins} ${e.wins===1?'victoria':'victorias'}</i>`:''}</div>
        <p class="engwhy">${esc(engWhy(e))}</p>
        <h4 class="engh">Cartas del engine · ${e.pack.length}</h4>
        <div class="gal packgal">${e.pack.filter(([n])=>CARDS[n]).map(([n,p,k])=>`<button class="tile ptile" data-card="${esc(n)}" title="${esc(n)} · en el ${p}% de los decks con este engine · ${k} copias en promedio"><span class="art">${cardImg(n,false)}</span><span class="tn">${esc(n)}</span><span class="tm"><b class="vv">${p}%</b><b class="vv">×${k}</b></span></button>`).join('')}</div>
        <p class="rnote">% = decks con este engine que la juegan · ×N = copias en promedio.</p>
        ${e.txt?`<p class="engtxt"><b>${esc(e.central)}</b>: «${esc(e.txt)}»</p>`:''}</div></article>`;
  const stap=D.staples&&D.staples.length?`${secHead('Staples (no son engines)',`Cartas sueltas que juegan muchísimos mazos sin formar un paquete: el % es la parte de los ${fmtNum(D.total)} decks que las juega. Sirven en cualquier arquetipo, por eso no cuentan como engine.`)}
      <div class="gal packgal">${D.staples.filter(x=>CARDS[x.n]).map(x=>`<button class="tile ptile" data-card="${esc(x.n)}" title="${esc(x.n)}"><span class="art">${cardImg(x.n,false)}</span><span class="tn">${esc(x.n)}</span><span class="tm"><b class="vv">${x.pct}%</b></span></button>`).join('')}</div></section>`:'';
  let extra='';
  if(ENG.mode==='speed') extra=`${secHead('Paquetes a mano','Paquetes que se ven en las recetas, analizados a mano.')}${enginesTable(DL_ENGINES.filter(e=>!['d-ed','d-generic'].includes(e.id)))}</section>`;
  else if(ENG.mode==='tcg') extra=`${secHead('Combinaciones a mano','Engines que cruzan arquetipos, analizados a mano el 21 de octubre. La última columna dice dónde más funciona cada uno.')}${enginesTable(TCG_ENGINES)}</section>`;
  return head+`${glance}<p class="lede" style="margin-top:var(--s3)">${E.length?`${E.length} engines en ${fmtNum(D.total)} decks entre el ${dmy(D.window[0])} y el ${dmy(D.window[1])}.`:'No hay engines con datos suficientes en este modo (Duel Links Meta define muy pocos en Rush).'}</p>
    <div class="englist">${E.map(row).join('')}</div></section>${stap}${extra}`;
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
.packgal{grid-template-columns:repeat(auto-fill,minmax(92px,1fr))}
.packgal .tn{font-size:.62rem}
.engh{margin:var(--s2) 0 0;font:700 .8rem var(--f-data);letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 37 ok')
