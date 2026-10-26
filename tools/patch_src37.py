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
  if(e.archN>=3) p.push(`Se juega en ${e.archN} arquetipos distintos (${e.archs.slice(0,3).map(a=>a[0]).join(', ')}${e.archN>3?'…':''}): sirve en muchos mazos y no solo en uno.`);
  else if(e.archN>=1) p.push(`Sostiene a ${e.archs.slice(0,2).map(a=>a[0]).join(' y ')}.`);
  if(e.wins) p.push(`${e.wins} ${e.wins===1?'victoria':'victorias'} de torneo con él en la muestra.`);
  return p.join(' ');
}
function engShared(){   // cartas que se repiten entre arquetipos de Duel Links (Duel Links Meta define pocos motores)
  const decks=(ENG.mode==='speed'?DL_SPEED:DL_RUSH).filter(d=>!d.out&&d.cards&&d.cards.length), m=new Map();
  for(const d of decks) for(const [n,p] of d.cards) if(p>=50){ const e=m.get(n)||{n,a:[]}; e.a.push(d.n); m.set(n,e); }
  return [...m.values()].filter(e=>e.a.length>=3).sort((a,b)=>b.a.length-a.a.length).slice(0,18);
}
function viewEngines(){
  engLoad();
  const seg=`<div class="seg" role="group" aria-label="Modo">${ENG_MODES.map(([k,t])=>`<button data-engm="${k}" aria-pressed="${ENG.mode===k}">${t}</button>`).join('')}</div>`;
  const head=pageHead('Motores en cada modo','Un motor es un grupo de cartas que se juegan juntas y se repiten en mazos de arquetipos distintos. Acá ves cuáles se usan hoy en cada modo, cuánto, y por qué importan.',
    how('<p>Cada motor sale de las etiquetas de YuGiOh Meta sobre los decks de torneos recientes (TCG, OCG y Genesys). En Duel Links un motor cuenta cuando el mazo tiene al menos la mitad de las cartas que lo identifican según Duel Links Meta.</p><p>"Por qué sirve" junta lo que se cuenta (en cuántos arquetipos se juega y cuántas victorias tiene) con el texto de su carta central. No es una opinión: son datos de la muestra.</p>','Cómo se calcula'))+seg;
  const D=ENG.data&&ENG.data.modes[ENG.mode];
  if(!D) return head+'<p class="lede">Cargando…</p></section>';
  const E=D.engines, max=Math.max(...E.map(e=>e.share),1);
  const glance=E.length?`<div class="engstrip">${E.slice(0,10).map(e=>`<span class="pill"><b>${esc(e.n)}</b> ${fmt(e.share)}</span>`).join('')}</div>`:'';
  const row=e=>{ const cid=e.central&&CARDS[e.central]?cardId(e.central):0;
    return `<article class="engcard">${cid?`<img class="engfg" src="${imgUrl(cid,true)}" alt="${esc(e.central)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">`:''}
      <div class="engmain"><h3>${esc(e.n)}</h3>
        <div class="bar" style="--tc:var(--accent)"><span class="track"><span class="fill" style="width:${(e.share/max*100).toFixed(1)}%"></span></span><span class="pct">${fmt(e.share)}</span></div>
        <div class="schips"><i>${e.decks} de ${D.total} decks</i><i>${e.archN} ${e.archN===1?'arquetipo':'arquetipos'}</i>${e.wins?`<i>${e.wins} ${e.wins===1?'victoria':'victorias'}</i>`:''}</div>
        <p class="engwhy">${esc(engWhy(e))}</p>
        ${e.txt?`<p class="engtxt"><b>${esc(e.central)}</b>: «${esc(e.txt)}»</p>`:''}
        ${e.req.length?`<div class="engcards">${e.req.filter(n=>CARDS[n]).map(n=>`<button class="cc" data-card="${esc(n)}">${thumb(n)}<span class="n">${esc(n)}</span></button>`).join('')}</div>`:''}</div></article>`; };
  let extra='';
  if(ENG.mode==='speed'||ENG.mode==='rush'){
    const sh=engShared();
    extra=`${secHead('Cartas que se repiten entre mazos',`En Duel Links, Duel Links Meta define pocos motores. Estas son las cartas que juegan al menos 3 arquetipos distintos del ranking (en la mitad o más de sus listas): el equivalente a un motor compartido.`)}
      <div class="cgrid">${sh.map(e=>`<button class="cc" data-card="${esc(e.n)}">${thumb(e.n)}<span class="n">${esc(e.n)}<b>${e.a.length} arquetipos</b></span></button>`).join('')}</div></section>
      ${ENG.mode==='speed'?`${secHead('Paquetes compartidos, a mano','Combinaciones que se ven en las recetas, analizadas a mano.')}${enginesTable(DL_ENGINES)}</section>`:''}`;
  } else if(ENG.mode==='tcg'){
    extra=`${secHead('Combinaciones a mano','Motores que cruzan arquetipos, analizados a mano el 21 de octubre. La última columna dice dónde más funciona cada uno.')}${enginesTable(TCG_ENGINES)}</section>`;
  }
  return head+`${glance}<p class="lede" style="margin-top:var(--s3)">${E.length?`${E.length} motores en ${fmtNum(D.total)} decks entre el ${dmy(D.window[0])} y el ${dmy(D.window[1])}.`:'Duel Links Meta no define motores para este modo.'}</p>
    <div class="englist">${E.map(row).join('')}</div></section>${extra}`;
}

/* ---------- BANLIST ---------- */''')
rep(".fmtbar{margin:var(--s4) 0 0}", """.fmtbar{margin:var(--s4) 0 0}
.engstrip{display:flex;flex-wrap:wrap;gap:var(--s2);margin:var(--s3) 0}
.engstrip .pill b{font-weight:700}
.englist{display:grid;gap:var(--s3)}
.engcard{position:relative;display:flex;gap:var(--s4);align-items:flex-start;padding:var(--s4);border:1px solid var(--line);border-radius:var(--r);background:linear-gradient(115deg,color-mix(in srgb,var(--accent) 9%,var(--surface)),var(--surface) 60%);overflow:hidden}
.engfg{flex:none;width:96px;aspect-ratio:59/86;object-fit:cover;border-radius:7px;rotate:-4deg;box-shadow:0 14px 26px -10px #000,0 0 0 1px rgba(255,255,255,.2);transition:rotate .4s}
.engcard:hover .engfg{rotate:0deg}
.engmain{display:grid;gap:var(--s2);min-width:0;flex:1}
.engmain h3{font:800 1.15rem var(--f-display);letter-spacing:-.01em}
.engwhy{margin:0;color:var(--fg)}
.engtxt{margin:0;color:var(--muted);font-size:.84rem}
.engtxt b{color:var(--fg)}
.engcards{display:flex;flex-wrap:wrap;gap:var(--s2)}
@media(max-width:620px){.engfg{width:64px}}""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 37 ok')
