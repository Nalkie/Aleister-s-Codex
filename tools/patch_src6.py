"""Magic touches: tier crests, livelier deck rows (featured, stat chips), recipe header with stat tiles and a gallery view.
Run once from build/ (backs src.html up first)."""
import re, shutil

shutil.copy('src.html', 'src.before_patch6.html')
s = open('src.html', encoding='utf-8').read()
magic = open('tools/style_magic.css', encoding='utf-8').read()


def rep(a, b):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, 1)


# ---- css ----
rep('</style>', magic + '</style>')

# ---- decklist (gallery + stats) ----
i = s.index('function dlQuotas(l){')
j = s.index('const how=(html')
s = s[:i] + r'''let RV='gal'; try{ RV=localStorage.getItem('rv')||'gal'; }catch(e){}
function dlQuotas(l){
  const used={1:0,2:0,3:0};
  for(const s of ['main','extra','side']) for(const [n,k] of l[s]){ const c=CARDS[canon(n)]; if(c&&c[C.DL]>=1&&c[C.DL]<=3) used[c[C.DL]]+=k; }
  if(!used[1]&&!used[2]&&!used[3]) return '<p class="rnote">Esta lista no usa cartas de la lista de prohibidas y limitadas de Duel Links.</p>';
  return `<div class="quota"><strong>Cupos de límite</strong>${[1,2,3].map(v=>`<span>${banIcon(v,dlTip(v))} ${used[v]} de ${v}</span>`).join('')}</div><p class="rnote">Las cartas del mismo límite comparten el cupo: con Límite 3 podés jugar 3 copias en total entre todas ellas (por ejemplo 2 de una y 1 de otra).</p>`;
}
const rstat=(label,value,extra='')=>`<div class="rstat"><small>${label}</small><b>${value}</b>${extra}</div>`;
function tile(n,k,pr,kind,secKey){
  const c=CARDS[canon(n)]; const i=kind==='dl'?DLD.cards[n]:null;
  let meta='';
  if(kind==='dl') meta=`${i&&i.r?i.r:''}${pr!=null?' · '+pr+'%':''}`;
  else if(kind==='gen'){ const g=c?c[C.GEN]:0; meta=g>0?g+' pts':g===-1?'? pts':''; }
  else meta=c&&c[C.PR]>0?'$'+c[C.PR]:'';
  const ban=kind==='gen'?'':banMark(n,kind);
  const bi=/class="bi/.test(ban)?ban:'';
  return `<button class="tile ${k>1?'k'+Math.min(k,3):''} s-${secKey}${i&&i.r?' r-'+i.r:''}" data-card="${esc(n)}" title="${esc(n)}${kind==='dl'?' · '+esc(dlBadge(n)):''}"><span class="art">${thumb(n)}<b class="cnt">×${k}</b>${bi}</span><span class="tn">${esc(n)}</span><span class="tm">${esc(meta)}</span></button>`;
}
function decklist(l,kind='tcg'){
  const secs=[['main','Main Deck',l.main],['extra','Extra Deck',l.extra],['side','Side Deck',l.side]];
  const sec=([key,t,arr])=>{ if(!arr.length) return ''; const tot=arr.reduce((a,x)=>a+x[1],0);
    const body = RV==='gal'
      ? `<div class="gal">${arr.map(([n,k,pr])=>tile(n,k,pr,kind,key)).join('')}</div>`
      : `<div class="dcol">${arr.map(([n,k,pr])=>`<button class="drow" data-card="${esc(n)}"><b>${k}</b>${thumb(n)}<span class="nm">${esc(n)}</span>${rowExtra(kind,n,pr)}</button>`).join('')}</div>`;
    return `<div class="dsec ${key}"><h4>${t} · ${tot} cartas</h4>${body}</div>`; };
  const cnt=k=>l[k].reduce((a,x)=>a+x[1],0);
  const sizes=`${cnt('main')}<em>main</em> · ${cnt('extra')}<em>extra</em>${cnt('side')?` · ${cnt('side')}<em>side</em>`:''}`;
  let stats='', note='';
  if(kind==='dl'){
    stats=rstat('Gemas',l.gems!=null?fmtNum(l.gems):'s/d')+rstat('Dinero real',l.usd?'US$ '+l.usd:'0')+rstat('Mediana del arquetipo',(l.gemsMed!=null?fmtNum(l.gemsMed):'s/d')+(l.usdMed?`<em>+ US$ ${l.usdMed}</em>`:''))+rstat('Skill',`<span style="font-size:.9rem">${esc(l.skill||'sin skill')}</span>`);
    note=`<p class="rnote">Costo estimado por Duel Links Meta. La mediana sale de ${l.n} decks del arquetipo.</p>${dlQuotas(l)}`;
  } else if(kind==='gen'){
    let t=0,unk=0; for(const s of ['main','extra','side']) for(const [n,k] of l[s]){ const c=CARDS[canon(n)]; if(!c) continue; const g=c[C.GEN]; if(g>0) t+=g*k; else if(g===-1) unk+=k; }
    stats=rstat('Puntos Genesys',`${t}<em>/ 100</em>`,`<div class="pbar${t>100?' over':''}"><i style="width:${Math.min(100,t)}%"></i></div>`)+rstat('Cartas',sizes)+(unk?rstat('Sin confirmar',`${unk}<em>cartas</em>`):'');
    note='<p class="rnote">Calculado con los puntos actuales de YuGiOh Meta. Los monstruos Link y Pendulum no se pueden usar en Genesys.</p>';
  } else {
    let t=0,miss=0,lim=0; for(const s of ['main','extra','side']) for(const [n,k] of l[s]){ const c=CARDS[canon(n)]; if(c&&c[C.PR]>0) t+=c[C.PR]*k; else miss+=k; if(c&&c[C.BAN]>=0&&c[C.BAN]<3) lim++; }
    if(l.price) t=l.price;
    stats=rstat('Valor aproximado','US$ '+t.toFixed(0))+rstat('Cartas',sizes)+rstat('Con límite en el TCG',`${lim}<em>cartas</em>`);
    note=`<p class="rnote">${l.price?'Precios de YuGiOh Meta':'Precios de TCGplayer'}${miss&&!l.price?` (sin precio para ${miss} cartas)`:''}. Las marcas rojas son cartas de la banlist del TCG.</p>`;
  }
  const tog=`<div class="seg mini" role="group" aria-label="Vista de la receta"><button data-rv="gal" aria-pressed="${RV==='gal'}">Galería</button><button data-rv="list" aria-pressed="${RV==='list'}">Lista</button></div>`;
  return `<div class="recipe"><div class="rhead"><div><h3>Receta ${kind==='dl'?'más usual':'de referencia'}</h3><p class="who">${esc(l.who)}</p></div>${tog}</div><div class="rstats">${stats}</div>${note}<div class="decklist">${secs.map(sec).join('')}</div></div>`;
}
''' + s[j:]

# ---- deck rows + tier crest ----
i = s.index('function deckRow(d,i,pctVal,barVal,metaTxt,body){')
j = s.index('const fmt=n=>')
s = s[:i] + r'''function deckRow(d,i,pctVal,barVal,metaTxt,body){
  const art=artOf(d.art);
  const chips=metaTxt.split(' · ').map(x=>`<i class="${/victoria/.test(x)?'w':/top 4/.test(x)?'t':''}">${x}</i>`).join('');
  return `<details class="deck${i===1?' feat':''}" data-id="${esc(d.id||d.n)}"><summary>${art?`<img class="art-bg" src="${art}" alt="" loading="lazy">`:'<div class="artph"></div>'}
    <span class="rank">${i}</span><span class="dname">${esc(d.n)}</span>
    <span class="bar"><span class="track"><span class="fill" style="width:${barVal.toFixed(1)}%"></span></span><span class="pct">${pctVal}</span></span>
    <span class="meta">${chips}</span></summary><div class="body">${body}</div></details>`;
}
const ROMAN={T1:'I',T2:'II',T3:'III',R:'IV',N:'–'};
function grouped(decks,render){
  const order=['T1','T2','T3','R','N']; let out='', k=0;
  for(const t of order){
    const g=decks.filter(d=>d.tier===t); if(!g.length) continue;
    out+=`<div class="tier ${TIERS[t][0]}"><div class="tierhead"><span class="crest">${ROMAN[t]}</span><span class="ttxt"><b>${TIERS[t][1]}</b><small>${TIERS[t][2]}</small></span><span class="tcount">${g.length} ${g.length===1?'mazo':'mazos'}</span></div>${g.map(d=>render(d,++k)).join('')}</div>`;
  }
  return out;
}
''' + s[j:]

# ---- outside-meta section used a tierbar: use a crest too ----
rep('<div class="t-n"><div class="tierbar">Ganaron sin ser meta <small>${out.length} arquetipos</small></div>',
    '<div class="tier t-n"><div class="tierhead"><span class="crest">★</span><span class="ttxt"><b>Ganaron sin ser meta</b><small>por debajo del tier 3</small></span><span class="tcount">${out.length} arquetipos</span></div>')
rep('<div class="t-n"><div class="tierbar">Ranking por uso <small>Rush no tiene tiers</small></div>',
    '<div class="tier t-n"><div class="tierhead"><span class="crest">R</span><span class="ttxt"><b>Ranking por uso</b><small>Rush no tiene tiers</small></span><span class="tcount">${sorted.length} mazos</span></div>')

# ---- render: keep open decks when the view toggles; click handler ----
rep("function render(focusId){\n  document.body.className=mode;",
    "function render(focusId){\n  const openIds=new Set([...document.querySelectorAll('details.deck[open]')].map(x=>x.dataset.id));\n  document.body.className=mode;")
rep("  const ty=$('#ty'); if(ty) ty.value=EX.type;",
    "  document.querySelectorAll('details.deck').forEach(x=>{ if(openIds.has(x.dataset.id)) x.open=true; });\n  const ty=$('#ty'); if(ty) ty.value=EX.type;")
rep("  else if(d.f){ dlFormat=d.f; render(); }",
    "  else if(d.rv){ RV=d.rv; try{ localStorage.setItem('rv',RV); }catch(e){} render(); }\n  else if(d.f){ dlFormat=d.f; render(); }")
open('src.html', 'w', encoding='utf-8').write(s)
print('patched', len(s))
