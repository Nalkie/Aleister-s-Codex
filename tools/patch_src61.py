"""Enlaces profundos: la navegación vive en la URL (?mode=…&view=…&deck=…) con la History API, para compartir en foros y Discord.
  * mode : tcg | ocg | edison | goat | hat | genesys | duellinks | cards | boxes | obtain | engines | events | builder | guide | banlist
  * view : meta (por defecto) | staples (cartas más usadas) | engines (motores y arquetipos): baja a esa sección
  * deck : el mazo abierto (slug del nombre, p. ej. deck=elfnote)         * card : la carta elegida en el buscador (mode=cards)
Al cargar se lee la URL y la página arranca en esa pestaña, con ese mazo abierto.  Cambiar de pestaña o de formato hace pushState (el botón Atrás vuelve);
abrir un mazo, cambiar de sección o elegir una carta hace replaceState.  Los enlaces viejos (#tcg, #ex…) siguen andando y se reescriben.
Backup: src.before_patch61.html."""
import shutil

shutil.copy('src.html', 'src.before_patch61.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


# ---- 1. el módulo de rutas (antes de render) ----
rep("function render(focusId){", r"""/* ---------- enlaces profundos (?mode=…&view=…&deck=…) ---------- */
const ROUTE_MODES={tcg:['tcg','adv'],ocg:['tcg','ocg'],edison:['tcg','edison'],goat:['tcg','goat'],hat:['tcg','hat'],genesys:['gen',''],duellinks:['dl',''],cards:['ex',''],boxes:['sets',''],obtain:['obt',''],engines:['eng',''],events:['ev',''],builder:['deck',''],guide:['guide',''],banlist:['ban','']};
const ROUTE_VIEWS=['meta','staples','engines'];
const ROUTE_OLD={tcg:'tcg',gen:'genesys',dl:'duellinks',ex:'cards',sets:'boxes',obt:'obtain',eng:'engines',deck:'builder',guide:'guide',ev:'events',ban:'banlist'};   // los #hash de antes
const deckSlug=n=>slug(String(n)).replace(/^-+|-+$/g,'');
function routeParse(search,hash){          // URL -> {name (mode de la URL), mode (interno), tcgf, view, deck, card}
  const q=new URLSearchParams(search||''), out={name:'',mode:'',tcgf:'',view:'meta',deck:'',card:''};
  let m=(q.get('mode')||'').toLowerCase();
  if(!ROUTE_MODES[m]&&ROUTE_OLD[m]) m=ROUTE_OLD[m];
  if(!ROUTE_MODES[m]) m=ROUTE_OLD[String(hash||'').replace(/^#/,'')]||'';
  if(!ROUTE_MODES[m]) return out;
  out.name=m; out.mode=ROUTE_MODES[m][0]; out.tcgf=ROUTE_MODES[m][1];
  const v=(q.get('view')||'').toLowerCase(); if(ROUTE_VIEWS.includes(v)) out.view=v;
  out.deck=deckSlug(q.get('deck')||''); out.card=out.mode==='ex'?(q.get('card')||''):'';
  return out;
}
function routeName(mode,tcgf){             // modo interno -> nombre en la URL
  if(mode==='tcg') return tcgf&&tcgf!=='adv'?tcgf:'tcg';
  return Object.keys(ROUTE_MODES).find(k=>ROUTE_MODES[k][0]===mode)||'tcg';
}
function routeBuild(st){                   // estado -> '?mode=…' (lo que es por defecto no se escribe)
  const q=new URLSearchParams(); q.set('mode',routeName(st.mode,st.tcgf));
  if(st.view&&st.view!=='meta'&&ROUTE_VIEWS.includes(st.view)) q.set('view',st.view);
  if(st.deck) q.set('deck',st.deck);
  if(st.mode==='ex'&&st.card) q.set('card',st.card);
  return '?'+q.toString();
}
const ROUTE={last:null,deck:'',view:'meta',pending:null,skip:false,vsec:[['Cartas más usadas','staples'],['Motores y arquetipos','engines']]};
function routeFromUrl(){                   // aplica la URL al estado de la página (carga inicial y botones Atrás / Adelante)
  const r=routeParse(location.search,location.hash); if(!r.mode) return false;
  mode=r.mode; if(r.tcgf) TCGF=r.tcgf;
  ROUTE.deck=r.deck; ROUTE.view=r.view; ROUTE.pending=(r.deck||r.view!=='meta')?{deck:r.deck,view:r.view,tries:0}:null;
  if(r.card){ EX.card=r.card; EX.view='card'; EX.q=''; }
  return true;
}
function routeSync(){                      // estado -> URL: pushState si cambió la pestaña o el formato, replaceState si no
  try{
    const st={mode,tcgf:mode==='tcg'?TCGF:'',view:ROUTE.view,deck:ROUTE.deck,card:EX.card};
    const qs=routeBuild(st), key=mode+'|'+(mode==='tcg'?TCGF:''), url=location.pathname+qs;
    if(!ROUTE.skip && (location.search!==qs||location.hash)){
      if(ROUTE.last&&ROUTE.last!==key) history.pushState(null,'',url); else history.replaceState(null,'',url);
    }
    ROUTE.last=key; ROUTE.skip=false;
  }catch(e){}
}
function routeMark(){                      // ids de sección y botones para saltar entre «Mejores mazos», «Cartas más usadas» y «Motores»
  document.querySelectorAll('#app section > .phead > h2').forEach(h=>{ const tx=h.textContent.trim(); for(const [es,v] of ROUTE.vsec) if(tx===es) h.closest('section').id='view-'+v; });
  const first=document.querySelector('#app section.first > .phead');
  if(first&&!document.querySelector('.vnav')&&(document.getElementById('view-staples')||document.getElementById('view-engines'))){
    const b=(v,l)=>document.getElementById('view-'+v)||v==='meta'?`<button data-rview="${v}" aria-pressed="${ROUTE.view===v}">${l}</button>`:'';
    first.insertAdjacentHTML('afterend',`<div class="seg mini vnav" role="group" aria-label="Sección">${b('meta','Mejores mazos')}${b('staples','Cartas más usadas')}${b('engines','Motores y arquetipos')}</div>`);
  }
  document.querySelectorAll('details.deck').forEach(x=>{ if(!x.dataset.slug) x.dataset.slug=deckSlug((x.querySelector('.dname')||{}).textContent||x.dataset.id); });
}
function routePending(){                   // cuando por fin existen el mazo o la sección del enlace: se abren y se baja hasta ahí
  const p=ROUTE.pending; if(!p) return;
  let done=true;
  if(p.deck){
    const row=[...document.querySelectorAll('details.deck')].find(x=>x.dataset.slug===p.deck);
    if(row){ row.open=true; ROUTE.deck=p.deck; p.deck=''; setTimeout(()=>row.scrollIntoView({block:'start'}),120); } else done=false;
  } else if(p.view&&p.view!=='meta'){
    const el=document.getElementById('view-'+p.view);
    if(el){ p.view='meta'; setTimeout(()=>el.scrollIntoView({block:'start'}),120); } else done=false;
  }
  if(done||++p.tries>12) ROUTE.pending=null;
}
function routeView(v){                     // botón de sección
  ROUTE.pending=null; ROUTE.view=v;
  const el=v==='meta'?document.querySelector('#app section.first'):document.getElementById('view-'+v);
  if(el) el.scrollIntoView({behavior:'smooth',block:'start'});
  document.querySelectorAll('[data-rview]').forEach(b=>b.setAttribute('aria-pressed',b.dataset.rview===v));
  routeSync();
}
document.addEventListener('click',e=>{     // abrir o cerrar un mazo: queda en la URL (el estado nuevo es el contrario al de ahora)
  const sm=e.target.closest&&e.target.closest('details.deck > summary'); if(!sm) return;
  const d=sm.parentElement, slugv=d.dataset.slug||deckSlug((d.querySelector('.dname')||{}).textContent||'');
  ROUTE.pending=null;
  if(!d.open) ROUTE.deck=slugv; else if(ROUTE.deck===slugv) ROUTE.deck='';
  routeSync();
},true);
window.addEventListener('popstate',()=>{ if(routeFromUrl()){ ROUTE.skip=true; render(); window.scrollTo(0,0); } });
function render(focusId){""")

# ---- 2. render: reemplaza el hash viejo por la ruta, marca las secciones y abre lo que pide el enlace ----
rep("  try{ history.replaceState(null,'','#'+mode); }catch(e){}\n", "  routeMark(); routePending(); routeSync();\n")

# ---- 3. la fila de mazo lleva su slug ----
rep("""<details class="deck${i===1?' feat':''}" data-id="${esc(d.id||d.n)}">""", """<details class="deck${i===1?' feat':''}" data-id="${esc(d.id||d.n)}" data-slug="${deckSlug(d.n)}">""")

# ---- 4. los clics de navegación sueltan lo pendiente y el botón de sección ----
rep("  if(d.mode){ mode=d.mode; render(); window.scrollTo(0,0); }", "  if(d.rview){ routeView(d.rview); return; }\n  if(d.mode||d.tcgf||d.gotcg||d.gotab){ ROUTE.pending=null; ROUTE.deck=''; ROUTE.view='meta'; }\n  if(d.mode){ mode=d.mode; render(); window.scrollTo(0,0); }")

# ---- 5. al cargar: la URL manda ----
rep("const h=location.hash.slice(1); if(MODES[h]) mode=h;", "if(!routeFromUrl()){ const h=location.hash.slice(1); if(MODES[h]) mode=h; }")

css = '''/* sección dentro de la página */
.vnav{margin:var(--s3) 0 0}
#app section[id^="view-"]{scroll-margin-top:150px}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 61 ok')
