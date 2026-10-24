"""Ronda 4: retrato de personajes, íconos de tickets (Speed/Rush), versiones de cada carta con la foto de TCGplayer, sección Eventos (Duel Links,
TCG y Genesys), ícono de Duel Links. Backup: src.before_patch19.html."""
import shutil
shutil.copy('src.html', 'src.before_patch19.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- Duel Links icon (app artwork as line art) ----------
a = s.index('<svg class="glyph" viewBox="0 0 48 48" aria-hidden="true"><defs><linearGradient id="dlg"')
b = s.index('</svg>', a) + len('</svg>')
s = s[:a] + '<span class="glyph dlicon" aria-hidden="true"></span>' + s[b:]

# ---------- new tool tab ----------
rep("""<button class="tool" role="tab" id="tab-ban" data-mode="ban">""", """<button class="tool" role="tab" id="tab-ev" data-mode="ev"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 10 H20.5 M8 3 V7 M16 3 V7 M8 14 H10 M13 14 H16"/></svg>Eventos</button>
    <button class="tool" role="tab" id="tab-ban" data-mode="ban">""")
rep("body.ex,body.sets,body.ban{--accent:var(--ac-tool)}", "body.ex,body.sets,body.ban,body.ev{--accent:var(--ac-tool)}")
rep("const MODES = {tcg:['TCG',viewTCG],gen:['Genesys',viewGEN],dl:['Duel Links',viewDL],ex:['Cartas',viewEX],sets:['Cajas y sets',viewSets],deck:['Constructor',viewDeck],guide:['Guía',viewGuide],ban:['Banlist',viewBan]};",
    "const MODES = {tcg:['TCG',viewTCG],gen:['Genesys',viewGEN],dl:['Duel Links',viewDL],ex:['Cartas',viewEX],sets:['Cajas y sets',viewSets],deck:['Constructor',viewDeck],guide:['Guía',viewGuide],ev:['Eventos',viewEv],ban:['Banlist',viewBan]};")
rep("(DBINFO||!['ex','sets','ban','deck','guide'].includes(mode))", "(DBINFO||!['ex','sets','ban','deck','guide','ev'].includes(mode))")
rep("  SETS.loading=false; if(mode==='sets') render(SETS.focusQ);", "  SETS.loading=false; if(mode==='sets'||mode==='ev') render(SETS.focusQ);")

# ---------- portraits of characters, ticket icons, Speed/Rush ----------
rep("""function boxMedia(s,fmt,rep){
  const u=boxUrl(s,fmt);
  return fmt==='tcg'""", """const TICKET = [   // íconos propios (no hay imágenes oficiales de los tickets en ninguna fuente): [expresión del nombre, color A, color B, texto]
  [/UR Tickets/,'#b69bff','#5fd4ff','UR'],[/SR Tickets/,'#ffe58a','#ffb93b','SR'],[/Acquirable with Tickets/,'#c9d3f5','#7f96d8','N·R'],
  [/Ranked/,'#7fb2ff','#3a63d6','★'],[/Anniversary/,'#ffe58a','#e09a2a','1º'],[/Gift|Campaign/,'#8ff0b8','#2fb36f','🎁'],
  [/Card Trader/,'#7ff0e0','#2aa6a0','⇄'],[/Mission|Bingo|Lifetime/,'#ffc48a','#e0763a','✔'],[/Special Set/,'#ff9bd2','#c45ad0','★'],[/Event|Tournament|Grand Prix|Scramble|Quest|Chronicles|Carnival|Circuit/,'#a9c7ff','#5b7fe0','⚑']
];
function ticketIcon(name){
  const t=TICKET.find(x=>x[0].test(name))||[0,'#d6dcf0','#8a93b6','✦'], id='tk'+(name||'').replace(/[^a-z0-9]/gi,'').slice(0,18);
  return `<svg viewBox="0 0 96 64" role="img" aria-label="${esc(name||'Ticket')}"><defs><linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${t[1]}"/><stop offset="1" stop-color="${t[2]}"/></linearGradient></defs>
    <g transform="rotate(-8 48 32)"><path d="M10 12h76a4 4 0 0 1 4 4v8a8 8 0 0 0 0 16v8a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4v-8a8 8 0 0 0 0-16v-8a4 4 0 0 1 4-4z" fill="url(#${id})" stroke="rgba(255,255,255,.55)" stroke-width="1.5"/>
    <path d="M30 14v36" stroke="rgba(0,0,0,.28)" stroke-width="1.5" stroke-dasharray="3 3"/><text x="60" y="39" text-anchor="middle" font-family="Unbounded,Arial Black,sans-serif" font-weight="800" font-size="${t[3].length>2?15:19}" fill="#10132e">${t[3]}</text></g></svg>`;
}
function boxMedia(s,fmt,rep){
  const u=boxUrl(s,fmt);
  if(fmt==='dl'&&s.kind==='other') return `<span class="spack tk">${ticketIcon(s.n)}</span>`;
  if(fmt==='dl'&&s.kind==='char'&&u) return `<span class="spack char"><img src="${u}" alt="" loading="lazy" decoding="async" referrerpolicy="no-referrer" onerror="this.parentNode.remove()"></span>${boxArt(rep)}`;
  return fmt==='tcg'""")
rep("""const hero=`<div class="sethero${fmt==='tcg'?' pack':''}">""", """const hero=`<div class="sethero${fmt==='tcg'||sel.kind!=='set'?' pack':''}">""")
rep("const SETS = {fmt:'tcg',q:'',sel:null,", "const SETS = {fmt:'tcg',rush:false,q:'',sel:null,")
rep("let list=data.filter(s=>(fmt==='tcg'||s.kind===SETS.kind)&&(!q||matchText(q,s.n)));", "let list=data.filter(s=>(fmt==='tcg'||s.kind===SETS.kind)&&(fmt==='tcg'||SETS.kind!=='other'||!!s.rush===SETS.rush)&&(!q||matchText(q,s.n)));")
rep("let sel=data.find(s=>s.n===SETS.sel&&(fmt==='tcg'||s.kind===SETS.kind))||null;", "let sel=data.find(s=>s.n===SETS.sel&&(fmt==='tcg'||s.kind===SETS.kind)&&(fmt==='tcg'||SETS.kind!=='other'||!!s.rush===SETS.rush))||null;")
rep("""${fmt==='dl'?`<div class="seg" role="group" aria-label="Tipo">${Object.keys(KIND_ES).map(k=>`<button data-skind="${k}" aria-pressed="${SETS.kind===k}">${KIND_ES[k]}</button>`).join('')}</div>`:''}`;""",
    """${fmt==='dl'?`<div class="seg" role="group" aria-label="Tipo">${Object.keys(KIND_ES).map(k=>`<button data-skind="${k}" aria-pressed="${SETS.kind===k}">${KIND_ES[k]}</button>`).join('')}</div>`:''}
    ${fmt==='dl'&&SETS.kind==='other'?`<div class="seg" role="group" aria-label="Modo"><button data-srush="0" aria-pressed="${!SETS.rush}">Speed Duel</button><button data-srush="1" aria-pressed="${SETS.rush}">Rush Duel</button></div>`:''}`;""")
rep("  else if(d.sclose){ SETS.card=null; render(); }", "  else if(d.sclose){ SETS.card=null; render(); }\n  else if(d.srush){ SETS.rush=d.srush==='1'; SETS.sel=null; SETS.card=null; SETS.cl=SCL; render(); }")
# character skills below the hero of a character
rep("""    mid=`<div class="detail sbox">${hero}""", """    const info=fmt==='dl'&&sel.kind==='char'?charInfo(sel.n):'';
    mid=`<div class="detail sbox">${hero}${info}""")

# ---------- versions of a card (TCGplayer pictures) ----------
rep("function tcgBlock(n,d,inSet){", r'''const VERS={all:false};
function versionsBlock(n,d){
  if(!d.pn||!d.pn.length) return '';
  const rows=[...d.pn].sort((a,b)=>rarRank(b[2],'tcg')-rarRank(a[2],'tcg')||(TCGSETS[b[0]][1]||'').localeCompare(TCGSETS[a[0]][1]||''));
  const shown=VERS.all?rows:rows.slice(0,24), cid=mainId(n);
  return `<div class="fmt">Versiones de la carta · ${rows.length} impresiones</div>
    <p class="rnote">Cada versión usa la foto de TCGplayer de esa impresión (Quarter Century, Starlight, Secreta, etc.). Tocá una para verla en grande. Ordenadas de mayor a menor rareza.</p>
    <div class="pvs">${shown.map(p=>{ const set=TCGSETS[p[0]]; return `<button class="pv" data-ver="${p[4]||0}" aria-pressed="false" title="${esc(set[0])}"><span class="art">${cardImg(n,false,'',p[4])}</span><b class="${rchip(p[2],'tcg')}">${esc(p[2])}</b><span class="mini">${esc(RAR_ES[p[2]]||'')}</span><span class="mini">${esc(set[0])}</span><span class="mini">${esc(set[2]?set[2]+'-'+p[1]:p[1])}</span><b class="pp">${p[3]>0?'$'+p[3].toFixed(2):'s/d'}</b></button>`; }).join('')}</div>
    ${rows.length>shown.length?`<p style="text-align:center"><button class="sbtn" data-vall="1">Ver las ${rows.length} versiones</button></p>`:VERS.all&&rows.length>24?`<p style="text-align:center"><button class="sbtn" data-vall="1">Ver menos</button></p>`:''}`;
}
function pickVersion(btn){
  const n=mode==='sets'?SETS.card:EX.card, box=document.querySelector('.bigcard .cf'); if(!box||!n) return;
  const pid=+btn.dataset.ver; let im=box.querySelector('img');
  if(!im){ im=document.createElement('img'); im.alt=n; im.referrerPolicy='no-referrer'; im.onerror=function(){ var a=this.dataset.alt; if(a){ this.removeAttribute('data-alt'); this.src=a; } else this.remove(); }; box.appendChild(im); }
  im.dataset.alt=cardSrc(n,true);
  im.src=pid?`https://product-images.tcgplayer.com/fit-in/437x437/${pid}.jpg`:cardSrc(n,true);
  document.querySelectorAll('[data-ver]').forEach(b=>b.setAttribute('aria-pressed',b===btn));
  box.removeAttribute('data-fo');
}
function tcgBlock(n,d,inSet){''')
rep("  $('#dx-tail').innerHTML=dlBlock(n,d)+tcgBlock(n,d);", "  $('#dx-tail').innerHTML=dlBlock(n,d)+versionsBlock(n,d)+tcgBlock(n,d);")
rep("  $('#sx-tail').innerHTML=tcgBlock(n,d,true);", "  $('#sx-tail').innerHTML=versionsBlock(n,d)+tcgBlock(n,d,true);")
rep("  else if(d.sclose){ SETS.card=null; render(); }", "  else if(d.sclose){ SETS.card=null; render(); }\n  else if(d.ver!==undefined){ pickVersion(b); }\n  else if(d.vall){ VERS.all=!VERS.all; render(); }")

# ---------- Eventos tab ----------
a = s.index('/* ---------- BANLIST ---------- */')
s = s[:a] + r'''/* ---------- EVENTOS Y TORNEOS ---------- */
const EV={fmt:'dl',tab:'events',char:null,cq:'',q:'',all:false};
let DLI=null, EVD=null, evAsked=false;
function loadEv(){
  if(evAsked) return; evAsked=true;
  loadData('dlinfo').then(j=>{ DLI=j; if(mode==='ev'||mode==='sets') render(); }).catch(()=>{});
  loadData('events').then(j=>{ EVD=j; if(mode==='ev') render(); }).catch(()=>{});
}
const HOW=h=>{ const m=/^Level (\d+)$/.exec(h||''); return m?'Nivel '+m[1]:({Drop:'Drop en la Puerta (Gate)','Character Deck':'Character Deck (duelos de personaje)','Starter Deck':'Mazo inicial'}[h]||h||'—'); };
const dmy=d=>{ if(!d) return ''; const [y,m,dd]=d.split('-'); return `${dd}/${m}/${y}`; };
const addDays=(d,n)=>{ const t=new Date(d+'T12:00:00Z'); t.setUTCDate(t.getUTCDate()+n); return t.toISOString().slice(0,10); };
const dayDiff=(a,b)=>Math.round((new Date(b+'T12:00:00Z')-new Date(a+'T12:00:00Z'))/864e5);
function charInfo(name){        // habilidades que da el personaje, con cómo se consiguen
  if(!DLI){ loadEv(); return ''; }
  const c=DLI.chars[name]; if(!c||!c.s.length) return '';
  return `<div class="cinfo"><div class="fmt">Habilidades que da ${esc(name)} · ${c.s.length}</div>${c.s.map(([n,d,how,rush])=>`<div class="use"><span><strong>${esc(n)}</strong> ${rush?'<span class="chip">Rush</span>':''}</span><b>${esc(HOW(how))}</b><p class="eff" style="flex:1 1 100%">${esc(d)}</p></div>`).join('')}</div>`;
}
function evDL(){
  const today=new Date().toISOString().slice(0,10), evs=(DLI.events||[]).filter(e=>e.d);
  const card=(e,tag)=>`<a class="evc" href="https://www.duellinksmeta.com${esc(e.u)}" target="_blank" rel="noopener noreferrer">${e.i?`<img src="https://s3.duellinksmeta.com${e.i.split('/').map(encodeURIComponent).join('/')}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">`:'<span class="evph"></span>'}<span class="evt2"><small>${tag}</small><b>${esc(e.t)}</b><span class="mini">${dmy(e.d)} al ${dmy(e.e)}</span>${e.x?`<span class="evx">${esc(e.x)}</span>`:''}</span></a>`;
  const act=evs.filter(e=>e.d<=today&&e.e>=today).sort((a,b)=>a.e.localeCompare(b.e)), up=evs.filter(e=>e.d>today).sort((a,b)=>a.d.localeCompare(b.d));
  const past=evs.filter(e=>e.e<today).sort((a,b)=>b.e.localeCompare(a.e)), pshown=EV.all?past:past.slice(0,9);
  return `${secHead('Eventos activos ahora',`Eventos del juego con su fecha de inicio y de fin (Duel Links Meta). Hoy es ${dmy(today)}.`)}
    ${act.length?`<div class="evg">${act.map(e=>card(e,`Activo · termina en ${Math.max(0,dayDiff(today,e.e))} ${dayDiff(today,e.e)===1?'día':'días'}`)).join('')}</div>`:'<p class="dkempty">No hay eventos activos hoy en los datos de Duel Links Meta.</p>'}</section>
    ${up.length?`${secHead('Próximos')}<div class="evg">${up.map(e=>card(e,'Empieza en '+dayDiff(today,e.d)+' días')).join('')}</div></section>`:''}
    ${secHead('Eventos terminados')}<div class="evg">${pshown.map(e=>card(e,'Terminó')).join('')}</div>${past.length>pshown.length?`<p style="text-align:center"><button class="sbtn" data-evmore="1">Ver los ${past.length}</button></p>`:''}</section>`;
}
function evChars(){
  const q=EV.cq.trim(), names=Object.keys(DLI.chars).filter(n=>!q||matchText(q,n)).sort((a,b)=>a.localeCompare(b));
  if(!SETS.data.dl) loadSets('dl');
  const sel=EV.char&&DLI.chars[EV.char]?EV.char:names[0];
  let right='<div class="detail"><p>Sin resultados.</p></div>';
  if(sel){
    const c=DLI.chars[sel], src=(SETS.data.dl||[]).find(x=>x.kind==='char'&&x.n===sel);
    let rewards='<p class="rnote">Cargando las cartas…</p>';
    if(src){
      const groups={}; for(const r of src.k){ const g=SUBSRC(r[2]||''); (groups[g[0]+'|'+g[1]]=groups[g[0]+'|'+g[1]]||[]).push([r,g[2]]); }
      rewards=Object.keys(groups).sort((a,b)=>parseInt(a)-parseInt(b)).map(k=>{ const title=k.split('|')[1], rs=groups[k].sort((a,b)=>rarRank(dlRar(NAMES[b[0][0]]),'dl')-rarRank(dlRar(NAMES[a[0][0]]),'dl'));
        return `<div class="fmt">${esc(title)} · ${rs.length}</div><div class="cgrid">${rs.map(([r,det])=>{ const n=NAMES[r[0]]; return `<button class="cc" data-card="${esc(n)}">${thumb(n)}<span class="n">${esc(n)}<b><i class="rr rr-${dlRar(n)}" style="font-style:normal;padding:0 6px;border-radius:99px;color:#10132e">${dlRar(n)}</i> ${esc(det||'')}${r[1]>1?' ×'+r[1]:''}</b></span></button>`; }).join('')}</div>`; }).join('');
    }
    right=`<div class="detail"><div class="hero-card">${c.p?`<span class="cportrait"><img src="https://s3.duellinksmeta.com${c.p}" alt="${esc(sel)}" referrerpolicy="no-referrer"></span>`:''}<div><h3>${esc(sel)}</h3><div class="chips">${c.w.map(w=>`<span class="chip">${esc(w)}</span>`).join('')}</div><p class="eff">Recompensas de cartas por nivel, por la Puerta y por duelos de personaje, y habilidades. Duel Links Meta no publica las gemas de cada nivel, así que no figuran acá.</p></div></div>${rewards}${charInfo(sel)}</div>`;
  }
  return `${secHead('Personajes: recompensas y habilidades',`${Object.keys(DLI.chars).length} personajes. Elegí uno para ver qué cartas da al subir de nivel, en la Puerta y en los duelos de personaje, y las habilidades que enseña.`)}
    <div class="sgrid"><div><div class="filters"><label class="sr" for="evcq">Buscar personaje</label><input id="evcq" type="search" placeholder="Buscar entre ${names.length} personajes" value="${esc(EV.cq)}" autocomplete="off" spellcheck="false"></div>
      <div class="setlist">${names.map(n=>{ const c=DLI.chars[n]; return `<button class="setb" data-evchar="${esc(n)}" aria-pressed="${n===sel}"><span class="spack char">${c.p?`<img src="https://s3.duellinksmeta.com${c.p}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">`:''}</span><span class="stxt"><b>${esc(n)}</b><span class="schips"><i>${esc(c.w.join(' · ')||'—')}</i><i>${c.s.length} habilidades</i></span></span></button>`; }).join('')}</div></div>${right}</div></section>`;
}
function evComp(f){
  const fm=f==='gen'?'Genesys':'TCG', all=(EVD||[]).filter(e=>e.f===fm), q=EV.q.trim();
  const today=new Date().toISOString().slice(0,10), last=all.length?all[0].d:'';
  const list=all.filter(e=>!q||matchText(q,e.n+' '+e.c));
  const live=all.filter(e=>dayDiff(e.d,today)<=1&&dayDiff(e.d,today)>=-1);
  const row=e=>{ const w=e.top[0]; return `<details class="evd"><summary><span class="evn"><b>${esc(e.n)}</b><span class="mini">${dmy(e.d)}${e.c?' · '+esc(e.c):''}${e.p?' · '+e.p.toLocaleString('es-AR')+' jugadores':''}${e.ty?' · '+esc(e.ty):''}</span></span><span class="evw">${w?`<i>1.º</i> ${esc(w[2])} <small>${esc(w[1])}</small>`:'<small>Sin resultados publicados</small>'}</span></summary>
    ${e.top.length?`<div class="tbl"><table class="ptab"><thead><tr><th>Puesto</th><th>Mazo</th><th>Jugador</th><th></th></tr></thead><tbody>${e.top.map(([pl,au,dk,u])=>`<tr><td>${pl===1?'1.º':'Top '+pl}</td><td><strong>${esc(dk)}</strong></td><td>${esc(au)}</td><td>${u?`<a href="https://www.yugiohmeta.com${esc(u)}" target="_blank" rel="noopener noreferrer">ver lista</a>`:''}</td></tr>`).join('')}</tbody></table></div>`:'<p class="rnote">YGOMeta todavía no publicó los mazos de este evento.</p>'}</details>`; };
  return `${secHead(`Torneos de ${fm}`,`Eventos de ${fm} con sus resultados, desde el 20 de agosto de 2026 (YGOMeta). Los datos llegan hasta el ${dmy(last)}: un evento aparece cuando se publican sus resultados, así que lo que está en juego hoy no figura hasta entonces.`)}
    <div class="seg mini" style="margin-top:0"><span class="pill">${all.length} eventos</span><span class="pill">${all.filter(e=>e.top.length).length} con resultados</span></div>
    <h3 style="margin-top:var(--s5)">En curso</h3>${live.length?live.map(row).join(''):`<p class="dkempty">Ningún evento de ${fm} figura en curso hoy (${dmy(today)}) en la fuente. El último con datos es del ${dmy(last)}.</p>`}</section>
    ${secHead('Resultados')}<div class="filters"><label class="sr" for="evq">Buscar evento</label><input id="evq" type="search" placeholder="Buscar por nombre o país" value="${esc(EV.q)}" autocomplete="off" spellcheck="false"></div>
    <div class="evl">${list.slice(0,EV.all?9999:30).map(row).join('')}</div>${list.length>30&&!EV.all?`<p style="text-align:center"><button class="sbtn" data-evmore="1">Ver los ${list.length}</button></p>`:''}</section>`;
}
function viewEv(){
  loadEv();
  const seg=`<div class="seg" role="group" aria-label="Juego">${[['dl','Duel Links'],['tcg','TCG'],['gen','Genesys']].map(([k,t])=>`<button data-evfmt="${k}" aria-pressed="${EV.fmt===k}">${t}</button>`).join('')}</div>
    ${EV.fmt==='dl'?`<div class="seg" role="group" aria-label="Sección"><button data-evtab="events" aria-pressed="${EV.tab==='events'}">Eventos del juego</button><button data-evtab="chars" aria-pressed="${EV.tab==='chars'}">Personajes y habilidades</button></div>`:''}`;
  const head=pageHead('Eventos y torneos','Duel Links: eventos activos del juego y lo que da cada personaje. TCG y Genesys: torneos con sus resultados.')+seg+'</section>';
  const need=EV.fmt==='dl'?!DLI:!EVD;
  if(need) return head+'<p class="lede">Cargando…</p>';
  return head+(EV.fmt==='dl'?(EV.tab==='chars'?evChars():evDL()):evComp(EV.fmt));
}

''' + s[a:]
# handlers
rep("  else if(d.sclose){ SETS.card=null; render(); }", "  else if(d.sclose){ SETS.card=null; render(); }\n  else if(d.evfmt){ EV.fmt=d.evfmt; EV.all=false; render(); }\n  else if(d.evtab){ EV.tab=d.evtab; render(); }\n  else if(d.evchar){ EV.char=d.evchar; render(); }\n  else if(d.evmore){ EV.all=true; render(); }")
rep("  else if(id==='bq'){ BAN.q=e.target.value; ensureES('bq'); render('bq'); }", "  else if(id==='bq'){ BAN.q=e.target.value; ensureES('bq'); render('bq'); }\n  else if(id==='evq'){ EV.q=e.target.value; render('evq'); }\n  else if(id==='evcq'){ EV.cq=e.target.value; render('evcq'); }")

# ---------- css ----------
rep("</style>\n\n<div class=\"sideart", """.dlicon{position:relative;display:block;border-radius:13px;border:2px solid var(--mc);overflow:hidden;background:linear-gradient(150deg,color-mix(in srgb,var(--mc) 22%,var(--surface2)),var(--surface2));box-shadow:0 0 14px -4px var(--mc);filter:none!important}
.dlicon::before{content:"";position:absolute;inset:0;background:var(--mc);-webkit-mask:url(/*__LINE_DL__*/art/line-dl.png) center top/cover no-repeat;mask:url(/*__LINE_DL__*/art/line-dl.png) center top/cover no-repeat}
.spack.tk{width:96px;max-width:40%}
.spack.tk svg{width:100%;height:auto;filter:drop-shadow(0 6px 8px rgba(0,0,0,.4))}
.spack.char img{height:100%;width:auto;max-width:96px;object-fit:contain;object-position:center bottom;filter:drop-shadow(0 6px 10px rgba(0,0,0,.45))}
.sethero.pack .spack.tk{width:170px;max-width:none;height:auto}
.setb .spack.char,.setb .spack.tk{right:10px}
.pv[aria-pressed="true"]{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.cinfo{display:grid;gap:var(--s2)}
.cportrait{flex:none;width:130px;border-radius:var(--r2);overflow:hidden;border:2px solid var(--accent);background:var(--surface2)}
.cportrait img{display:block;width:100%;height:auto}
.evg{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:var(--s3);margin-top:var(--s3)}
.evc{display:grid;grid-template-columns:128px minmax(0,1fr);gap:var(--s3);padding:var(--s2);border-radius:var(--r);border:1px solid var(--line2);background:linear-gradient(150deg,color-mix(in srgb,var(--accent) 9%,var(--surface)),var(--surface));text-decoration:none;color:var(--fg);align-items:stretch;transition:border-color .15s,transform .15s}
.evc:hover{border-color:var(--accent);transform:translateY(-2px)}
.evc img,.evph{width:100%;height:100%;min-height:84px;object-fit:cover;border-radius:var(--r2);background:var(--surface2)}
.evt2{display:grid;gap:3px;align-content:start;min-width:0}
.evt2 small{font:600 .66rem var(--f-data);letter-spacing:.08em;text-transform:uppercase;color:var(--accent)}
.evt2 b{font:700 .95rem var(--f-display);line-height:1.2;overflow-wrap:anywhere}
.evx{font-size:.8rem;color:var(--muted);display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.evl{display:grid;gap:var(--s2);margin-top:var(--s3)}
.evd{border:1px solid var(--line2);border-radius:var(--r2);background:var(--surface);margin-top:var(--s2)}
.evd > summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;gap:var(--s4);align-items:center;flex-wrap:wrap;padding:var(--s3) var(--s4)}
.evd > summary::-webkit-details-marker{display:none}
.evn{display:grid;gap:2px;min-width:0}
.evn b{font:700 .95rem var(--f-display);overflow-wrap:anywhere}
.evw{font-size:.9rem}
.evw i{font-style:normal;font:700 .72rem var(--f-data);color:var(--t1);margin-right:4px}
.evw small{color:var(--muted)}
.evd .tbl{margin:0 var(--s4) var(--s4)}
.evd > p{margin:0 var(--s4) var(--s4)}
</style>

<div class=\"sideart""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch19 ok')
