"""Patch src.html: card database loaded from data/*.json, banlist per format, DL box ordering,
TCG printings, box/set explorer and a banlist tab. Run once from build/ (src.html is backed up first)."""
import re, shutil

shutil.copy('src.html', 'src.before_patch2.html')
s = open('src.html', encoding='utf-8').read()


def sub_between(start, end, repl, include_end=False):
    """Replace s[start .. end) (or through end) with repl."""
    global s
    i = s.index(start)
    j = s.index(end, i + len(start))
    if include_end:
        j += len(end)
    s = s[:i] + repl + s[j:]


def rep(old, new, count=1):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, count)


# ---------- header / nav ----------
rep('<button class="tab" role="tab" id="tab-ex" data-mode="ex">Buscador de cartas</button>',
    '<button class="tab" role="tab" id="tab-ex" data-mode="ex">Buscador de cartas</button>\n  <button class="tab" role="tab" id="tab-sets" data-mode="sets">Cajas y sets</button>\n  <button class="tab" role="tab" id="tab-ban" data-mode="ban">Banlist</button>')

# ---------- css ----------
rep(".th{display:block;width:var(--sz,42px);height:var(--sz,42px);flex:none;background-size:800% 800%;",
    ".th{display:block;width:var(--sz,42px);height:var(--sz,42px);flex:none;background-size:900% 900%;")
rep(".ph{display:grid;place-items:center;font:700 .9rem var(--f-display);color:var(--muted)}",
    ".ph{display:grid;place-items:center;font:700 .9rem var(--f-display);color:var(--muted)}\n.k-s{background:#0b6e5b55}.k-t{background:#8a2a6a55}.k-e{background:#5b3fb555}.k-m{background:#9a6b2a44}")
css_add = """
.lims{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
.lim{border:1px solid var(--line);background:var(--surface2);padding:6px 10px}
.lim small{display:block;font:500 .7rem var(--f-data);letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.lim b{font:700 1.05rem var(--f-display);letter-spacing:.03em}
.lim.hot{border-color:var(--red)} .lim.hot b{color:var(--red)}
.src{display:flex;gap:8px;align-items:baseline;flex-wrap:wrap;border-bottom:1px dashed var(--line);padding:5px 0;font-size:.92rem}
.src b{font:500 .8rem var(--f-data);color:var(--accent)}
.src .new{font:500 .7rem var(--f-data);background:var(--accent);color:var(--bg);padding:0 6px}
.lnk{background:none;border:0;padding:0;cursor:pointer;color:var(--accent);text-align:left;text-decoration:underline;text-decoration-color:var(--line)}
.mini{font:500 .68rem var(--f-data);color:var(--muted)}
.mini i{font-style:normal;color:var(--red)}
.ptab{width:100%;border-collapse:collapse;font-size:.85rem;min-width:0}
.ptab td,.ptab th{padding:4px 8px}
.setlist{max-height:620px;overflow:auto;display:grid;gap:4px}
.setb{display:flex;justify-content:space-between;gap:8px;text-align:left;background:var(--surface);border:1px solid var(--line);padding:6px 10px;cursor:pointer}
.setb[aria-pressed="true"]{border-color:var(--accent);box-shadow:0 0 12px var(--glow)}
.setb small{font:500 .72rem var(--f-data);color:var(--muted);white-space:nowrap}
.bgrp{margin-top:18px}
.bgrp h3{font-size:1.1rem;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin-bottom:8px}
"""
rep("footer{margin-top:56px", css_add + "footer{margin-top:56px")
rep("@media(max-width:760px){\n  .exg{grid-template-columns:1fr}", "@media(max-width:760px){\n  .lims{grid-template-columns:1fr}\n  .exg{grid-template-columns:1fr}")

# ---------- globals: CARDS from data/index.json ----------
rep("const CARDS = /*__CARDS__*/{};          // nombre -> [hoja, celda, tipo, baneo TCG, staple, texto]",
    "const CARDS = {};                        // nombre -> [tipo, hoja, celda, límite TCG, límite DL, puntos Genesys, chunk, banderas, precio]\nconst C = {CAT:0,SH:1,CE:2,BAN:3,DL:4,GEN:5,CH:6,FL:7,PR:8};\nlet NAMES = [], TCGSETS = [], DBINFO = null;")
rep("const COLS = 8;\n", "const COLS = 9;\n")

# ---------- thumb ----------
sub_between("function thumb(n){", "function cardChips(cards)", '''function thumb(n){
  const c=CARDS[canon(n)];
  if(!c||c[C.SH]<0) return `<span class="th ph k-${c?c[C.CAT]:'m'}">${esc(initials(n))}</span>`;
  const x=(c[C.CE]%COLS)/(COLS-1)*100, y=Math.floor(c[C.CE]/COLS)/(COLS-1)*100;
  return `<span class="th" style="background-image:url(sheets/s${c[C.SH]}.jpg);background-position:${x.toFixed(2)}% ${y.toFixed(2)}%"></span>`;
}
''')

# ---------- DL badge: boxes ordered, no static info block ----------
sub_between("function dlBadge(n){", "/* ---------- ÍNDICE CARTA", '''const SEL_RE = /Selection/;
const PACK_RE = /^(Main Box|Mini Box|Deck Build Box|Pickup Box)$/;
const PAID = /^Structure|Selection/;
function srcOrder(sets){   // cajas "normales" primero y la más nueva adelante; luego estructuras; luego cajas de selección
  const grp = t => PACK_RE.test(t||'') ? 0 : /^Structure/.test(t||'') ? 1 : 2;
  return [...sets].sort((a,b)=>grp(a[2])-grp(b[2]) || (b[4]||'').localeCompare(a[4]||''));
}
function dlBadge(n){
  const i=DLD.cards[n]; if(!i) return '';
  if(i.c.length) return 'Gratis · personaje';
  const free=i.o.filter(([nm])=>nm&&!TICKETS.has(nm)&&!TRADERS.has(nm)&&nm!=='Special Set'&&/Event|Missions|Ranked|Respect|Campaign|Gift/.test(nm));
  if(free.length) return 'Gratis · evento';
  const ss=srcOrder(i.s.map(([nm,t,k,rel])=>[null,nm,t,k,rel||'']));
  if(ss.length && PACK_RE.test(ss[0][2]||'')) return 'Paquete';
  if(i.o.some(([nm])=>nm==='Acquirable with UR Tickets')) return 'Ticket UR';
  if(i.o.some(([nm])=>nm==='Acquirable with SR Tickets')) return 'Ticket SR';
  if(i.o.some(([nm])=>TICKETS.has(nm))) return 'Tickets';
  if(ss.length && /^Structure/.test(ss[0][2]||'')) return 'Estructura';
  if(ss.length) return 'Caja de selección';
  if(i.o.some(([nm])=>TRADERS.has(nm))) return 'Card Trader';
  return 'Especial';
}
function dlBadgeTitle(n){
  const i=DLD.cards[n]; if(!i) return '';
  const ss=srcOrder(i.s.map(([nm,t,k,rel])=>[null,nm,t,k,rel||'']));
  return ss.length ? 'Caja más reciente: '+ss[0][1]+(ss[0][4]?' ('+ss[0][4]+')':'') : '';
}

''')

# ---------- decklist rows ----------
sub_between("function rowExtra(kind,n,pr){", "function tbl(head,rows)", '''function banMark(n,kind){
  const c=CARDS[canon(n)]; if(!c) return '';
  if(kind==='tcg'){ const b=c[C.BAN]; return b>=0&&b<3?`<u class="bdg" title="Banlist TCG" style="color:var(--red)">${b===0?'Prohibida':'Límite '+b}</u>`:''; }
  if(kind==='dl'){ const d=c[C.DL]; return d>=1&&d<=3?`<u class="bdg" title="Lista de prohibidas de Duel Links" style="color:var(--red)">Límite ${d}</u>`:''; }
  if(kind==='gen'){ const g=c[C.GEN]; return g>0?`<u class="bdg" title="Puntos Genesys">${g} pts</u>`:g===-1?'<u class="bdg" title="Carta reciente: puntos sin confirmar">? pts</u>':''; }
  return '';
}
function rowExtra(kind,n,pr){
  if(kind==='dl'){ const i=DLD.cards[n]; return `<span class="ex">${i&&i.r?`<em class="rar">${esc(i.r)}</em>`:''}${pr!=null?`<i class="pr">${pr}%</i>`:''}${banMark(n,'dl')}<u class="bdg" title="${esc(dlBadgeTitle(n))}">${esc(dlBadge(n))}</u></span>`; }
  const c=CARDS[canon(n)]; const pr$=c&&c[C.PR]>0?`<i class="pr">$${c[C.PR]}</i>`:'';
  return `<span class="ex">${banMark(n,kind)}${kind==='gen'?'':pr$}</span>`;
}
function decklist(l,kind='tcg'){
  const sec=(t,arr)=>{ if(!arr.length) return ''; const tot=arr.reduce((a,x)=>a+x[1],0);
    return `<div class="dsec"><h4>${t} · ${tot} cartas</h4><div class="dcol">${arr.map(([n,k,pr])=>`<button class="drow" data-card="${esc(n)}"><b>${k}</b>${thumb(n)}<span class="nm">${esc(n)}</span>${rowExtra(kind,n,pr)}</button>`).join('')}</div></div>`; };
  let cost='';
  if(kind==='dl'){
    cost=`<p class="cost"><strong>Costo estimado de esta lista (Duel Links Meta):</strong> ${l.gems!=null?fmtNum(l.gems)+' gemas':'sin dato'}${l.usd?' + US$ '+l.usd+' de dinero real':' (sin gasto de dinero real)'}.
      Mediana de los ${l.n} decks del arquetipo: ${l.gemsMed!=null?fmtNum(l.gemsMed)+' gemas':'sin dato'}${l.usdMed?' + US$ '+l.usdMed:''}. Skill: ${esc(l.skill||'sin skill')}. Las marcas en rojo son cartas de la lista de prohibidas de Duel Links.</p>`;
  } else if(kind==='gen'){
    let t=0,unk=0; for(const s of ['main','extra','side']) for(const [n,k] of l[s]){ const c=CARDS[canon(n)]; if(!c) continue; const g=c[C.GEN]; if(g>0) t+=g*k; else if(g===-1) unk+=k; }
    cost=`<p class="cost"><strong>Puntos Genesys de esta lista:</strong> ${t}${unk?` + ${unk} cartas con puntos sin confirmar`:''} (tope del formato: 100). Calculado con la lista de puntos del 5 oct 2026; cada carta muestra los suyos a la derecha.</p>`;
  } else {
    let t=0,miss=0; for(const s of ['main','extra','side']) for(const [n,k] of l[s]){ const c=CARDS[canon(n)]; if(c&&c[C.PR]>0) t+=c[C.PR]*k; else miss+=k; }
    cost=`<p class="cost"><strong>Valor aproximado:</strong> US$ ${t.toFixed(0)} en TCGplayer${miss?` (sin precio para ${miss} cartas)`:''}. Precio por carta a la derecha; las marcas en rojo son cartas de la banlist del TCG.</p>`;
  }
  return `<div class="recipe"><h3>Receta ${kind==='dl'?'más usual':'de referencia'}</h3><p class="lede" style="margin:0 0 6px">${esc(l.who)}</p>${cost}<div class="decklist">${sec('Main Deck',l.main)}${sec('Extra Deck',l.extra)}${sec('Side Deck',l.side)}</div></div>`;
}
''')
rep("${d.list?decklist(d.list,'tcg'):'<p>Sin lista publicada en las fuentes leídas.</p>'}", "${d.list?decklist(d.list,'gen'):'<p>Sin lista publicada en las fuentes leídas.</p>'}")

# ---------- explorer, sets and banlist views + routing ----------
NEW_TAIL = r'''/* ---------- BANLIST POR FORMATO ---------- */
function limitText(n){
  const c=CARDS[n]; if(!c) return {};
  const b=c[C.BAN], d=c[C.DL], g=c[C.GEN];
  return {
    tcg: b<0?'No existe en el TCG':b===0?'Prohibida (0)':'Límite '+b,
    dl: d<0?'No existe en Duel Links':'Límite '+(d===4?3:d),
    gen: g===-2?'No existe en Genesys':g===-1?'Puntos sin confirmar':g===0?'Cuesta 0':'Cuesta '+g,
    hot:{tcg:b>=0&&b<3, dl:d>=1&&d<=3, gen:g>0}
  };
}
function limitChips(n){
  const t=limitText(n);
  return `<div class="lims"><div class="lim ${t.hot.tcg?'hot':''}"><small>TCG</small><b>${esc(t.tcg)}</b></div><div class="lim ${t.hot.dl?'hot':''}"><small>Duel Links</small><b>${esc(t.dl)}</b></div><div class="lim ${t.hot.gen?'hot':''}"><small>Genesys</small><b>${esc(t.gen)}</b></div></div>`;
}
function miniLims(n){
  const c=CARDS[n], b=c[C.BAN], d=c[C.DL], g=c[C.GEN];
  const f=(v,hot)=>hot?`<i>${v}</i>`:v;
  return `<span class="mini" title="Límite en TCG · Duel Links · puntos Genesys">TCG ${b<0?'–':f(b,b<3)} · DL ${d<0?'–':f(d===4?3:d,d>=1&&d<=3)} · GEN ${g>0?f(g,true):g===-1?'?':'–'}</span>`;
}

/* ---------- BUSCADOR ---------- */
const EX = {view:'card',card:'Droll & Lock Bird',fmt:'tcg',strat:'branded',q:'',type:'all',fm:'all',meta:false,limit:60,allPrints:false};
let USEDN = {};
const usedCount = n => USEDN[n]||0;
function computeUsed(){ USEDN={}; for(const f in INDEX) for(const n in INDEX[f].byCard) USEDN[n]=(USEDN[n]||0)+INDEX[f].byCard[n].length; }
const DETAIL = {};
async function getDetail(n){
  const ch=CARDS[n][C.CH];
  if(!DETAIL[ch]) DETAIL[ch]=fetch('data/c'+ch+'.json').then(r=>{ if(!r.ok) throw new Error(r.status); return r.json(); });
  const all=await DETAIL[ch]; return all[n]||{};
}
function useRows(uses){
  return uses.map(u=>`<div class="use"><span><strong>${esc(u.s.name)}</strong> <span class="chip">${u.s.kind}${u.s.tier&&TIERS[u.s.tier]&&u.s.tier[0]==='T'?' · '+TIERS[u.s.tier][1]:''}</span></span>
   <b>${u.p!=null?u.p+'% de sus listas':''}${u.k?(u.p!=null?' · ':'')+u.k.join(', '):''}${u.p==null&&!u.k?'en su lista':''}</b>
   ${u.s.works?`<div class="tags"><span>También funciona en:</span>${u.s.works.map(w=>`<span>${esc(w)}</span>`).join('')}</div>`:''}</div>`).join('');
}
function cardDetail(n){
  const c=CARDS[n]; if(!c) return '';
  let sec='';
  for(const f of Object.keys(FORMATS)){
    const uses=INDEX[f].byCard[n]||[];
    sec+=`<div class="fmt">${FORMATS[f].label} · ${uses.length?uses.length+(uses.length===1?' estrategia':' estrategias'):'sin uso en las listas leídas'}</div>${useRows(uses)}`;
  }
  const total=usedCount(n);
  return `<div class="detail"><div class="hero-card">${thumb(n)}<div><h3>${esc(n)}</h3><div class="chips" id="dx-chips"></div><p class="eff" id="dx-eff">Cargando…</p></div></div>
    <div class="fmt">Banlist por formato</div>${limitChips(n)}
    <div id="dx-tail"></div>
    <p style="margin:0;color:var(--muted);font-size:.9rem">${total>=4?'Es una carta genérica: la juegan muchas estrategias.':total===0?'No aparece en ninguna lista del meta leído.':''}</p>${sec}</div>`;
}
const RAR_ES = {C:'Común',R:'Rara',SR:'Súper',UR:'Ultra',UtR:'Ultimate',ScR:'Secreta',PScR:'Secreta prismática',StR:'Starlight',CR:"Collector's",GR:'Ghost',GScR:'Gold secreta',PG:'Premium Gold',QCScR:'Secreta 25.º aniv.',SHR:'Shatterfoil',DNPR:'Duel Terminal',SPR:'Short Print',N:'Normal'};
function dlBlock(n,d){
  const dl=d.dl;
  if(!dl) return `<div class="fmt">Duel Links · cómo conseguirla</div><p class="eff">No está en Duel Links.</p>`;
  const sets=srcOrder(dl.ob.filter(o=>o[0]==='s'));
  const chars=dl.ob.filter(o=>o[0]==='c'), oth=dl.ob.filter(o=>o[0]==='o');
  const firstPack=sets.findIndex(o=>PACK_RE.test(o[2]||''));
  const rows=sets.map((o,i)=>`<div class="src">${i===firstPack?'<span class="new">Caja más reciente</span>':''}<button class="lnk" data-set="dl|${esc(o[1])}">${esc(o[1])}</button><span class="mini">${esc(SET_ES[o[2]]||o[2]||'')}${o[4]?' · '+o[4]:''}</span><b>${o[3]?'×'+o[3]:''}</b></div>`).join('');
  const crows=chars.map(o=>`<div class="src"><button class="lnk" data-set="dl|${esc(o[1])}">${esc(o[1])}</button><span class="mini">Subiendo de nivel al personaje</span><b>${o[3]?'×'+o[3]:''}</b></div>`).join('');
  const names=oth.map(o=>o[1]);
  const trader=names.filter(x=>TRADERS.has(x));
  const orows=oth.map(o=>`<div class="src"><button class="lnk" data-set="dl|${esc(o[1])}">${esc(OTHER_ES[o[1]]||o[1])}</button><b>${o[3]>1?'×'+o[3]:''}</b></div>`).join('');
  let tnote='';
  if(trader.length){
    tnote = sets.length
      ? `<p class="eff">Card Trader: la carta también sale en cajas, así que probablemente se cambia con fichas (la fuente no distingue el tipo de moneda).</p>`
      : `<p class="eff">Card Trader: la carta no sale en ninguna caja, así que se cambia con ítems exclusivos del cambiacartas.</p>`;
  }
  const paid=sets.some(o=>PAID.test(o[2]||''));
  return `<div class="fmt">Duel Links · cómo conseguirla</div>
   <div class="chips"><span class="chip">Rareza ${esc(dl.r||'?')}</span>${dl.rel?`<span class="chip">Salió ${esc(dl.rel)}</span>`:''}${dl.rush?'<span class="chip">Rush Duel</span>':''}<span class="chip">${esc(DLD.cards[n]?dlBadge(n):'')}</span></div>
   ${rows?`<h4 class="mini" style="margin:8px 0 2px">CAJAS Y ESTRUCTURAS (la más reciente primero, selección al final)</h4>${rows}`:''}
   ${crows?`<h4 class="mini" style="margin:8px 0 2px">PERSONAJES</h4>${crows}`:''}
   ${orows?`<h4 class="mini" style="margin:8px 0 2px">OTRAS VÍAS</h4>${orows}`:''}${tnote}
   ${paid?'<p class="eff">Las estructuras y cajas de selección suelen venderse con dinero real o gemas; la fuente no publica el precio de cada una.</p>':''}`;
}
function tcgBlock(n,d){
  if(!d.pn||!d.pn.length) return `<div class="fmt">TCG · expansiones y rarezas</div><p class="eff">No tiene impresiones en el TCG.</p>`;
  const sets=TCGSETS, rows=EX.allPrints?d.pn:d.pn.slice(0,12);
  const rars=[...new Set(d.pn.map(p=>p[2]))];
  const first=d.pn[d.pn.length-1];
  const pr=d.p||[];
  return `<div class="fmt">TCG · expansiones, rarezas y precio</div>
   <p class="eff">Primera impresión: ${esc(sets[first[0]][0])} (${esc(sets[first[0]][2]||'')}-${esc(first[1])}), ${esc((sets[first[0]][1]||'').slice(0,7))}. ${d.pn.length} impresiones.
   ${pr[0]!=null?'≈ US$ '+pr[0]+' (TCGplayer)':''}${pr[1]!=null?' · ≈ € '+pr[1]+' (Cardmarket)':''}. Precio de referencia.</p>
   <div class="chips">${rars.map(r=>`<span class="chip" title="${esc(RAR_ES[r]||r)}">${esc(r)}</span>`).join('')}</div>
   <div class="tbl"><table class="ptab"><thead><tr><th>Expansión</th><th>Código</th><th>Rareza</th><th>Fecha</th><th>Precio</th></tr></thead><tbody>
   ${rows.map(p=>`<tr><td><button class="lnk" data-set="tcg|${esc(sets[p[0]][0])}">${esc(sets[p[0]][0])}</button></td><td>${esc(sets[p[0]][2]||'')}-${esc(p[1])}</td><td title="${esc(RAR_ES[p[2]]||'')}">${esc(p[2])}</td><td>${esc((sets[p[0]][1]||'').slice(0,7))}</td><td>${p[3]>0?'US$ '+p[3]:''}</td></tr>`).join('')}</tbody></table></div>
   ${d.pn.length>12?`<p style="margin:6px 0 0"><button class="sbtn" data-allprints="1">${EX.allPrints?'Ver menos':'Ver las '+d.pn.length+' impresiones'}</button></p>`:''}`;
}
async function fillDetail(n){
  const tail=$('#dx-tail'); if(!tail) return;
  let d;
  try{ d=await getDetail(n); }catch(e){ const el=$('#dx-eff'); if(el) el.textContent='No se pudo cargar el detalle de la carta.'; return; }
  if(mode!=='ex'||EX.card!==n||!$('#dx-tail')) return;
  $('#dx-eff').textContent=d.d||(d.dl?'Carta de Duel Links sin texto en la base TCG.':'');
  const c=CARDS[n];
  $('#dx-chips').innerHTML=(d.ty?`<span class="chip">${esc(d.ty)}</span>`:'')+(c[C.FL]&8?'<span class="chip">Staple</span>':'')+(c[C.FL]&4?'<span class="chip">Rush Duel</span>':'');
  $('#dx-tail').innerHTML=dlBlock(n,d)+tcgBlock(n,d);
}
function viewEX(){
  const q=EX.q.trim().toLowerCase();
  let left, right;
  if(EX.view==='card'){
    const fmOK=n=>{ const f=CARDS[n][C.FL]; return EX.fm==='all'||(EX.fm==='tcg'&&(f&1))||(EX.fm==='dl'&&(f&2))||(EX.fm==='rush'&&(f&4)); };
    const catOK=n=>EX.type==='all'||CARDS[n][C.CAT]===EX.type;
    let names=NAMES.filter(n=>(!q||n.toLowerCase().includes(q))&&catOK(n)&&fmOK(n)&&(!EX.meta||usedCount(n)>0));
    names.sort((a,b)=>usedCount(b)-usedCount(a)||(CARDS[b][C.SH]>=0)-(CARDS[a][C.SH]>=0)||a.localeCompare(b));
    const shown=names.slice(0,EX.limit);
    if(!CARDS[EX.card]) EX.card=names[0]||NAMES[0];
    left=`<div class="filters"><label class="sr" for="q">Buscar carta</label><input id="q" type="search" placeholder="Buscar entre ${NAMES.length.toLocaleString('es-AR')} cartas (ej. Nibiru)" value="${esc(EX.q)}" autocomplete="off">
      <label class="sr" for="ty">Tipo</label><select id="ty"><option value="all">Todos los tipos</option><option value="m">Monstruos</option><option value="e">Extra Deck</option><option value="s">Hechizos</option><option value="t">Trampas</option></select>
      <label class="sr" for="fm">Juego</label><select id="fm"><option value="all">Todos los juegos</option><option value="tcg">TCG</option><option value="dl">Duel Links</option><option value="rush">Rush Duel</option></select>
      <label class="chk"><input type="checkbox" id="mt" ${EX.meta?'checked':''}> Solo cartas del meta</label></div>
      <p class="lede">${names.length.toLocaleString('es-AR')} ${names.length===1?'carta':'cartas'}. Primero las que más estrategias usan.</p>
      <div class="pick"><div class="cgrid">${shown.map(c=>`<button class="cc" data-card="${esc(c)}" aria-pressed="${c===EX.card}">${thumb(c)}<span class="n">${esc(c)}<b>${usedCount(c)?usedCount(c)+' estrat.':''}</b>${miniLims(c)}</span></button>`).join('')}</div>
      ${names.length>shown.length?`<p style="text-align:center"><button class="sbtn" data-more="1">Mostrar más</button></p>`:''}</div>`;
    right=cardDetail(EX.card);
  } else {
    const idx=INDEX[EX.fmt];
    if(!idx.strategies.find(s=>s.id===EX.strat)) EX.strat=(idx.strategies[0]||{}).id;
    const s=idx.strategies.find(x=>x.id===EX.strat);
    left=`<div class="seg" style="margin-top:0">${Object.keys(FORMATS).map(f=>`<button data-fmt="${f}" aria-pressed="${f===EX.fmt}">${FORMATS[f].label}</button>`).join('')}</div>
      <p class="lede">Elegí una estrategia para ver todas sus cartas y en qué otras estrategias se usa cada una.</p>
      <div>${idx.strategies.map(x=>`<button class="sbtn" data-strat="${x.id}" aria-pressed="${x.id===EX.strat}">${esc(x.name)}</button>`).join('')}</div>`;
    right=s?`<div class="detail"><h3>${esc(s.name)}</h3><p style="margin:0">${s.kind==='motor'?esc(s.txt):'Mazo con '+s.cards.length+' cartas distintas'+(s.lists?' · % sobre '+s.lists+' listas':'')+'.'}</p>
      ${s.cards.map(([c,p,k])=>{const others=(idx.byCard[c]||[]).filter(u=>u.s.id!==s.id);
        return `<div class="use"><button class="tcard" data-card="${esc(c)}">${thumb(c)}<span>${esc(c)}</span></button><b>${p!=null?p+'%':''}${k?(p!=null?' · ':'')+k.join(', '):''}</b>
         <div class="tags">${others.length?'<span>También en:</span>'+others.map(u=>`<span>${esc(u.s.name)}</span>`).join(''):'<span>Solo en esta estrategia</span>'}</div></div>`;}).join('')}</div>`:'<div class="detail"><p>Sin datos.</p></div>';
  }
  return `<section style="margin-top:32px"><h2>Buscador de cartas</h2>
   <p class="lede">Buscá entre todas las cartas del TCG y de Duel Links. Cada carta muestra su límite en el TCG, en Duel Links y su costo en Genesys, dónde se consigue y en qué estrategias del meta se juega.</p>
   <div class="seg" role="group" aria-label="Vista"><button data-v="card" aria-pressed="${EX.view==='card'}">Por carta</button><button data-v="strat" aria-pressed="${EX.view==='strat'}">Por estrategia</button></div>
   <div class="exg"><div>${left}</div>${right}</div></section>`;
}

/* ---------- CAJAS Y SETS ---------- */
const SETS = {fmt:'tcg',q:'',sel:null,kind:'set',limit:80,cl:150,data:{},loading:false};
const KIND_ES = {set:'Cajas y estructuras',char:'Personajes',other:'Otras vías'};
async function loadSets(fmt){
  if(SETS.data[fmt]||SETS.loading) return;
  SETS.loading=true;
  try{ SETS.data[fmt]=await fetch('data/sets-'+fmt+'.json').then(r=>{ if(!r.ok) throw new Error(r.status); return r.json(); }); }catch(e){ SETS.data[fmt]=[]; }
  SETS.loading=false; if(mode==='sets') render(SETS.focusQ);
}
function viewSets(){
  const fmt=SETS.fmt, data=SETS.data[fmt];
  const head=`<section style="margin-top:32px"><h2>Cajas y sets</h2>
    <p class="lede">Mirá qué cartas trae cada expansión del TCG, o cada caja, estructura, personaje y vía especial de Duel Links.</p>
    <div class="seg" role="group" aria-label="Juego"><button data-sfmt="tcg" aria-pressed="${fmt==='tcg'}">TCG</button><button data-sfmt="dl" aria-pressed="${fmt==='dl'}">Duel Links</button></div>
    ${fmt==='dl'?`<div class="seg" role="group" aria-label="Tipo">${Object.keys(KIND_ES).map(k=>`<button data-skind="${k}" aria-pressed="${SETS.kind===k}">${KIND_ES[k]}</button>`).join('')}</div>`:''}`;
  if(!data){ loadSets(fmt); return head+'<p class="lede">Cargando…</p></section>'; }
  const q=SETS.q.trim().toLowerCase();
  let list=data.filter(s=>(fmt==='tcg'||s.kind===SETS.kind)&&(!q||s.n.toLowerCase().includes(q)));
  if(fmt==='dl'&&SETS.kind!=='set') list.sort((a,b)=>b.k.length-a.k.length);
  const shown=list.slice(0,SETS.limit);
  let sel=data.find(s=>s.n===SETS.sel&&(fmt==='tcg'||s.kind===SETS.kind))||null;
  if(!sel&&shown.length) sel=shown[0];
  let right='<div class="detail"><p>Sin resultados.</p></div>';
  if(sel){
    const rows=fmt==='tcg'?[...sel.k].sort((a,b)=>a[1].localeCompare(b[1])):[...sel.k].sort((a,b)=>NAMES[a[0]].localeCompare(NAMES[b[0]]));
    const cs=rows.slice(0,SETS.cl);
    right=`<div class="detail"><h3>${esc(sel.n)}</h3>
      <p class="eff">${fmt==='tcg'?`${esc(sel.d||'sin fecha')} · ${sel.k.length} cartas de nuestra base`:`${esc(SET_ES[sel.t]||sel.t||'')}${sel.rel?' · '+esc(sel.rel):''} · ${sel.k.length} cartas`}</p>
      <div class="cgrid">${cs.map(r=>{const n=NAMES[r[0]]; return `<button class="cc" data-card="${esc(n)}">${thumb(n)}<span class="n">${esc(n)}<b>${fmt==='tcg'?esc(r[1])+' · '+esc(r[2])+(r[3]>0?' · $'+r[3]:''):(r[1]?'×'+r[1]:'')}</b></span></button>`;}).join('')}</div>
      ${rows.length>cs.length?`<p style="text-align:center"><button class="sbtn" data-smore="1">Mostrar más</button></p>`:''}</div>`;
  }
  return head+`<div class="exg"><div><div class="filters"><label class="sr" for="sq">Buscar set</label><input id="sq" type="search" placeholder="Buscar entre ${list.length} ${fmt==='tcg'?'expansiones':KIND_ES[SETS.kind].toLowerCase()}" value="${esc(SETS.q)}" autocomplete="off"></div>
    <p class="lede">Más recientes primero.</p>
    <div class="setlist">${shown.map(s=>`<button class="setb" data-setsel="${esc(s.n)}" aria-pressed="${sel&&s.n===sel.n}"><span>${esc(s.n)}</span><small>${fmt==='tcg'?esc((s.d||'').slice(0,7)):esc((SET_ES[s.t]||s.t||'')+(s.rel?' · '+s.rel.slice(0,7):''))}</small></button>`).join('')}
    ${list.length>shown.length?`<button class="sbtn" data-smoresets="1">Mostrar más</button>`:''}</div></div>${right}</div></section>`;
}

/* ---------- BANLIST ---------- */
const BAN = {fmt:'tcg',q:'',min:1};
function viewBan(){
  const q=BAN.q.trim().toLowerCase(), f=BAN.fmt;
  const match=n=>!q||n.toLowerCase().includes(q);
  const grid=(names,label)=>`<div class="cgrid">${names.map(n=>`<button class="cc" data-card="${esc(n)}">${thumb(n)}<span class="n">${esc(n)}<b>${label(n)}</b></span></button>`).join('')}</div>`;
  let body='', note='';
  if(f==='tcg'){
    const groups=[[0,'Prohibidas (0 copias)'],[1,'Limitadas (1 copia)'],[2,'Semi-limitadas (2 copias)']];
    body=groups.map(([b,t])=>{ const ns=NAMES.filter(n=>CARDS[n][C.BAN]===b&&match(n)); return ns.length?`<div class="bgrp"><h3>${t} · ${ns.length}</h3>${grid(ns,()=>'TCG')}</div>`:''; }).join('');
    note='Lista de prohibidas y limitadas del TCG según YGOPRODeck. El resto de las cartas va hasta 3 copias.';
  } else if(f==='dl'){
    const groups=[[1,'Límite 1'],[2,'Límite 2'],[3,'Límite 3']];
    body=groups.map(([d,t])=>{ const ns=NAMES.filter(n=>CARDS[n][C.DL]===d&&match(n)); return ns.length?`<div class="bgrp"><h3>${t} · ${ns.length}</h3>${grid(ns,()=>'Duel Links')}</div>`:''; }).join('');
    note='Lista de prohibidas y limitadas de Duel Links según Duel Links Meta. Las cartas fuera de la lista van hasta 3 copias.';
  } else {
    const ns=NAMES.filter(n=>CARDS[n][C.GEN]>=BAN.min&&match(n)).sort((a,b)=>CARDS[b][C.GEN]-CARDS[a][C.GEN]||a.localeCompare(b));
    body=`<div class="seg" role="group" aria-label="Puntos mínimos">${[[1,'Todas'],[20,'20 o más'],[50,'50 o más'],[100,'100 (casi prohibidas)']].map(([v,t])=>`<button data-bmin="${v}" aria-pressed="${BAN.min===v}">${t}</button>`).join('')}</div>
      <div class="bgrp"><h3>Cartas con puntos · ${ns.length}</h3>${grid(ns.slice(0,400),n=>CARDS[n][C.GEN]+' pts')}${ns.length>400?'<p class="lede">Mostrando las 400 de mayor costo. Usá el buscador para el resto.</p>':''}</div>`;
    note=`Puntos Genesys: lista de julio de 2026 más el ajuste de aniversario del 5 oct de 2026 (${DBINFO?DBINFO.gen.n:''} cartas con puntos). Cada carta cuenta su costo en el tope de 100 puntos del mazo. Las cartas de sets posteriores a julio pueden faltar.`;
  }
  return `<section style="margin-top:32px"><h2>Banlist por formato</h2>
    <p class="lede">Cómo se aplica la banlist en cada modo: límite de copias en el TCG, límite en Duel Links y costo en puntos en Genesys. Tocá una carta para ver las tres a la vez.</p>
    <div class="seg" role="group" aria-label="Formato"><button data-bfmt="tcg" aria-pressed="${f==='tcg'}">TCG</button><button data-bfmt="dl" aria-pressed="${f==='dl'}">Duel Links</button><button data-bfmt="gen" aria-pressed="${f==='gen'}">Genesys</button></div>
    <div class="note">${note}</div>
    <div class="filters"><label class="sr" for="bq">Buscar carta</label><input id="bq" type="search" placeholder="Filtrar por nombre" value="${esc(BAN.q)}" autocomplete="off"></div>${body}</section>`;
}

/* ---------- ENRUTADO ---------- */
let mode='tcg';
const MODES = {tcg:['TCG',viewTCG],gen:['Genesys',viewGEN],dl:['Duel Links',viewDL],ex:['Cartas',viewEX],sets:['Cajas y sets',viewSets],ban:['Banlist',viewBan]};
function render(focusId){
  document.body.className=mode;
  $('#hmode').textContent = MODES[mode][0];
  for(const m in MODES) $('#tab-'+m).setAttribute('aria-selected',m===mode);
  $('#app').innerHTML = (DBINFO||!['ex','sets','ban'].includes(mode)) ? MODES[mode][1]() : '<p class="lede" style="margin-top:32px">Cargando la base de cartas…</p>';
  const ty=$('#ty'); if(ty) ty.value=EX.type;
  const fm=$('#fm'); if(fm) fm.value=EX.fm;
  if(focusId){ const q=$('#'+focusId); if(q){q.focus(); q.setSelectionRange(q.value.length,q.value.length);} }
  try{ history.replaceState(null,'','#'+mode); }catch(e){}
  if(mode==='ex'&&EX.view==='card'&&DBINFO) fillDetail(EX.card);
}
function goCard(n){ EX.card=canon(n); EX.view='card'; EX.q=''; EX.type='all'; EX.fm='all'; EX.meta=false; EX.limit=60; EX.allPrints=false; mode='ex'; }
document.addEventListener('click',e=>{
  const b=e.target.closest('button'); if(!b) return;
  const d=b.dataset;
  if(d.mode){ mode=d.mode; render(); window.scrollTo(0,0); }
  else if(d.f){ dlFormat=d.f; render(); }
  else if(d.v){ EX.view=d.v; render(); }
  else if(d.fmt){ EX.fmt=d.fmt; render(); }
  else if(d.strat){ EX.strat=d.strat; render(); }
  else if(d.more){ EX.limit+=60; render(); }
  else if(d.allprints){ EX.allPrints=!EX.allPrints; render(); }
  else if(d.set){ const [f,nm]=d.set.split('|'); const i=nm; SETS.fmt=f; SETS.q=''; SETS.sel=i; SETS.limit=80; SETS.cl=150;
    if(f==='dl'){ SETS.kind='set'; loadSets('dl').then(()=>{ const s=(SETS.data.dl||[]).find(x=>x.n===i); if(s){ SETS.kind=s.kind; render(); } }); }
    mode='sets'; render(); window.scrollTo(0,0); }
  else if(d.sfmt){ SETS.fmt=d.sfmt; SETS.sel=null; SETS.q=''; SETS.limit=80; SETS.cl=150; render(); }
  else if(d.skind){ SETS.kind=d.skind; SETS.sel=null; SETS.limit=80; SETS.cl=150; render(); }
  else if(d.setsel){ SETS.sel=d.setsel; SETS.cl=150; render(); }
  else if(d.smore){ SETS.cl+=150; render(); }
  else if(d.smoresets){ SETS.limit+=80; render(); }
  else if(d.bfmt){ BAN.fmt=d.bfmt; render(); }
  else if(d.bmin){ BAN.min=+d.bmin; render(); }
  else if(d.card){ const was=mode; goCard(d.card); render(); if(was!=='ex') window.scrollTo(0,0); }
});
document.addEventListener('input',e=>{
  const id=e.target.id;
  if(id==='q'){ EX.q=e.target.value; EX.limit=60; render('q'); }
  else if(id==='ty'){ EX.type=e.target.value; EX.limit=60; render(); }
  else if(id==='fm'){ EX.fm=e.target.value; EX.limit=60; render(); }
  else if(id==='mt'){ EX.meta=e.target.checked; EX.limit=60; render(); }
  else if(id==='sq'){ SETS.q=e.target.value; SETS.limit=80; render('sq'); }
  else if(id==='bq'){ BAN.q=e.target.value; render('bq'); }
});
(()=>{ const el=$('#ticks'); if(el){ let s=''; for(let i=0;i<48;i++){ const a=i*7.5; s+=`<line x1="0" y1="-96" x2="0" y2="${i%4?-93:-90}" transform="rotate(${a})"/>`; } el.innerHTML=s; } })();
(()=>{ const el=$('#runes'); if(!el) return; const G=['M0,-85.5V-89.5','M0,-85.5V-89.5M-1.8,-87.5H1.8','M-1.5,-85.5L0,-89.5L1.5,-85.5','M0,-85.5V-87.6M0,-88.8V-89.5','M-1.6,-85.5L1.6,-89.5M1.6,-85.5L-1.6,-89.5','M-1.5,-89.5H1.5M0,-89.5V-85.5M-1.5,-85.5H1.5'];
  let s=''; for(let i=0;i<40;i++) s+=`<path d="${G[(i*7+i%3)%G.length]}" transform="rotate(${i*9})"/>`; el.innerHTML=s;
  const nd=$('#nodes'); if(nd){ let n=''; for(const [x,y] of [[0,-64],[55.4,32],[-55.4,-32],[0,64],[55.4,-32],[-55.4,32]]) n+=`<circle cx="${x}" cy="${y}" r="2.6"/>`; nd.innerHTML=n; } })();
const h=location.hash.slice(1); if(MODES[h]) mode=h;
render();
fetch('data/index.json').then(r=>{ if(!r.ok) throw new Error(r.status); return r.json(); }).then(j=>{
  DBINFO=j; TCGSETS=j.tcgsets;
  for(const r of j.cards){ CARDS[r[0]]=r.slice(1); NAMES.push(r[0]); }
  computeUsed(); render();
}).catch(e=>{ $('#app').innerHTML='<div class="note" style="margin-top:32px">No se pudo cargar la base de cartas (data/index.json). Recargá la página.</div>'; });
</script>
'''
i = s.index("/* ---------- BUSCADOR ---------- */")
s = s[:i] + NEW_TAIL

# ---------- footer ----------
rep("<li>Cartas, arte y textos: <a href=\"https://ygoprodeck.com/\">YGOPRODeck</a>. El buscador incluye las cartas del meta, los staples y todas las cartas de la lista de baneos del TCG, unas 600 en total, no las 13.000 del juego.</li>",
    "<li>Cartas, arte, textos, impresiones y banlist del TCG: <a href=\"https://ygoprodeck.com/\">YGOPRODeck</a> (unas 14.600 cartas). Las cartas de Duel Links y Rush Duel salen de Duel Links Meta. El arte está disponible para unas 3.000 cartas relevantes (meta, staples, banlists, Genesys y Duel Links); el resto muestra un cuadro por tipo.</li>\n    <li>Puntos Genesys: lista de <a href=\"https://genesyspointsygo.com/\">genesyspointsygo.com</a> del 6 jul 2026 más el ajuste de aniversario del 5 oct 2026 (<a href=\"https://ygorganization.com/genesys-1st-anniversary-update-genesys\">YGOrganization</a>, 316 de los 317 cambios). Las cartas de sets posteriores a julio aparecen con puntos sin confirmar.</li>\n    <li>Límite en Duel Links: campo de banlist de Duel Links Meta. Las cartas fuera de su lista de prohibidas van hasta 3 copias.</li>")
rep("Sin verificar: cuánto cambian los porcentajes tras la lista de baneos del 18 oct, y los puntos Genesys actuales (el ajuste de aniversario de oct 2026 no está cargado).",
    "Sin verificar: cuánto cambian los porcentajes tras la lista de baneos del 18 oct, y si algún set posterior al ajuste de aniversario movió puntos Genesys.")

open('src.html', 'w', encoding='utf-8').write(s)
print('patched', len(s))
