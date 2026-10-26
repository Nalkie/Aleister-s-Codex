"""Pestaña Tickets: qué se puede sacar con los Dream UR / SR (Speed y Rush) y con los tickets normales UR / SR / R (cartas farmeables).
Los datos salen de data/tickets.js (tools/tickets.py). Backup: src.before_patch24.html."""
import shutil
shutil.copy('src.html', 'src.before_patch24.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep('''Banlist</button>''', '''Banlist</button>
    <button class="tool" role="tab" id="tab-tk" data-mode="tk"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 7.5h17v3a2 2 0 0 0 0 3v3h-17v-3a2 2 0 0 0 0-3z"/><path d="M9 7.5v9" stroke-dasharray="2 2"/></svg>Tickets</button>''')
rep(",ban:['Banlist',viewBan]};", ",ban:['Banlist',viewBan],tk:['Tickets',viewTickets]};")
rep("!['ex','sets','ban','deck','guide','ev'].includes(mode)", "!['ex','sets','ban','deck','guide','ev','tk'].includes(mode)")
rep("  else if(d.evfmt){", """  else if(d.tkk){ TK.kind=d.tkk; TK.r=d.tkk==='dream'&&TK.r==='R'?'UR':TK.r; TK.limit=80; render(); }
  else if(d.tkm){ TK.mode=d.tkm; TK.limit=80; render(); }
  else if(d.tkr){ TK.r=d.tkr; TK.limit=80; render(); }
  else if(d.tkmore){ TK.limit+=120; render(); }
  else if(d.evfmt){""")
rep("  else if(id==='evq'){", "  else if(id==='tkq'){ TK.q=e.target.value; TK.limit=80; render('tkq'); }\n  else if(id==='evq'){")
rep("/* ---------- BANLIST ---------- */", r'''/* ---------- TICKETS ---------- */
const TK = {kind:'dream',mode:'speed',r:'UR',q:'',limit:80,data:null,asked:false};
function viewTickets(){
  if(!TK.asked){ TK.asked=true; loadData('tickets').then(j=>{ TK.data=j; if(mode==='tk') render(); }).catch(()=>{ TK.asked=false; }); }
  const d=TK.data, dream=TK.kind==='dream', rar=dream?['UR','SR']:['UR','SR','R'], r=rar.includes(TK.r)?TK.r:'UR';
  const seg=(attr,cur,items)=>`<div class="seg" role="group">${items.map(([k,t])=>`<button data-${attr}="${k}" aria-pressed="${cur===k}">${t}</button>`).join('')}</div>`;
  const dmyc=x=>x?dmy(x):'';
  const cut=d?(dream?`Speed Duel: cartas de cajas hasta <b>${esc(d.cuts.speedSet)}</b> (${dmyc(d.cuts.speed)}) · Rush Duel: cartas de cajas hasta <b>${esc(d.cuts.rushSet)}</b> (${dmyc(d.cuts.rush)})`:`Cartas que se consiguen jugando (niveles de personaje, Puerta, mazos de personaje, eventos y misiones) hasta el <b>${dmyc(d.cuts.farm)}</b>`):'';
  const head=pageHead('Tickets: qué se puede sacar',dream?'Con un Dream UR o un Dream SR elegís cualquier carta de esa rareza del conjunto de cajas que entra en el ticket. Hay un conjunto para Speed Duel y otro para Rush Duel.':'Los tickets UR, SR y R normales (por ejemplo los del modo Ranked) se canjean por cartas que se pueden farmear, no por cartas que solo salen de cajas.','',`<div class="note">${cut||'Cargando…'}<br>Los cortes los fijó el dueño del proyecto según las reglas del juego: ninguna fuente pública los publica. Se cambian en <code>tools/tickets.py</code>.</div>`)
    +`<div class="tkhead">${tkSvg(r,r,dream?(TK.mode==='rush'?2:1):0)}<div class="tkseg">${seg('tkk',TK.kind,[['dream','Dream (de ensueño)'],['farm','Normales (farmeables)']])}${seg('tkm',TK.mode,[['speed','Speed Duel'],['rush','Rush Duel']])}${seg('tkr',r,rar.map(x=>[x,(dream?'Dream ':'')+x]))}</div></div>`;
  if(!d) return head+'<p class="lede">Cargando…</p>';
  const all=(dream?d.dream:d.farm)[TK.mode][r]||[], q=TK.q.trim(), list=all.filter(n=>!q||matchText(q,n));
  return head+`<div class="filters"><label class="sr" for="tkq">Buscar carta</label><input id="tkq" type="search" placeholder="Buscar entre ${all.length.toLocaleString('es-AR')} cartas" value="${esc(TK.q)}" autocomplete="off" spellcheck="false"></div>
    <p class="lede">${list.length.toLocaleString('es-AR')} cartas ${r} ${dream?'de Dream ':''}en ${TK.mode==='rush'?'Rush Duel':'Speed Duel'}, de la más nueva a la más vieja. Tocá una para ver cómo conseguirla.</p>
    <div class="gal tkgal">${list.slice(0,TK.limit).map(n=>`<button class="tile ptile" data-card="${esc(n)}" title="${esc(n)}"><span class="art">${cardImg(n,false,'')}</span><span class="tn">${esc(n)}</span><span class="tm"><b class="rr rr-${r}">${r}</b></span><span class="mini">${esc(dlRel(n)||'')}</span></button>`).join('')}</div>
    ${list.length>TK.limit?`<p style="text-align:center"><button class="sbtn" data-tkmore="1">Ver más (${(list.length-TK.limit).toLocaleString('es-AR')})</button></p>`:''}</section>`;
}

/* ---------- BANLIST ---------- */''')
rep(".cportrait img{display:block;width:100%;height:auto}", """.cportrait img{display:block;width:100%;height:auto}
.tkhead{display:flex;align-items:center;gap:var(--s4);flex-wrap:wrap;margin:var(--s4) 0}
.tkhead svg{width:150px;flex:none;filter:drop-shadow(0 8px 12px rgba(0,0,0,.45))}
.tkseg{display:grid;gap:var(--s2)}
.tkgal{grid-template-columns:repeat(auto-fill,minmax(112px,1fr))}""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 24 ok')
