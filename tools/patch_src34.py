"""Duel Links: "Cartas recomendadas" (fuera de la Guía), en Speed y en Rush: las que conviene tener hoy (las que más mazos del meta juegan) y las que recomiendo
para quien empieza (las más jugadas entre las que se consiguen gratis, con tickets o en estructuras), más los mazos del meta más baratos. Todo se calcula con las
recetas de los decks recientes y con cómo se consigue cada carta; es un criterio de este sitio. Backup: src.before_patch34.html."""
import shutil
shutil.copy('src.html', 'src.before_patch34.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("function viewDL(){", r'''const DL_EASY=new Set(['Gratis · personaje','Gratis · evento','Ticket UR','Ticket SR','Tickets','Estructura']);
function dlHow(n){   // cómo conseguir una carta, en una línea
  const i=DLD.cards[n]; if(!i) return '';
  const b=dlBadge(n);
  if(i.c.length) return `Gratis con ${i.c[0][0]}${i.c.length>1?' y '+(i.c.length-1)+' personaje'+(i.c.length>2?'s':'')+' más':''}`;
  if(b==='Gratis · evento') return 'Gratis en eventos y misiones';
  if(/^Ticket/.test(b)||b==='Tickets') return 'Canje con tickets';
  if(b==='Estructura') return 'Mazo de estructura';
  if(b==='Paquete'||b==='Caja de selección') return (i.s[0]?'Caja: '+i.s[0][0]:'Cajas');
  return b;
}
function dlRecs(){
  const decks=(dlFormat==='speed'?DL_SPEED:DL_RUSH).filter(d=>!d.out&&d.cards&&d.cards.length&&d.lists);
  const total=decks.reduce((a,d)=>a+d.lists,0)||1, m=new Map();
  for(const d of decks) for(const [n,p] of d.cards){ const e=m.get(n)||{n,s:0,k:0}; e.s+=d.lists*p/100; e.k++; m.set(n,e); }
  const rows=[...m.values()].filter(e=>DLD.cards[e.n]).map(e=>({n:e.n,cov:e.s/total*100,k:e.k,badge:dlBadge(e.n),how:dlHow(e.n)})).sort((a,b)=>b.cov-a.cov||b.k-a.k);
  const cheap=decks.filter(d=>d.gemsMed!=null&&(dlFormat==='rush'||(d.tier!=='R'&&d.tier!=='N'))).sort((a,b)=>a.gemsMed-b.gemsMed||b.share-a.share).slice(0,4);
  return {today:rows.filter(r=>r.k>=2||r.cov>=8).slice(0,24), start:rows.filter(r=>DL_EASY.has(r.badge)&&(r.k>=2||r.cov>=5)).slice(0,18), cheap, total, n:decks.length};
}
function dlRecsSection(){
  const R=dlRecs(), mode=DL_FMT[dlFormat];
  const cards=rs=>`<div class="cgrid">${rs.map(r=>`<button class="cc" data-card="${esc(r.n)}">${thumb(r.n)}<span class="n">${esc(r.n)}<b>${fmt(r.cov)} de los mazos${r.k>1?' · '+r.k+' arquetipos':''}</b><small class="rhow">${esc(r.how)}</small></span></button>`).join('')}</div>`;
  const rows=R.cheap.map(d=>`<tr><td><strong>${esc(d.n)}</strong></td><td class="big">${fmtNum(d.gemsMed)}</td><td class="big">${d.usdMed?'US$ '+d.usdMed:'0'}</td><td>${fmt(d.share)}</td><td>${d.tier&&TIERS[d.tier]?TIERS[d.tier][1]:'—'}</td></tr>`);
  return `${secHead('Cartas recomendadas',`Qué conviene tener en ${mode} y por dónde empezar. Se calcula con los ${R.total} decks recientes de los ${R.n} arquetipos del ranking: es el porcentaje de esos decks que juega cada carta.`,
      how(`<p><b>Para tener hoy</b>: las cartas que más mazos del meta juegan (al menos 2 arquetipos, o 8% de los decks). Si las tenés, armás varios mazos buenos.</p><p><b>Para quien empieza</b>: las más jugadas entre las que se consiguen sin gastar gemas en cajas: gratis con personajes o en eventos, con tickets o en mazos de estructura. Los mazos más baratos usan la mediana de gemas y dinero que estima Duel Links Meta.</p><p>Es un criterio de este sitio, no una lista oficial. El meta cambia con cada caja y cada lista de prohibidas.</p>`))}
    <h3 style="margin-top:var(--s4)">Para tener hoy</h3>${cards(R.today)}
    <h3 style="margin-top:var(--s5)">Para quien empieza</h3><p class="lede">Muy jugadas y fáciles de conseguir. Empezá por las gratis con personajes y eventos.</p>${cards(R.start)}
    ${R.cheap.length?`<h3 style="margin-top:var(--s5)">Mazos del meta más baratos de armar</h3>${tbl(['Mazo','Gemas (mediana)','Dinero real (mediana)','% de la muestra','Tier'],rows)}`:''}</section>`;
}
function viewDL(){''')
rep("  ${secHead(`Cuánto cuesta armarlo`,", "  ${dlRecsSection()}\n  ${secHead(`Cuánto cuesta armarlo`,")
rep(".fmtbar{margin:var(--s4) 0 0}", ".fmtbar{margin:var(--s4) 0 0}\n.rhow{display:block;margin-top:2px;color:var(--muted);font:500 .68rem var(--f-data);white-space:normal}")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 34 ok')
