"""Formatos retro del TCG (Edison, Goat, HAT) además del Advanced actual: selector en la pestaña TCG, banlist por formato, límites en el buscador,
constructor con las reglas de cada formato y una sección en la Guía. Datos: data/formats.js (tools/fetch_formats.py + tools/formats.py). Backup: src.before_patch25.html."""
import shutil
shutil.copy('src.html', 'src.before_patch25.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- datos y textos ----------
rep("function banMark(n,kind){", r'''/* ---------- formatos retro del TCG: Edison, Goat y HAT ---------- */
const FMT_RETRO={edison:'Edison',goat:'Goat',hat:'HAT'};
const FM={data:null,asked:false,pool:{}};
function fmLoad(){ if(FM.asked) return; FM.asked=true; loadData('formats').then(j=>{ FM.data=j; if(['tcg','ban','deck','ex','guide'].includes(mode)) render(); }).catch(()=>{ FM.asked=false; }); }
const fmPool=k=>{ if(!FM.data||typeof NAMES==='undefined'||!NAMES.length) return null; return FM.pool[k]||(FM.pool[k]=new Set(FM.data.formats[k].pool.map(i=>NAMES[i]))); };
function fmLimit(k,n){ const p=fmPool(k); if(!p) return null; if(!p.has(n)) return -1; const b=FM.data.formats[k].ban[n]; return b===undefined?3:b; }   // -1 no existe · 0 prohibida · 1 limitada · 2 semi-limitada · 3 libre
const RETRO_ES={
  adv:{n:'Advanced',era:'Formato actual',
    lede:'Es el formato oficial del TCG: se juega con todas las cartas publicadas y la banlist vigente de Konami. Es el que cubren los mejores mazos y los torneos de las otras secciones.',
    rules:['Main Deck de 40 a 60 cartas; Extra Deck y Side Deck de hasta 15.','Están todas las invocaciones: Fusión, Ritual, Sincro, Xyz, Péndulo y Link, con las zonas actuales (incluida la Zona de Monstruo Adicional).','Quien empieza el duelo no roba en su primer turno.','La banlist se actualiza varias veces al año y cambia el meta cada vez.'],
    meta:'Los mazos más usados de hoy están en la pestaña TCG, con su receta y sus cartas clave.'},
  edison:{n:'Edison',era:"Era 5D's · 2010",
    lede:'Formato retro que se juega con las cartas y la banlist de la primavera de 2010. Se llama así por el Shonen Jump Championship de Edison (Nueva Jersey) de abril de 2010, que ganó el Quickdraw Plant de Jeff Jones. Es famoso por la variedad de mazos y por su construcción abierta.',
    rules:['Banlist de marzo de 2010 (43 prohibidas, 70 limitadas y 19 semi-limitadas).','Solo existen las invocaciones Normal, Ritual, Fusión y Sincro: no hay Xyz, Péndulo ni Link, y no existe la Zona de Monstruo Adicional.','Los dos jugadores roban en el primer turno (esa regla se quitó recién con el Péndulo, en 2014).','Las cartas se leen con su texto y rulings de la época, no con el texto actual.'],
    meta:'El meta actual del formato lo dominan Blackwing, HERO y las variantes de Frog; también se juegan Lightsworn, Gladiator Beast, Vayu Turbo, Dragon, Hada, Machina, Planta y Zombi.'},
  goat:{n:'Goat',era:'Era GX · 2005',
    lede:'El primer formato de la era GX y uno de los retro más jugados. Su nombre viene del mazo Goat Control, que fue de los más exitosos de la época, aunque hoy el meta gira alrededor de Chaos Turbo. Es un formato simple e interactivo: pesan la lectura del rival, el engaño y el manejo de recursos.',
    rules:['Banlist de abril de 2005 (17 prohibidas, 41 limitadas y 15 semi-limitadas).','Las últimas expansiones del formato son Flaming Eternity y The Lost Millennium.','Hay Fusión y Ritual, pero no existen Sincro, Xyz, Péndulo ni Link.','Entran Rescue Cat, Brain Control y Lightning Vortex; Confiscation y The Forceful Sentry pasan a prohibidas, y Delinquent Duo y Graceful Charity salen de la lista de prohibidas (quedan limitadas).'],
    meta:'Chaos Turbo es el mazo de referencia; también se juegan Warrior, Goat Control y otros mazos de la época.'},
  hat:{n:'HAT',era:'Era Zexal · 2014',
    lede:'El último formato de la era Zexal y uno de los retro más jugados. El nombre sale de tres motores: Hand (mano), Artifact y Traptrix. Fue el último formato antes de los monstruos de Péndulo y de que se quitara el robo del primer turno.',
    rules:['Banlist de abril de 2014 (77 prohibidas, 71 limitadas y 14 semi-limitadas).','Hay Fusión, Ritual, Sincro y Xyz; no existen Péndulo ni Link.','Desde el formato Vegas se sumaron Dragons of Legend y Primal Origin: Traptrix Dionaea, Soul Charge, el apoyo de Sylvan y los arquetipos Artifact y Hand.','Se roba en el primer turno, como en Edison y Goat.'],
    meta:'El meta incluye Artifact Traptrix, Bujin, Geargia, Mermail y Spellbook, entre otros.'}
};
const RETRO_BAN={'April 2005':'abril de 2005','March 2010':'marzo de 2010','April 2014':'abril de 2014'};
let TCGF='adv';

function banMark(n,kind){''')
rep("  if(kind==='tcg'){ const b=c[C.BAN]; return b>=0&&b<3?banIcon(b,TCG_TIP[b]):''; }",
    "  if(kind==='tcg'){ const b=c[C.BAN]; return b>=0&&b<3?banIcon(b,TCG_TIP[b]):''; }\n  if(FMT_RETRO[kind]){ const l=fmLimit(kind,canon(n)); return l!=null&&l>=0&&l<3?banIcon(l,TCG_TIP[l]):''; }")

# ---------- buscador: límites por formato ----------
rep("  return `<div class=\"lims\"><div class=\"lim ${b>=0&&b<3?'hot':''}\"><small>TCG</small>${tcg}</div>",
    r'''  fmLoad();
  const rchip=k=>{ const l=fmLimit(k,n); const t=l==null?'<b>…</b>':l<0?'<b>No existe en el formato</b>':l<3?`<b>${banIcon(l,TCG_TIP[l])} ${l===0?'Prohibida':l===1?'Limitada · 1 copia':'Semi-limitada · 2 copias'}</b>`:'<b>Libre · hasta 3 copias</b>'; return `<div class="lim ${l!=null&&l>=0&&l<3?'hot':''}"><small>${FMT_RETRO[k]}</small>${t}</div>`; };
  const retro=`<div class="lims lims-r">${Object.keys(FMT_RETRO).map(rchip).join('')}</div>`;
  return `<div class="lims"><div class="lim ${b>=0&&b<3?'hot':''}"><small>TCG</small>${tcg}</div>''')
a = s.index("function limitChips(n){")
e = s.index("\n}\n", a)
fn = s[a:e]
tail = "</div></div>`;"
assert fn.rstrip().endswith(tail), fn[-80:]
fn2 = fn.rstrip()[:-len(tail)] + "</div></div>${retro}`;"
s = s[:a] + fn2 + s[e:]

# ---------- banlist por formato ----------
rep("  } else if(f==='dl'){\n    const groups=[[0,banIcon(0,dlTip(0))",
    r'''  } else if(FMT_RETRO[f]){
    fmLoad(); const F=FM.data&&FM.data.formats[f];
    if(!F) body='<p class="lede">Cargando la banlist…</p>';
    else {
      const groups=[[0,banIcon(0,TCG_TIP[0])+' Prohibidas (0 copias)'],[1,banIcon(1,TCG_TIP[1])+' Limitadas (1 copia)'],[2,banIcon(2,TCG_TIP[2])+' Semi-limitadas (2 copias)']];
      body=groups.map(([b,t])=>{ const ns=Object.keys(F.ban).filter(n=>F.ban[n]===b&&CARDS[n]&&match(n)).sort(); return ns.length?`<div class="bgrp"><h3>${t} · ${ns.length}</h3>${grid(ns,()=>banIcon(b,TCG_TIP[b]))}</div>`:''; }).join('');
      note=`Banlist ${RETRO_BAN[F.banlistName]||F.banlistName} del formato ${F.name}, de Format Library${f==='goat'?' (la de Goat coincide carta por carta con la de YGOPRODeck)':''}. Las cartas que no figuran van hasta 3 copias si existen en el formato (${F.pool.length.toLocaleString('es-AR')} cartas).`;
    }
  } else if(f==='dl'){
    const groups=[[0,banIcon(0,dlTip(0))''')
rep('<button data-bfmt="tcg" aria-pressed="${f===\'tcg\'}">TCG</button>',
    '<button data-bfmt="tcg" aria-pressed="${f===\'tcg\'}">TCG</button>${Object.entries(FMT_RETRO).map(([k,t])=>`<button data-bfmt="${k}" aria-pressed="${f===k}">${t}</button>`).join(\'\')}')

# ---------- pestaña TCG: selector de formato y vista retro ----------
rep("function viewTCG(){\n  const all=TCG_DECKS", r'''const fmtBar=cur=>`<div class="seg fmtbar" role="group" aria-label="Formato del TCG">${['adv','edison','goat','hat'].map(k=>`<button data-tcgf="${k}" aria-pressed="${cur===k}">${RETRO_ES[k].n}</button>`).join('')}</div>`;
function viewTCG(){
  return fmtBar(TCGF)+(TCGF==='adv'?viewTCGAdv():viewRetro(TCGF));
}
function viewRetro(k){
  fmLoad(); const I=RETRO_ES[k], F=FM.data&&FM.data.formats[k];
  const head=pageHead(`${I.n} · ${I.era}`,I.lede,how(`<p>La banlist, los mazos populares y los torneos recientes vienen de <a href="https://formatlibrary.com/">Format Library</a>. ${k==='hat'?'No hay una lista publicada de cartas legales de HAT: se toman todas las cartas cuya primera impresión en el TCG es anterior al formato (la misma regla acierta 3.661 de las 3.662 cartas de Edison).':'La lista de cartas legales es la que publica YGOPRODeck.'}</p><p>Son formatos históricos que juega la comunidad: no son formatos oficiales de Konami hoy y sus torneos son comunitarios, así que no hay tiers calculados como en Advanced.</p>`,'Fuentes y límites'));
  if(!F) return head+'<p class="lede">Cargando…</p></section>';
  const cnt=b=>Object.values(F.ban).filter(v=>v===b).length;
  const rs=(l,v)=>`<div class="rstat"><small>${l}</small><b>${v}</b></div>`;
  const art=id=>`<img src="https://images.ygoprodeck.com/images/cards_cropped/${esc(id)}.jpg" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">`;
  const safe=u=>/^https:\/\//.test(u||'')?u:'';
  return head+`<div class="rstats rr6">${rs('Formato desde',dmy(F.date))}${rs('Banlist',esc(RETRO_BAN[F.banlistName]||F.banlistName))}${rs('Cartas legales',F.pool.length.toLocaleString('es-AR'))}${rs('Prohibidas',cnt(0))}${rs('Limitadas',cnt(1))}${rs('Semi-limitadas',cnt(2))}</div>
    <p style="margin:var(--s3) 0"><button class="sbtn" data-gobfmt="${k}">Ver la banlist completa</button> <button class="sbtn" data-gotab="deck" data-dkf="${k}">Armar un mazo de ${I.n}</button></p>
    <h3 style="margin-top:var(--s5)">Cómo se juega</h3><ul class="rrules">${I.rules.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p class="lede">${esc(I.meta)}</p>
    <h3 style="margin-top:var(--s5)">Mazos populares</h3><div class="rdecks">${F.decks.map(d=>`<div class="rdeck"><div class="rart">${d.art.map(art).join('')}</div><b>${esc(d.n)}</b></div>`).join('')}</div>
    <h3 style="margin-top:var(--s5)">Torneos recientes</h3>${F.events.length?`<div class="tbl"><table class="ptab"><thead><tr><th>Torneo</th><th>Fecha</th><th>Jugadores</th><th>Ganador</th><th>Comunidad</th></tr></thead><tbody>${F.events.map(e=>`<tr><td>${safe(e.url)?`<a href="${esc(safe(e.url))}" target="_blank" rel="noopener noreferrer">${esc(e.n)}</a>`:esc(e.n)}</td><td>${e.d?dmy(e.d):''}</td><td>${e.size||''}</td><td>${esc(e.winner||'')}</td><td>${esc(e.community||'')}</td></tr>`).join('')}</tbody></table></div>`:'<p class="lede">Format Library no tiene torneos recientes de este formato.</p>'}
    <p class="rnote">Datos de Format Library; ${I.n} no tiene torneos oficiales hoy, estos son eventos de la comunidad.</p></section>`;
}
function viewTCGAdv(){
  const all=TCG_DECKS''')

# ---------- constructor ----------
rep("const FMT_ES={tcg:'TCG',gen:'Genesys',dl:'Duel Links'};", "const FMT_ES={tcg:'TCG',edison:'Edison',goat:'Goat',hat:'HAT',gen:'Genesys',dl:'Duel Links'};")
rep("  if(DK.fmt==='tcg'){ const b=c[C.BAN]; return b<0?0:b===3?3:b; }",
    "  if(FMT_RETRO[DK.fmt]){ const l=fmLimit(DK.fmt,n); return l==null?3:l<0?0:l; }\n  if(DK.fmt==='tcg'){ const b=c[C.BAN]; return b<0?0:b===3?3:b; }")
rep("  return `No se pueden usar cartas prohibidas: ${n} está prohibida en ${FMT_ES[DK.fmt]}.`;",
    "  if(FMT_RETRO[DK.fmt]&&fmLimit(DK.fmt,n)===-1) return `${n} no existe en ${FMT_ES[DK.fmt]} (es posterior al formato).`;\n  return `No se pueden usar cartas prohibidas: ${n} está prohibida en ${FMT_ES[DK.fmt]}.`;")
rep("const dkExists = n => { const c=CARDS[n]; if(DK.fmt==='tcg') return c[C.BAN]>=0;",
    "const dkExists = n => { const c=CARDS[n]; if(FMT_RETRO[DK.fmt]){ const l=fmLimit(DK.fmt,n); return l==null?c[C.BAN]>=0:l>=0; } if(DK.fmt==='tcg') return c[C.BAN]>=0;")
rep("const acc={tcg:'#4ee1ff',gen:'#b78bff',dl:'#3ddc97'}[DK.fmt];", "const acc={tcg:'#4ee1ff',edison:'#4ee1ff',goat:'#4ee1ff',hat:'#4ee1ff',gen:'#b78bff',dl:'#3ddc97'}[DK.fmt];")
rep("banMark(n,DK.fmt==='dl'?'dl':DK.fmt==='tcg'?'tcg':'')", "banMark(n,DK.fmt==='dl'?'dl':DK.fmt==='gen'?'':DK.fmt)")
rep("b=banMark(n,dl?'dl':'tcg');", "b=banMark(n,dl?'dl':DK.fmt);")
rep("${['tcg','gen','dl'].map(f=>`<button data-dkfmt=", "${['tcg','edison','goat','hat','gen','dl'].map(f=>`<button data-dkfmt=")
rep("function viewDeck(){\n", "function viewDeck(){\n  fmLoad();\n")

# ---------- Guía: pestaña Formatos ----------
rep("['basics','Cómo se juega'],['summons','Invocaciones']", "['basics','Cómo se juega'],['formats','Formatos del TCG'],['summons','Invocaciones']")
rep("  else if(GD.tab==='basics') body=", r'''  else if(GD.tab==='formats'){
    fmLoad();
    const card=k=>{ const I=RETRO_ES[k], F=FM.data&&FM.data.formats[k], dk=F?F.decks.slice(0,6).map(d=>`<i>${esc(d.n)}</i>`).join(''):'';
      const st=F?`<div class="schips"><i>${F.pool.length.toLocaleString('es-AR')} cartas legales</i><i>${Object.values(F.ban).filter(v=>v===0).length} prohibidas</i><i>${Object.values(F.ban).filter(v=>v===1).length} limitadas</i><i>${Object.values(F.ban).filter(v=>v===2).length} semi-limitadas</i></div>`:'';
      return `<div class="gfmt"><h3>${I.n} <span class="chip">${esc(I.era)}</span></h3><p>${esc(I.lede)}</p><ul class="rrules">${I.rules.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p>${esc(I.meta)}</p>${dk?`<div class="schips"><b>Mazos populares:</b>${dk}</div>`:''}${st}
        <p><button class="sbtn" data-gotcg="${k}">${k==='adv'?'Ver los mejores mazos':'Ver el formato'}</button> <button class="sbtn" data-gobfmt="${k==='adv'?'tcg':k}">Ver la banlist</button></p></div>`; };
    body=`<p class="lede">El TCG se puede jugar en varios formatos. El Advanced es el actual; Edison, Goat y HAT son formatos históricos que la comunidad sigue jugando con la banlist y las cartas de su época. Cada uno tiene su banlist, su lista de cartas legales y sus mazos, y están en el buscador, el constructor y la pestaña TCG.</p><div class="gfmts">${['adv','edison','goat','hat'].map(card).join('')}</div>`;
  }
  else if(GD.tab==='basics') body=''')

# ---------- eventos de clic ----------
rep("  else if(d.bfmt){ BAN.fmt=d.bfmt; render(); }",
    "  else if(d.tcgf){ TCGF=d.tcgf; render(); }\n  else if(d.gotcg){ TCGF=d.gotcg; mode='tcg'; render(); window.scrollTo(0,0); }\n  else if(d.gobfmt){ BAN.fmt=d.gobfmt; mode='ban'; render(); window.scrollTo(0,0); }\n  else if(d.gotab){ if(d.dkf){ DK.fmt=d.dkf; DK.msg=''; dkDraft(); } mode=d.gotab; render(); window.scrollTo(0,0); }\n  else if(d.bfmt){ BAN.fmt=d.bfmt; render(); }")

# ---------- fuentes y estilos ----------
rep("  <li>Cartas, arte, textos e impresiones:", "  <li>Formatos retro del TCG (Edison, Goat, HAT): banlists, mazos populares y torneos de <a href=\"https://formatlibrary.com/\">Format Library</a>; cartas legales de Goat y Edison de <a href=\"https://ygoprodeck.com/\">YGOPRODeck</a>, y la banlist de Goat se verificó contra la de YGOPRODeck. HAT no tiene lista publicada: se toman las cartas con primera impresión hasta la fecha del formato.</li>\n  <li>Cartas, arte, textos e impresiones:") if s.count("  <li>Cartas, arte, textos e impresiones:") == 1 else None
rep(".cportrait img{display:block;width:100%;height:auto}", """.cportrait img{display:block;width:100%;height:auto}
.fmtbar{margin:var(--s4) 0 0}
.rstats.rr6{grid-template-columns:repeat(auto-fit,minmax(150px,1fr))}
.lims-r{margin-top:var(--s2)}
.rrules{margin:var(--s2) 0 var(--s3);padding-left:1.1em;display:grid;gap:6px;color:var(--fg)}
.rdecks{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:var(--s3);margin-top:var(--s3)}
.rdeck{border:1px solid var(--line);border-radius:var(--r2);background:linear-gradient(150deg,color-mix(in srgb,var(--accent) 9%,var(--surface)),var(--surface));overflow:hidden;display:grid}
.rdeck b{padding:var(--s2) var(--s3);font:700 .92rem var(--f-display)}
.rart{display:grid;grid-template-columns:repeat(3,1fr);height:92px}
.rart img{width:100%;height:100%;object-fit:cover;transition:transform .5s cubic-bezier(.2,.7,.2,1)}
.rdeck:hover .rart img{transform:scale(1.08)}
.gfmts{display:grid;gap:var(--s4)}
.gfmt{border:1px solid var(--line);border-radius:var(--r2);padding:var(--s4);background:var(--surface)}
.gfmt h3{display:flex;align-items:center;gap:var(--s3);flex-wrap:wrap}""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 25 ok')
