"""Ronda 3: imagen real de TCGplayer por rareza (sin brillos), rarezas reales de Duel Links, orden por rareza o fecha, personajes por forma de obtención,
arte lateral más grande. Backup: src.before_patch18.html."""
import shutil
shutil.copy('src.html', 'src.before_patch18.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("ID:9,DID:10};", "ID:9,DID:10,DR:11,REL:12};")
# ---- cardImg: optional TCGplayer product id (real picture of one printing)
rep("function cardImg(n,big,fo){", "function cardImg(n,big,fo,pid){")
rep("  const src=cardSrc(n,big);\n  const c=CARDS[canon(n)], alt=c&&c[C.DID]&&!/s3\\.duellinksmeta/.test(src)?`https://s3.duellinksmeta.com/cards/${c[C.DID]}_w${big?360:200}.webp`:'';",
    "  const tp=pid?`https://product-images.tcgplayer.com/fit-in/${big?'437x437':'200x279'}/${pid}.jpg`:'';   // foto de TCGplayer de esa impresión; si falla, la carta de YGOPRODeck\n"
    "  const src=tp||cardSrc(n,big);\n  const c=CARDS[canon(n)], alt=tp?cardSrc(n,big):(c&&c[C.DID]&&!/s3\\.duellinksmeta/.test(src)?`https://s3.duellinksmeta.com/cards/${c[C.DID]}_w${big?360:200}.webp`:'');")
rep("const ffoil = (r,fmt) => fmt==='tcg' ? foil(r) : ({N:'n',R:'r',SR:'dsr',UR:'dur'}[r]||'n');", "const ffoil = (r,fmt) => fmt==='tcg' ? '' : ({N:'n',R:'r',SR:'dsr',UR:'dur'}[r]||'n');   // TCG: la foto real ya trae su acabado\nconst dlRar = n => (CARDS[n]&&CARDS[n][C.DR])||'N';\nconst dlRel = n => (CARDS[n]&&CARDS[n][C.REL])||'';\n"
    "const SUBSRC = sub => { const m=/^Level (\\d+)$/.exec(sub||''); if(m) return [+m[1],`Subiendo de nivel · nivel ${m[1]}`]; return {Drop:[100,'Farmeo en la Puerta (Gate): drop al ganar duelos'],'Character Deck':[101,'Duelos de personaje (Character Deck)'],'Starter Deck':[102,'Mazo inicial del personaje']}[sub]||[103,'Otras formas']; };")

# ---- sets block: rows, tile, inspector
a = s.index('function setRows(')
b = s.index('async function fillSInsp')
s = s[:a] + r'''function setRows(sel,fmt){
  const cn=SETS.cq.trim();
  let rows=sel.k;
  if(cn){ const ok=new Set(searchNames([...new Set(rows.map(r=>NAMES[r[0]]))],cn,(a,b)=>a.localeCompare(b))); rows=rows.filter(r=>ok.has(NAMES[r[0]])); }
  const rarOf=r=>fmt==='tcg'?r[2]:dlRar(NAMES[r[0]]);
  if(SETS.rf!=='all') rows=rows.filter(r=>rarOf(r)===SETS.rf);
  const desc=SETS.desc==null?fmt==='dl':SETS.desc, dir=desc?-1:1;      // TCG: de menor a mayor rareza; Duel Links: de mayor a menor (UR primero)
  const byDate=fmt==='dl'&&SETS.sort==='date', char=fmt==='dl'&&sel.kind==='char';
  const nm=r=>NAMES[r[0]];
  const cmp=(a,b)=>{
    if(char){ const d=SUBSRC(a[2])[0]-SUBSRC(b[2])[0]; if(d) return d; }
    if(byDate){ const d=dlRel(nm(b)).localeCompare(dlRel(nm(a))); if(d) return dir<0?d:-d; }
    return dir*(rarRank(rarOf(a),fmt)-rarRank(rarOf(b),fmt))||dir*rarOf(a).localeCompare(rarOf(b))||(fmt==='tcg'?a[1].localeCompare(b[1],undefined,{numeric:true}):nm(a).localeCompare(nm(b)));
  };
  const group=r=>{            // encabezado de cada bloque de cartas
    if(char) return SUBSRC(r[2])[1];
    if(byDate) return dlRel(nm(r)).slice(0,7)||'sin fecha';
    return rarOf(r);
  };
  return {rows:[...rows].sort(cmp),rarOf,group,gKind:char?'char':byDate?'date':'rar'};
}
function sTile(r,sel,fmt,rarOf,showDate){
  const n=NAMES[r[0]], rar=rarOf(r), price=fmt==='tcg'?r[3]:0;
  const on=SETS.card===n&&(fmt!=='tcg'||SETS.rar==null||SETS.rar===rar);
  const sub=fmt==='tcg'?(sel.code?sel.code+'-':'')+r[1]:(showDate?(dlRel(n)||'sin fecha'):(r[1]?'×'+r[1]+' en la caja':''));
  return `<button class="tile ptile${on?' on':''}" data-scard="${esc(n)}" data-srar="${esc(rar)}" title="${esc(n)} · ${esc(RAR_ES[rar]||rar)}"><span class="art">${cardImg(n,false,ffoil(rar,fmt),fmt==='tcg'?r[4]:0)}</span><span class="tn">${esc(n)}</span><span class="tm"><b class="${rchip(rar,fmt)}">${esc(rar)}</b>${price>0?`<b class="vv">$${price}</b>`:''}</span><span class="mini">${esc(sub)}</span></button>`;
}
function sInsp(sel,fmt){
  const n=SETS.card, c=CARDS[n]; if(!c) return '';
  const rows=sel.k.filter(r=>NAMES[r[0]]===n);
  let here='', pid=0;
  if(fmt==='tcg'){
    const ps=[...rows].sort((a,b)=>rarRank(b[2],'tcg')-rarRank(a[2],'tcg')||b[3]-a[3]);
    const cur=SETS.rar&&ps.some(r=>r[2]===SETS.rar)?SETS.rar:(ps[0]||[])[2];
    pid=(ps.find(r=>r[2]===cur)||[])[4]||0;
    here=`<div class="fmt">Rarezas en esta expansión · ${ps.length}</div><div class="pvs">${ps.map(r=>`<button class="pv${r[2]===cur?' on':''}" data-srar2="${esc(r[2])}" title="Ver esta rareza"><span class="art">${cardImg(n,false,'',r[4])}</span><b class="${rchip(r[2],'tcg')}">${esc(r[2])}</b><span class="mini">${esc(RAR_ES[r[2]]||'')}</span><span class="mini">${esc((sel.code?sel.code+'-':'')+r[1])}</span><b class="pp" data-pp="${esc((sel.code?sel.code+'-':'')+r[1])}|${esc(r[2])}">${r[3]>0?'$'+r[3].toFixed(2):'s/d'}</b></button>`).join('')}</div>
      <p class="rnote" id="sx-live">Consultando el precio de hoy…</p>
      ${ps.some(r=>r[4])?'<p class="rnote">Las imágenes de cada rareza son las fotos de TCGplayer de esa impresión.</p>':''}`;
    SETS._cur=cur;
  } else {
    const rar=dlRar(n);
    here=`<div class="fmt">En esta caja</div><div class="pvs">${rows.map(r=>`<div class="pv on"><span class="art">${cardImg(n,false,ffoil(rar,'dl'))}</span><b class="${rchip(rar,'dl')}">${esc(rar)}</b><span class="mini">${esc(sel.kind==='char'?SUBSRC(r[2])[1]:r[1]?'×'+r[1]+' copias':'')}</span></div>`).join('')}</div>
      <p class="rnote">${dlRel(n)?'Carta salida en Duel Links el '+esc(dlRel(n))+'.':''}</p>`;
    SETS._cur=rar;
  }
  return `<aside class="detail sinsp" aria-label="Carta seleccionada"><div class="sihead"><h3>${esc(n)}</h3><button class="abtn" data-sclose="1">Cerrar</button></div>
    <p class="esn" id="sx-es"></p>
    <div class="si-img"><div class="bigcard">${cardImg(n,true,ffoil(SETS._cur,fmt),pid)}${altSel(n)}</div><div><div class="chips" id="sx-chips"></div><div id="sx-stats"></div></div></div>
    <p class="eff" id="sx-eff">Cargando…</p>
    ${here}
    <div class="fmt">Banlist por formato</div>${limitChips(n)}
    <div id="sx-tail"></div>
    <p><button class="abtn" data-card="${esc(n)}">Abrir en el buscador de cartas</button></p></aside>`;
}
''' + s[b:]

# ---- viewSets pieces
rep("const SETS = {fmt:'tcg',q:'',sel:null,card:null,rar:null,cq:'',rf:'all',desc:false,kind:'set',limit:80,cl:SCL,data:{},loading:false};",
    "const SETS = {fmt:'tcg',q:'',sel:null,card:null,rar:null,cq:'',rf:'all',desc:null,sort:'rar',kind:'set',limit:80,cl:SCL,data:{},loading:false};")
rep("    const {rows,rarOf}=setRows(sel,fmt), cs=rows.slice(0,SETS.cl);", "    const {rows,rarOf,group,gKind}=setRows(sel,fmt), cs=rows.slice(0,SETS.cl);\n    const effDesc=SETS.desc==null?fmt==='dl':SETS.desc, byDate=gKind==='date'||(fmt==='dl'&&SETS.sort==='date');")
rep("const rarList=[...new Set(sel.k.map(r=>fmt==='tcg'?r[2]:((DLD.cards[NAMES[r[0]]]||{}).r||'N')))]", "const rarList=[...new Set(sel.k.map(r=>fmt==='tcg'?r[2]:dlRar(NAMES[r[0]])))]")
rep("""        <button class="abtn" data-sdesc="1" title="Cambiar el orden de las cartas por rareza">Orden: ${SETS.desc?'mayor a menor rareza':'menor a mayor rareza'}</button></div>`;""",
    """        ${fmt==='dl'?`<div class="seg mini" role="group" aria-label="Ordenar por"><button data-ssort="rar" aria-pressed="${SETS.sort==='rar'}">Por rareza</button><button data-ssort="date" aria-pressed="${SETS.sort==='date'}">Por fecha de lanzamiento</button></div>`:''}
        <button class="abtn" data-sdesc="1" title="Invertir el orden">Orden: ${SETS.sort==='date'&&fmt==='dl'?(effDesc?'más nuevas primero':'más viejas primero'):(effDesc?'mayor a menor rareza':'menor a mayor rareza')}</button></div>`;""")
rep("Ordenadas por rareza; cada una tiene su color y su efecto. Toc� una para verla en grande${fmt==='tcg'?' con su precio':''}.".replace('Toc�','Tocá'),
    "${gKind==='char'?'Agrupadas por cómo las da el personaje (subir de nivel, farmeo en la Puerta, duelos de personaje, mazo inicial) y ordenadas dentro de cada grupo.':gKind==='date'?'Ordenadas por fecha de lanzamiento en Duel Links.':'Ordenadas por rareza.'} Tocá una para verla en grande${fmt==='tcg'?' con la foto de cada rareza y su precio':''}.")
rep("const cnt={}; for(const r of rows){ const k=rarOf(r); cnt[k]=(cnt[k]||0)+1; } let last=null; return cs.map(r=>{ const k=rarOf(r); let h=''; if(k!==last){ last=k; h=`<h4 class=\"rgh\"><b class=\"${rchip(k,fmt)}\">${esc(k)}</b>${esc(RAR_ES[k]||'')} · ${cnt[k]}</h4>`; } return h+sTile(r,sel,fmt,rarOf); }).join('');",
    "const cnt={}; for(const r of rows){ const k=group(r); cnt[k]=(cnt[k]||0)+1; } let last=null; return cs.map(r=>{ const k=group(r); let h=''; if(k!==last){ last=k; h=`<h4 class=\"rgh\">${gKind==='rar'?`<b class=\"${rchip(k,fmt)}\">${esc(k)}</b>${esc(RAR_ES[k]||'')}`:esc(k)} · ${cnt[k]}</h4>`; } return h+sTile(r,sel,fmt,rarOf,byDate); }).join('');")
rep("  else if(d.sdesc){ SETS.desc=!SETS.desc; SETS.cl=SCL; render(); }", "  else if(d.sdesc){ SETS.desc=!(SETS.desc==null?SETS.fmt==='dl':SETS.desc); SETS.cl=SCL; render(); }\n  else if(d.ssort){ SETS.sort=d.ssort; SETS.cl=SCL; render(); }")
# kind buttons keep the order choice per format; leaving the format resets it
rep("else if(d.sfmt){ SETS.fmt=d.sfmt;", "else if(d.sfmt){ SETS.fmt=d.sfmt; SETS.desc=null; SETS.sort='rar';")

# ---- how a character gives the card
rep("const crows=chars.map(o=>`<div class=\"src\"><button class=\"lnk\" data-set=\"dl|${esc(o[1])}\">${esc(o[1])}</button><span class=\"mini\">Subiendo de nivel al personaje</span><b>${o[3]?'×'+o[3]:''}</b></div>`).join('');",
    "const crows=chars.map(o=>`<div class=\"src\"><button class=\"lnk\" data-set=\"dl|${esc(o[1])}\">${esc(o[1])}</button><span class=\"mini\">${esc(SUBSRC(o[5])[1])}</span><b>${o[3]?'×'+o[3]:''}</b></div>`).join('');")

# ---- css: no name-bar glare, no dotted glitter; bigger side art
rep(".sideart{position:fixed;top:110px;bottom:0;width:min(26vw,380px);pointer-events:none;z-index:-1;opacity:.2;",
    ".sideart{position:fixed;top:70px;bottom:0;width:min(36vw,620px);pointer-events:none;z-index:-1;opacity:.2;")
rep(".sideart.l{left:-24px;", ".sideart.l{left:-5vw;")
rep(".sideart.r{right:-24px;", ".sideart.r{right:-5vw;")
rep("@media(max-width:1240px){.sideart{display:none}}", "@media(max-width:1000px){.sideart{display:none}}\n@media(max-width:1240px){.sideart{opacity:.12}}")
rep("@media(prefers-reduced-motion:reduce){.cf[data-fo]::before,.cf[data-fo]::after{animation:none!important}.deck .card-fg{transition:none}}",
    """.cf[data-fo="r"]::before{background:linear-gradient(120deg,transparent 30%,rgba(190,215,255,.30) 50%,transparent 70%);mix-blend-mode:screen}
.cf[data-fo="dur"]::before{background:conic-gradient(from 0deg at 50% 60%,rgba(255,120,200,.22),rgba(120,200,255,.26),rgba(255,240,140,.22),rgba(160,255,200,.22),rgba(255,120,200,.22));mix-blend-mode:screen}
.bigcard .cf[data-fo="dur"]::before,.pv .cf[data-fo="dur"]::before{animation:fhue 8s linear infinite}
@media(prefers-reduced-motion:reduce){.cf[data-fo]::before,.cf[data-fo]::after{animation:none!important}.deck .card-fg{transition:none}}""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch18 ok')
