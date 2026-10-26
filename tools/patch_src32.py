"""1) Precio de las cartas que no tenían: Rush Duel desde Yuyu-tei (¥, convertido) y estimados marcados con ≈ para el resto (bandera 16 del índice, detalle "pj").
2) Cabecera de las vías de obtención (tickets, eventos...) con la misma lógica que la tarjeta de personaje: ticket grande e inclinado a la izquierda y las cartas
más fuertes de esa vía en abanico a la derecha. Backup: src.before_patch32.html."""
import shutil
shutil.copy('src.html', 'src.before_patch32.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- precios: ≈ en los estimados ----------
rep("const pr$=c&&c[C.PR]>0?`<i class=\"pr\">$${c[C.PR]}</i>`:'';", "const pr$=c&&c[C.PR]>0?`<i class=\"pr\"${c[C.FL]&16?' title=\"Precio estimado\"':''}>${c[C.FL]&16?'≈':''}$${c[C.PR]}</i>`:'';")
rep("else meta=c&&c[C.PR]>0?`<b class=\"vv\">$${c[C.PR]}</b>`:'';", "else meta=c&&c[C.PR]>0?`<b class=\"vv\"${c[C.FL]&16?' title=\"Precio estimado\"':''}>${c[C.FL]&16?'≈':''}$${c[C.PR]}</b>`:'';")
rep("const isec=(t,h,open=true)=>", r'''const pjBlock=d=>{   // precio de una carta que no se vende en el TCG
  const p=d&&d.pj; if(!p) return '';
  if(p.k==='yuyu') return isec('Precio de referencia (Japón)',`<p class="eff">≈ US$ ${p.usd} · ¥${p.jpy.toLocaleString('es-AR')} en Yuyu-tei, impresión ${esc(p.no)}${p.stock>0?'':' (sin stock)'}. Es el precio de venta de la tienda japonesa, no un promedio de mercado ni la última venta. Convertido al cambio del ${dmy(p.date)} (1 ¥ = US$ ${p.rate}).</p>${p.url&&/^https:\/\//.test(p.url)?`<p><a href="${esc(p.url)}" target="_blank" rel="noopener noreferrer">Ver en Yuyu-tei</a></p>`:''}`,false);
  return isec('Precio estimado',`<p class="eff">≈ US$ ${p.usd} (estimado). Esta carta no tiene precio publicado; se toma la mediana de las ${p.n} ${p.cat?'cartas del TCG del mismo tipo ('+({m:'monstruo',e:'Extra Deck',s:'magia',t:'trampa'}[p.cat]||'carta')+')':'cartas '+(p.rush?'de Rush Duel ':'')+'de rareza '+esc(p.rar)} que sí tienen precio. Es solo una referencia.</p>`,false);
};
const isec=(t,h,open=true)=>''')
rep("$('#dx-tail').innerHTML=isec('Duel Links · cómo conseguirla',dlBlock(n,d))+", "$('#dx-tail').innerHTML=isec('Duel Links · cómo conseguirla',dlBlock(n,d))+pjBlock(d)+")
rep("if(SETS.fmt==='dl'){ $('#sx-tail').innerHTML=isec('Cómo conseguirla',dlBlock(n,d)); return; }", "if(SETS.fmt==='dl'){ $('#sx-tail').innerHTML=isec('Cómo conseguirla',dlBlock(n,d))+pjBlock(d); return; }")

# ---------- cabecera de las otras vías ----------
rep("function boxMedia(s,fmt,rep){", r'''function srcTop(sel,k){   // las cartas más fuertes de una vía: rareza y, a igual rareza, la más nueva
  const seen=new Set(), rows=[];
  for(const r of sel.k){ const n=NAMES[r[0]]; if(seen.has(n)||!CARDS[n]||!CARDS[n][C.ID]) continue; seen.add(n); rows.push([n,CHAR_RAR[dlRar(n)]||0,dlRel(n)||'']); }
  rows.sort((a,b)=>b[1]-a[1]||b[2].localeCompare(a[2]));
  return rows.slice(0,k).map(x=>x[0]);
}
function othCard(sel){
  const t=TICKET.find(x=>x[0].test(sel.n)), kind=t?t[1]:'gen', tc=(TKKIND[kind]||TKKIND.gen)[1], top=srcTop(sel,2);
  const cnt=r=>sel.k.filter(x=>dlRar(NAMES[x[0]])===r).length;
  return `<div class="chcard oth" style="--oc:${tc}">
    <div class="othticket">${ticketIcon(sel.n,sel.rush)}</div>
    <div class="chtxt"><small>Otra vía${sel.rush?' · Rush Duel':' · Speed Duel'}</small><h3>${esc(sel.n)}</h3>
      <div class="schips"><i>${sel.k.length} cartas</i>${['UR','SR','R'].filter(r=>cnt(r)).map(r=>`<i>${r} ${cnt(r)}</i>`).join('')}</div>
      ${top.length?`<p class="chflag">Más fuertes: <b>${top.map(esc).join(' · ')}</b></p>`:''}</div>
    ${top.map((n,i)=>`<img class="chfg f${i+1}" src="${imgUrl(cardId(n),true)}" alt="${esc(n)}" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">`).join('')}
  </div>`;
}
function boxMedia(s,fmt,rep){''')
rep("${fmt==='dl'&&sel.kind==='char'?charCard(sel):`<div class=\"sethero", "${fmt==='dl'&&sel.kind==='char'?charCard(sel):fmt==='dl'&&sel.kind==='other'?othCard(sel):`<div class=\"sethero")
rep(".fmtbar{margin:var(--s4) 0 0}", """.fmtbar{margin:var(--s4) 0 0}
.chcard.oth{background:linear-gradient(115deg,color-mix(in srgb,var(--oc,var(--accent)) 26%,var(--surface)),var(--surface) 64%);border-color:color-mix(in srgb,var(--oc,var(--accent)) 50%,var(--line2))}
.chcard.oth::after{content:"";position:absolute;left:-6%;top:-30%;width:55%;height:160%;z-index:-1;background:radial-gradient(closest-side,color-mix(in srgb,var(--oc,var(--accent)) 38%,transparent),transparent);pointer-events:none}
.othticket{flex:none;width:236px;rotate:-5deg;filter:drop-shadow(0 16px 22px rgba(0,0,0,.5));transition:rotate .5s,scale .5s}
.othticket svg{display:block;width:100%;height:auto}
.chcard.oth:hover .othticket{rotate:-2deg;scale:1.04}
.chcard.oth .chtxt{max-width:34%}
.chfg.f1{right:17%;rotate:-6deg;z-index:1}
.chfg.f2{right:3%;rotate:8deg;z-index:2}
.chcard.oth:hover .chfg.f1{rotate:-9deg}.chcard.oth:hover .chfg.f2{rotate:5deg}
@container (max-width:600px){.chcard.oth .othticket{width:170px}.chcard.oth .chtxt{max-width:calc(100% - 290px)}.chfg.f1{display:none}.chfg.f2{right:2.5%}}
@container (max-width:470px){.chcard.oth .othticket{width:120px}.chcard.oth .chtxt{max-width:none}.chfg.f2{display:none}}""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 32 ok')
