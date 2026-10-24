"""Deck builder: build, validate by format, save in the browser, import (YDK, YDKE, text lists), export (YDK, YDKE, PNG).
Run once from build/ (backs src.html up first)."""
import re, shutil

shutil.copy('src.html', 'src.before_patch7.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert a in s, a[:80]
    s = s.replace(a, b, cnt)


# ---------- css ----------
CSS = r'''
/* ====== constructor de mazos ====== */
body.deck{--accent:var(--ac-tool)}
.dkbar{display:flex;flex-wrap:wrap;gap:var(--s3);align-items:center;margin-top:var(--s5)}
.dkbar .seg{margin:0}
.dkbar input[type="text"]{flex:1 1 200px;min-height:var(--ctl);padding:0 var(--s4);border-radius:var(--r2);border:1px solid var(--line2);background:var(--surface);color:var(--fg);font:600 1rem var(--f-body)}
.abtn{display:inline-flex;align-items:center;gap:var(--s2);min-height:38px;padding:0 var(--s4);border-radius:99px;border:1px solid var(--line2);background:var(--surface);font:600 .85rem var(--f-body);cursor:pointer;color:var(--fg);transition:border-color .15s,background .15s,color .15s}
.abtn:hover{border-color:var(--accent)}
.abtn.pri{background:var(--accent);border-color:var(--accent);color:var(--bg);box-shadow:0 8px 22px -10px var(--accent)}
.abtn.danger:hover{border-color:var(--red);color:var(--red)}
.dkgrid{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,1fr);gap:var(--s5);margin-top:var(--s5);align-items:start}
.dkdeck,.dkpick{background:linear-gradient(180deg,var(--surface),color-mix(in srgb,var(--surface) 88%,var(--surface2)));border:1px solid var(--line2);border-radius:var(--r);padding:var(--s5);display:grid;gap:var(--s4)}
.dkpick{position:sticky;top:132px;max-height:calc(100vh - 150px);overflow:auto}
.dkstats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:var(--s2)}
.dkissues{display:flex;flex-wrap:wrap;gap:var(--s2)}
.dkissues span{font:500 .78rem var(--f-body);padding:4px 12px;border-radius:99px;border:1px solid color-mix(in srgb,var(--red) 55%,transparent);background:color-mix(in srgb,var(--red) 10%,transparent);color:var(--fg)}
.dkissues span.ok{border-color:color-mix(in srgb,var(--ac-dl) 55%,transparent);background:color-mix(in srgb,var(--ac-dl) 12%,transparent)}
.dkmsg{font-size:.88rem;color:var(--accent);min-height:1.2em;margin:0}
.dkempty{padding:var(--s5);border:1px dashed var(--line2);border-radius:var(--r2);color:var(--muted);text-align:center;font-size:.9rem}
.tile .ctl{display:flex;gap:6px;justify-content:center}
.tile .ctl i{font-style:normal;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;border:1px solid var(--line2);background:var(--surface2);font:700 .9rem var(--f-body);color:var(--fg);cursor:pointer}
.tile .ctl i:hover{border-color:var(--accent);color:var(--accent)}
.tile.add .art .th{border-color:var(--line2)}
.tile.add:hover .art{box-shadow:0 16px 30px -12px var(--accent)}
.tile.add .plus{position:absolute;right:-6px;top:-6px;z-index:2;width:24px;height:24px;border-radius:50%;display:grid;place-items:center;background:var(--accent);color:var(--bg);font:800 .95rem var(--f-body);opacity:0;transform:scale(.6);transition:opacity .15s,transform .15s}
.tile.add:hover .plus{opacity:1;transform:none}
.modal{position:fixed;inset:0;z-index:60;display:grid;place-items:center;padding:var(--s4);background:color-mix(in srgb,var(--bg) 70%,#000 30%);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
.mbox{width:min(760px,100%);max-height:calc(100vh - 32px);overflow:auto;border-radius:var(--r);border:1px solid var(--line2);background:var(--surface);padding:var(--s5);display:grid;gap:var(--s4);box-shadow:0 40px 100px -30px var(--accent)}
.mbox header{display:flex;justify-content:space-between;align-items:center;gap:var(--s3)}
.mbox h3{font-size:1.15rem}
.mbox textarea{width:100%;min-height:200px;resize:vertical;border-radius:var(--r2);border:1px solid var(--line2);background:var(--surface2);color:var(--fg);padding:var(--s3);font:500 .8rem var(--f-data)}
.pngprev{width:100%;border-radius:var(--r2);border:1px solid var(--line2)}
.srow{display:flex;align-items:center;gap:var(--s3);justify-content:space-between;border:1px solid var(--line);border-radius:var(--r2);padding:var(--s3) var(--s4);background:var(--surface2)}
.srow b{font:700 .95rem var(--f-display)}
.srow small{display:block;color:var(--muted);font:500 .7rem var(--f-data)}
.srow .acts{display:flex;gap:var(--s2);flex-wrap:wrap}
.rhead .abtn{min-height:32px;font-size:.78rem}
@media(max-width:900px){.dkgrid{grid-template-columns:1fr}.dkpick{position:static;max-height:none}}
'''
rep('</style>', CSS + '</style>')

# ---------- nav tool + body class + modes ----------
rep('<button class="tool" role="tab" id="tab-ban" data-mode="ban">',
    '<button class="tool" role="tab" id="tab-deck" data-mode="deck"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="4" y="3" width="12" height="17" rx="2"/><path d="M8 7 H12 M8 11 H12 M19 8 V21 H9"/></svg>Constructor</button>\n    <button class="tool" role="tab" id="tab-ban" data-mode="ban">')
rep("const MODES = {tcg:['TCG',viewTCG],gen:['Genesys',viewGEN],dl:['Duel Links',viewDL],ex:['Cartas',viewEX],sets:['Cajas y sets',viewSets],ban:['Banlist',viewBan]};",
    "const MODES = {tcg:['TCG',viewTCG],gen:['Genesys',viewGEN],dl:['Duel Links',viewDL],ex:['Cartas',viewEX],sets:['Cajas y sets',viewSets],deck:['Constructor',viewDeck],ban:['Banlist',viewBan]};")
rep("(DBINFO||!['ex','sets','ban'].includes(mode))", "(DBINFO||!['ex','sets','ban','deck'].includes(mode))")
rep("const C = {CAT:0,SH:1,CE:2,BAN:3,DL:4,GEN:5,CH:6,FL:7,PR:8};", "const C = {CAT:0,SH:1,CE:2,BAN:3,DL:4,GEN:5,CH:6,FL:7,PR:8,ID:9};")

# ---------- recipes -> builder button ----------
rep("function decklist(l,kind='tcg'){\n", "const RECIPES=[];\nfunction decklist(l,kind='tcg'){\n  const rIdx=RECIPES.push({l,kind})-1;\n")
rep("""const tog=`<div class="seg mini" role="group" aria-label="Vista de la receta">""", """const tog=`<div style="display:flex;gap:var(--s2);flex-wrap:wrap;align-items:center"><button class="abtn pri" data-todeck="${rIdx}">Abrir en el constructor</button><div class="seg mini" role="group" aria-label="Vista de la receta">""")
rep("""<button data-rv="list" aria-pressed="${RV==='list'}">Lista</button></div>`;""", """<button data-rv="list" aria-pressed="${RV==='list'}">Lista</button></div></div>`;""")
rep("function render(focusId){\n", "function render(focusId){\n  RECIPES.length=0;\n")
# recipes need names for the builder
rep("    const list={kind:fmt==='gen'?'gen':'tcg',price:w.price,", "    const list={kind:fmt==='gen'?'gen':'tcg',name,price:w.price,")
rep("    const list={kind:'dl',who:", "    const list={kind:'dl',name:type,who:")

# ---------- builder code ----------
BUILDER = r'''/* ---------- CONSTRUCTOR DE MAZOS ---------- */
const DK={fmt:'tcg',name:'Mi mazo',main:{},extra:{},side:{},target:'auto',q:'',type:'all',limit:48,modal:null,msg:'',png:'',imp:'',bk:'',tab:'ydk',saved:[]};
const SECS=['main','extra','side'];
const SEC_ES={main:'Main Deck',extra:'Extra Deck',side:'Side Deck'};
const FMT_ES={tcg:'TCG',gen:'Genesys',dl:'Duel Links'};
function dkLoad(){ try{ DK.saved=JSON.parse(localStorage.getItem('codex_decks')||'[]'); }catch(e){ DK.saved=[]; }
  try{ const d=JSON.parse(localStorage.getItem('codex_draft')||'null'); if(d) Object.assign(DK,{fmt:d.fmt||'tcg',name:d.name||'Mi mazo',main:d.main||{},extra:d.extra||{},side:d.side||{}}); }catch(e){} }
function dkStoreSaved(){ try{ localStorage.setItem('codex_decks',JSON.stringify(DK.saved)); return true; }catch(e){ DK.msg='Este navegador no permite guardar mazos (almacenamiento bloqueado). Usá Exportar para conservarlo.'; return false; } }
function dkDraft(){ try{ localStorage.setItem('codex_draft',JSON.stringify({fmt:DK.fmt,name:DK.name,main:DK.main,extra:DK.extra,side:DK.side})); }catch(e){} }
dkLoad();
const dkCount=sec=>Object.values(DK[sec]).reduce((a,x)=>a+x,0);
const dkCopies=n=>SECS.reduce((a,s)=>a+(DK[s][n]||0),0);
const dkAll=()=>SECS.flatMap(s=>Object.entries(DK[s]).map(([n,k])=>[n,k,s]));
function dkMax(n){
  const c=CARDS[n]; if(!c) return 0;
  if(DK.fmt==='tcg'){ const b=c[C.BAN]; return b<0?0:b===3?3:b; }
  if(DK.fmt==='gen'){ return c[C.GEN]===-3?0:3; }
  const d=c[C.DL]; return (d<0||d===5||d===0)?0:3;
}
function dkAdd(n,forceSec){
  const c=CARDS[n]; if(!c) return;
  const max=dkMax(n);
  if(dkCopies(n)>=max){ DK.msg=max===0?`${n} no se puede usar en ${FMT_ES[DK.fmt]}.`:`Máximo ${max} ${max===1?'copia':'copias'} de ${n} en ${FMT_ES[DK.fmt]}.`; return; }
  const sec=forceSec||(DK.target==='side'?'side':(c[C.CAT]==='e'?'extra':'main'));
  if(sec==='extra'&&c[C.CAT]!=='e'){ DK.msg='Solo los monstruos del Extra Deck van en el Extra Deck.'; return; }
  if(sec==='main'&&c[C.CAT]==='e'){ DK.msg='Los monstruos del Extra Deck van en el Extra Deck o en el Side Deck.'; return; }
  DK[sec][n]=(DK[sec][n]||0)+1; DK.msg=''; dkDraft();
}
function dkDec(n,sec){ if(!DK[sec][n]) return; DK[sec][n]--; if(!DK[sec][n]) delete DK[sec][n]; DK.msg=''; dkDraft(); }
function dkPoints(){ let t=0,unk=0; for(const [n,k] of dkAll()){ const g=CARDS[n]?CARDS[n][C.GEN]:0; if(g>0) t+=g*k; else if(g===-1) unk+=k; } return {t,unk}; }
function dkIssues(){
  const out=[], m=dkCount('main'), e=dkCount('extra'), sd=dkCount('side');
  if(DK.fmt==='dl'){ if(m<30||m>40) out.push(`Main Deck: ${m} cartas (las recetas de Duel Links usan 30)`); }
  else{ if(m<40) out.push(`Main Deck: ${m} cartas, el mínimo es 40`); if(m>60) out.push(`Main Deck: ${m} cartas, el máximo es 60`); if(e>15) out.push(`Extra Deck: ${e} cartas, el máximo es 15`); if(sd>15) out.push(`Side Deck: ${sd} cartas, el máximo es 15`); }
  const bad=new Set();
  for(const [n] of dkAll()){ if(bad.has(n)) continue; const max=dkMax(n), k=dkCopies(n);
    if(max===0){ out.push(`${n}: no se puede usar en ${FMT_ES[DK.fmt]}`); bad.add(n); }
    else if(k>max){ out.push(`${n}: ${k} copias, el máximo es ${max}`); bad.add(n); } }
  if(DK.fmt==='gen'){ const {t,unk}=dkPoints(); if(t>100) out.push(`Genesys: ${t} puntos, el tope es 100`); if(unk) out.push(`${unk} cartas con puntos sin confirmar`); }
  if(DK.fmt==='dl'){ const used={1:0,2:0,3:0}; for(const [n,k] of dkAll()){ const d=CARDS[n]?CARDS[n][C.DL]:-1; if(d>=1&&d<=3) used[d]+=k; }
    for(const v of [1,2,3]) if(used[v]>v) out.push(`Límite ${v}: ${used[v]} copias entre todas, el máximo es ${v}`); }
  return out;
}
/* ids y formatos de intercambio */
let ID2N=null;
function idMap(){ if(!ID2N){ ID2N={}; for(const n of NAMES){ const id=CARDS[n][C.ID]; if(id) ID2N[id]=n; } } return ID2N; }
const dkIds=sec=>Object.entries(DK[sec]).flatMap(([n,k])=>Array(k).fill(CARDS[n]?CARDS[n][C.ID]:0)).filter(Boolean);
const dkNoId=()=>dkAll().filter(([n])=>!(CARDS[n]&&CARDS[n][C.ID])).reduce((a,[,k])=>a+k,0);
function dkYdk(){ return `#created by Aleister's Codex\n#main\n${dkIds('main').join('\n')}\n#extra\n${dkIds('extra').join('\n')}\n!side\n${dkIds('side').join('\n')}\n`; }
function b64(ids){ const buf=new Uint8Array(ids.length*4); ids.forEach((id,i)=>{ buf[i*4]=id&255; buf[i*4+1]=(id>>8)&255; buf[i*4+2]=(id>>16)&255; buf[i*4+3]=(id>>>24)&255; }); let bin=''; buf.forEach(x=>bin+=String.fromCharCode(x)); return btoa(bin); }
function unb64(t){ try{ const bin=atob(t); const ids=[]; for(let i=0;i+3<bin.length;i+=4) ids.push(bin.charCodeAt(i)|(bin.charCodeAt(i+1)<<8)|(bin.charCodeAt(i+2)<<16)|(bin.charCodeAt(i+3)<<24)>>>0); return ids; }catch(e){ return []; } }
function dkYdke(){ return 'ydke://'+SECS.map(s=>b64(dkIds(s))).join('!')+'!'; }
function dkText(){ return SECS.map(s=>{ const rows=Object.entries(DK[s]); return rows.length?`# ${SEC_ES[s]}\n`+rows.map(([n,k])=>`${k}x ${n}`).join('\n'):''; }).filter(Boolean).join('\n\n'); }
function dkImport(text){
  const t=(text||'').trim(); if(!t) return 'No hay nada para importar.';
  const idm=idMap(), nm={}; for(const n of NAMES) nm[n.toLowerCase()]=n;
  const next={main:{},extra:{},side:{}}; let miss=0, ok=0;
  const put=(sec,name,k)=>{ if(!name){ miss+=k; return; } const c=CARDS[name]; const s=(sec==='main'&&c&&c[C.CAT]==='e')?'extra':sec; next[s][name]=(next[s][name]||0)+k; ok+=k; };
  if(/^ydke:\/\//i.test(t)){
    const parts=t.replace(/^ydke:\/\//i,'').split('!');
    ['main','extra','side'].forEach((sec,i)=>unb64(parts[i]||'').forEach(id=>put(sec,idm[id],1)));
  } else if(/^(#main|#created|!side|#extra)/im.test(t)||/^\d{5,9}\s*$/m.test(t)&&!/[a-zA-Z]{3}/.test(t.replace(/#.*|!.*/g,''))){
    let sec='main';
    for(const line of t.split(/\r?\n/)){ const l=line.trim(); if(!l) continue;
      if(/^#main/i.test(l)){ sec='main'; continue; } if(/^#extra/i.test(l)){ sec='extra'; continue; } if(/^!side/i.test(l)){ sec='side'; continue; } if(l[0]==='#') continue;
      if(/^\d+$/.test(l)) put(sec,idm[+l],1); }
  } else {
    let sec='main';
    for(const line of t.split(/\r?\n/)){ const l=line.trim(); if(!l) continue;
      const h=l.match(/^#?\s*(main|extra|side)\b/i); if(h&&!/^\d/.test(l)){ sec=h[1].toLowerCase(); continue; }
      const m=l.match(/^(\d+)\s*x?\s+(.+)$/i); const k=m?+m[1]:1, name=(m?m[2]:l).trim();
      put(sec,nm[name.toLowerCase()],k); }
  }
  if(!ok) return 'No pude reconocer ninguna carta. Pegá un YDK, un enlace ydke:// o una lista como "3x Ash Blossom & Joyous Spring".';
  DK.main=next.main; DK.extra=next.extra; DK.side=next.side; dkDraft();
  return `Importé ${ok} cartas${miss?` (${miss} no se reconocieron)`:''}.`;
}
/* imagen PNG del mazo */
async function dkPng(){
  const all=SECS.map(s=>[s,Object.entries(DK[s]).flatMap(([n,k])=>Array(k).fill(n))]).filter(([,a])=>a.length);
  const T=104,G=10,COLS=12,PAD=44,W=PAD*2+COLS*(T+G)-G;
  const rows=all.reduce((a,[,arr])=>a+Math.ceil(arr.length/COLS),0);
  const H=170+all.length*52+rows*(T+G)+60;
  const cv=document.createElement('canvas'); cv.width=W; cv.height=H; const x=cv.getContext('2d');
  const acc={tcg:'#4ee1ff',gen:'#b78bff',dl:'#3ddc97'}[DK.fmt];
  const g=x.createLinearGradient(0,0,W,H); g.addColorStop(0,'#0b1030'); g.addColorStop(1,'#070a1c'); x.fillStyle=g; x.fillRect(0,0,W,H);
  const rg=x.createRadialGradient(W,0,0,W,0,W*.7); rg.addColorStop(0,acc+'55'); rg.addColorStop(1,'transparent'); x.fillStyle=rg; x.fillRect(0,0,W,H);
  try{ await document.fonts.ready; }catch(e){}
  x.fillStyle='#eef1ff'; x.font='800 46px Unbounded, system-ui, sans-serif'; x.textBaseline='alphabetic'; x.fillText(DK.name||'Mi mazo',PAD,84);
  const {t}=dkPoints(); x.fillStyle=acc; x.font='500 22px "JetBrains Mono", monospace';
  x.fillText(`${FMT_ES[DK.fmt]}  ·  Main ${dkCount('main')}  ·  Extra ${dkCount('extra')}  ·  Side ${dkCount('side')}${DK.fmt==='gen'?`  ·  ${t} pts`:''}`,PAD,122);
  const sheets={}; const need=new Set();
  for(const [,arr] of all) for(const n of arr){ const c=CARDS[n]; if(c&&c[C.SH]!==-1) need.add(c[C.SH]>=0?'sheets/s'+c[C.SH]+'.jpg':'sheets/l'+(-2-c[C.SH])+'.jpg'); }
  await Promise.all([...need].map(u=>new Promise(res=>{ const im=new Image(); im.onload=()=>{ sheets[u]=im; res(); }; im.onerror=()=>res(); im.src=u; })));
  let y=150;
  for(const [sec,arr] of all){
    x.fillStyle='#eef1ff'; x.font='700 24px Unbounded, system-ui, sans-serif'; x.fillText(`${SEC_ES[sec]} · ${arr.length}`,PAD,y+28); y+=44;
    arr.forEach((n,i)=>{ const cx=PAD+(i%COLS)*(T+G), cy=y+Math.floor(i/COLS)*(T+G); const c=CARDS[n];
      x.save(); x.beginPath(); x.roundRect(cx,cy,T,T,12); x.clip();
      x.fillStyle='#151b44'; x.fillRect(cx,cy,T,T);
      if(c&&c[C.SH]!==-1){ const hi=c[C.SH]>=0, cols=hi?COLS_HI:LCOLS_, cell=hi?112:72; const im=sheets[hi?'sheets/s'+c[C.SH]+'.jpg':'sheets/l'+(-2-c[C.SH])+'.jpg'];
        if(im) x.drawImage(im,(c[C.CE]%cols)*cell,Math.floor(c[C.CE]/cols)*cell,cell,cell,cx,cy,T,T); }
      else { x.fillStyle='#9aa4d6'; x.font='700 22px system-ui'; x.textAlign='center'; x.fillText(initials(n),cx+T/2,cy+T/2+8); x.textAlign='left'; }
      x.restore(); x.strokeStyle=acc+'88'; x.lineWidth=2; x.beginPath(); x.roundRect(cx,cy,T,T,12); x.stroke(); });
    y+=Math.ceil(arr.length/COLS)*(T+G)+8;
  }
  x.fillStyle='#9aa4d6'; x.font='500 18px "JetBrains Mono", monospace'; x.fillText("Aleister's Codex · "+new Date().toISOString().slice(0,10),PAD,H-24);
  return cv.toDataURL('image/png');
}
const COLS_HI=9, LCOLS_=12;
/* acciones */
async function copyText(text,id){
  try{ await navigator.clipboard.writeText(text); DK.msg='Copiado al portapapeles.'; }
  catch(e){ const el=$('#'+id); if(el){ el.focus(); el.select(); } DK.msg='Tu navegador no deja copiar solo: el texto quedó seleccionado, copialo con Ctrl+C.'; }
}
async function copyPng(){
  try{ const bin=atob(DK.png.split(',')[1]); const u=new Uint8Array(bin.length); for(let i=0;i<bin.length;i++) u[i]=bin.charCodeAt(i);
    await navigator.clipboard.write([new ClipboardItem({'image/png':new Blob([u],{type:'image/png'})})]); DK.msg='Imagen copiada al portapapeles.'; }
  catch(e){ DK.msg='No pude copiar la imagen: guardala con clic derecho (o manteniéndola apretada en el celular).'; }
}
function dkSave(){
  const name=(DK.name||'Mi mazo').trim()||'Mi mazo';
  const rec={id:Date.now().toString(36),name,fmt:DK.fmt,main:DK.main,extra:DK.extra,side:DK.side,ts:new Date().toISOString().slice(0,10)};
  const i=DK.saved.findIndex(x=>x.name===name&&x.fmt===DK.fmt);
  if(i>=0){ rec.id=DK.saved[i].id; DK.saved[i]=rec; } else DK.saved.unshift(rec);
  if(dkStoreSaved()) DK.msg=`Guardé «${name}» en este navegador.`;
}
function dkFromRecipe(r){
  const l=r.l; DK.fmt=r.kind==='dl'?'dl':r.kind==='gen'?'gen':'tcg'; DK.name=l.name||'Receta';
  for(const s of SECS){ DK[s]={}; for(const [n,k] of l[s]) DK[s][n]=(DK[s][n]||0)+k; }
  DK.target='auto'; DK.msg=`Cargué la receta de ${DK.name}. Podés editarla.`; dkDraft();
}
function dkAction(d){
  const a=d.dk;
  if(a==='new'){ DK.main={}; DK.extra={}; DK.side={}; DK.name='Mi mazo'; DK.msg='Mazo nuevo.'; dkDraft(); }
  else if(a==='save') dkSave();
  else if(a==='saved'){ DK.modal='saved'; }
  else if(a==='import'){ DK.modal='import'; DK.imp=''; }
  else if(a==='export'){ DK.modal='export'; DK.tab='ydk'; DK.png=''; }
  else if(a==='close'){ DK.modal=null; DK.msg=''; }
  else if(a==='do-import'){ DK.msg=dkImport(DK.imp); if(/^Importé/.test(DK.msg)) DK.modal=null; }
  else if(a==='clear-target'){ DK.target=d.val; }
}
'''
BUILDER += r'''
function dkTile(n,k,sec){
  return `<div class="tile s-${sec}${k>1?' k'+Math.min(k,3):''}"><span class="art">${thumb(n)}<b class="cnt">×${k}</b>${(()=>{const b=banMark(n,DK.fmt==='dl'?'dl':DK.fmt==='tcg'?'tcg':'');return /class="bi/.test(b)?b:'';})()}</span><span class="tn">${esc(n)}</span>
    <span class="ctl"><i data-dec="${esc(n)}" data-sec="${sec}" title="Quitar una copia" role="button">−</i><i data-inc="${esc(n)}" data-sec="${sec}" title="Agregar una copia" role="button">+</i></span></div>`;
}
function dkModal(){
  if(!DK.modal) return '';
  const head=t=>`<header><h3>${t}</h3><button class="abtn" data-dk="close">Cerrar</button></header>`;
  let body='';
  if(DK.modal==='export'){
    const tabs=[['ydk','YDK'],['ydke','YDKE'],['png','Imagen PNG'],['txt','Lista de texto']];
    const tb=`<div class="seg" style="margin:0">${tabs.map(([k,t])=>`<button data-xt="${k}" aria-pressed="${DK.tab===k}">${t}</button>`).join('')}</div>`;
    let pane='';
    const noId=dkNoId();
    if(DK.tab==='ydk') pane=`<p class="lede">Formato clásico de EDOPro, YGOPro y otros simuladores. Copiá el texto y pegalo en un archivo con extensión <b>.ydk</b>.${noId?` ${noId} cartas sin código no se incluyen.`:''}</p><textarea id="dk-out" readonly>${esc(dkYdk())}</textarea><button class="abtn pri" data-copy="ydk">Copiar YDK</button>`;
    else if(DK.tab==='ydke') pane=`<p class="lede">Enlace corto que aceptan YGOPRODeck, Dueling Nexus y otros importadores: pegalo en su opción de importar.</p><textarea id="dk-out" readonly style="min-height:110px">${esc(dkYdke())}</textarea><button class="abtn pri" data-copy="ydke">Copiar enlace YDKE</button>`;
    else if(DK.tab==='txt') pane=`<p class="lede">Lista legible: sirve para compartir o para volver a importarla acá.</p><textarea id="dk-out" readonly>${esc(dkText())}</textarea><button class="abtn pri" data-copy="txt">Copiar lista</button>`;
    else pane=DK.png?`<img class="pngprev" src="${DK.png}" alt="Imagen del mazo"><p class="lede">Para guardarla: clic derecho sobre la imagen y «Guardar imagen como», o mantenela apretada en el celular. La página no puede iniciar descargas por su cuenta.</p><button class="abtn pri" data-copy="png">Copiar imagen</button>`:'<p class="lede">Generando la imagen…</p>';
    body=tb+pane;
  } else if(DK.modal==='import'){
    body=`<p class="lede">Pegá un archivo YDK, un enlace <b>ydke://</b> o una lista de texto (por ejemplo «3x Ash Blossom &amp; Joyous Spring»). Reemplaza el mazo actual.</p><textarea id="dk-imp" placeholder="#main&#10;14558127&#10;..." >${esc(DK.imp)}</textarea><button class="abtn pri" data-dk="do-import">Importar</button>`;
  } else {
    const rows=DK.saved.map(r=>`<div class="srow"><div><b>${esc(r.name)}</b><small>${FMT_ES[r.fmt]} · ${Object.values(r.main).reduce((a,x)=>a+x,0)}/${Object.values(r.extra).reduce((a,x)=>a+x,0)}/${Object.values(r.side).reduce((a,x)=>a+x,0)} · ${r.ts}</small></div><div class="acts"><button class="abtn pri" data-load="${r.id}">Cargar</button><button class="abtn danger" data-del="${r.id}">Eliminar</button></div></div>`).join('');
    const bk=JSON.stringify(DK.saved);
    body=`${rows||'<div class="dkempty">Todavía no guardaste mazos. Armá uno y tocá «Guardar».</div>'}
      <p class="lede" style="margin-top:var(--s3)">Los mazos se guardan solo en este navegador. Para no perderlos o pasarlos a otro dispositivo, copiá esta copia de seguridad y pegala abajo donde dice «Restaurar».</p>
      <textarea id="dk-bk-out" readonly style="min-height:90px">${esc(bk)}</textarea><button class="abtn" data-copy="bk">Copiar copia de seguridad</button>
      <textarea id="dk-bk" placeholder="Pegá una copia de seguridad para restaurar" style="min-height:70px">${esc(DK.bk)}</textarea><button class="abtn" data-restore="1">Restaurar</button>`;
  }
  const title=DK.modal==='export'?'Exportar mazo':DK.modal==='import'?'Importar mazo':'Mis mazos';
  return `<div class="modal" data-close="1"><div class="mbox" role="dialog" aria-modal="true" aria-label="${title}">${head(title)}${body}<p class="dkmsg">${esc(DK.msg)}</p></div></div>`;
}
function viewDeck(){
  const q=DK.q.trim().toLowerCase();
  const names=NAMES.filter(n=>(!q||n.toLowerCase().includes(q))&&(DK.type==='all'||CARDS[n][C.CAT]===DK.type)&&dkMax(n)>0&&CARDS[n][C.SH]!==-1);
  names.sort((a,b)=>usedCount(b)-usedCount(a)||a.localeCompare(b));
  const shown=names.slice(0,DK.limit);
  const issues=dkIssues(), pts=dkPoints();
  const pickTile=n=>{ const c=CARDS[n]; const b=DK.fmt==='gen'?'':banMark(n,DK.fmt==='dl'?'dl':'tcg'); const bi=/class="bi/.test(b)?b:''; const g=DK.fmt==='gen'&&c[C.GEN]>0?c[C.GEN]+' pts':'';
    return `<button class="tile add" data-add="${esc(n)}" title="${esc(n)}"><span class="art">${thumb(n)}<b class="plus">+</b>${bi}</span><span class="tn">${esc(n)}</span><span class="tm">${g}</span></button>`; };
  const sec=s=>{ const rows=Object.entries(DK[s]); if(!rows.length&&s!=='main') return ''; return `<div class="dsec ${s}"><h4>${SEC_ES[s]} · ${dkCount(s)} cartas</h4>${rows.length?`<div class="gal">${rows.map(([n,k])=>dkTile(n,k,s)).join('')}</div>`:'<div class="dkempty">Vacío. Buscá cartas a la derecha y tocalas para agregarlas, o importá un mazo.</div>'}</div>`; };
  return `${pageHead('Constructor de mazos','Armá un mazo con las reglas de cada formato, guardalo en este navegador y exportalo.',
    how('<p>Elegí el formato: la banlist del TCG, los puntos de Genesys y los cupos de límite de Duel Links se aplican mientras armás.</p><p>Tocá una carta de la derecha para agregarla (los monstruos del Extra Deck van solos a su sección). Usá «Side» para mandar la carta al Side Deck. En cada carta del mazo podés restar o sumar copias.</p><p>Exportá como YDK, enlace YDKE, imagen PNG o lista de texto. También podés importar cualquiera de esos formatos y abrir las recetas del meta en el constructor.</p>','Cómo se usa'))}
    <div class="dkbar">
      <div class="seg" role="group" aria-label="Formato">${['tcg','gen','dl'].map(f=>`<button data-dkfmt="${f}" aria-pressed="${DK.fmt===f}">${FMT_ES[f]}</button>`).join('')}</div>
      <label class="sr" for="dk-name">Nombre del mazo</label><input type="text" id="dk-name" value="${esc(DK.name)}" placeholder="Nombre del mazo" maxlength="60">
      <button class="abtn pri" data-dk="save">Guardar</button><button class="abtn" data-dk="saved">Mis mazos (${DK.saved.length})</button>
      <button class="abtn" data-dk="import">Importar</button><button class="abtn" data-dk="export">Exportar</button><button class="abtn danger" data-dk="new">Nuevo</button>
    </div>
    <div class="dkgrid">
      <div class="dkdeck">
        <div class="dkstats">${rstat('Main',`${dkCount('main')}<em>${DK.fmt==='dl'?'30–40':'40–60'}</em>`)}${rstat('Extra',`${dkCount('extra')}<em>${DK.fmt==='dl'?'':'/ 15'}</em>`)}${rstat('Side',`${dkCount('side')}<em>${DK.fmt==='dl'?'':'/ 15'}</em>`)}${DK.fmt==='gen'?rstat('Puntos',`${pts.t}<em>/ 100</em>`,`<div class="pbar${pts.t>100?' over':''}"><i style="width:${Math.min(100,pts.t)}%"></i></div>`):''}</div>
        <div class="dkissues">${issues.length?issues.map(x=>`<span>${esc(x)}</span>`).join(''):(dkCount('main')?'<span class="ok">El mazo cumple las reglas de '+FMT_ES[DK.fmt]+'</span>':'')}</div>
        <p class="dkmsg">${DK.modal?'':esc(DK.msg)}</p>
        ${sec('main')}${sec('extra')}${sec('side')}
      </div>
      <div class="dkpick">
        <div class="filters"><label class="sr" for="dq">Buscar carta</label><input id="dq" type="search" placeholder="Buscar carta" value="${esc(DK.q)}" autocomplete="off">
          <label class="sr" for="dkty">Tipo</label><select id="dkty"><option value="all">Todos los tipos</option><option value="m">Monstruos</option><option value="e">Extra Deck</option><option value="s">Hechizos</option><option value="t">Trampas</option></select></div>
        <div class="seg" style="margin:0" role="group" aria-label="Agregar a"><button data-dktarget="auto" aria-pressed="${DK.target==='auto'}">Agregar al mazo</button><button data-dktarget="side" aria-pressed="${DK.target==='side'}">Agregar al Side</button></div>
        <p class="lede" style="margin:0;font-size:.82rem">${names.length.toLocaleString('es-AR')} cartas disponibles en ${FMT_ES[DK.fmt]}. Solo las que tienen arte.</p>
        <div class="gal">${shown.map(pickTile).join('')}</div>
        ${names.length>shown.length?'<button class="abtn" data-dkmore="1">Mostrar más</button>':''}
      </div>
    </div>${dkModal()}</section>`;
}

'''
rep("/* ---------- ENRUTADO ---------- */", BUILDER + "/* ---------- ENRUTADO ---------- */")

# ---------- click/input handlers ----------
rep("  else if(d.rv){ RV=d.rv;",
    r'''  else if(d.todeck!==undefined){ dkFromRecipe(RECIPES[+d.todeck]); mode='deck'; render(); window.scrollTo(0,0); }
  else if(d.dk){ dkAction(d); render(); if(DK.modal==='export'&&DK.tab==='png'&&!DK.png) dkPng().then(u=>{ DK.png=u; render(); }); }
  else if(d.dkfmt){ DK.fmt=d.dkfmt; DK.msg=''; dkDraft(); render(); }
  else if(d.dktarget){ DK.target=d.dktarget; render(); }
  else if(d.dkmore){ DK.limit+=48; render(); }
  else if(d.add){ dkAdd(d.add); render(); }
  else if(d.xt){ DK.tab=d.xt; DK.msg=''; render(); if(DK.tab==='png'&&!DK.png) dkPng().then(u=>{ DK.png=u; render(); }); }
  else if(d.copy){ const map={ydk:dkYdk,ydke:dkYdke,txt:dkText,bk:()=>JSON.stringify(DK.saved)}; (async()=>{ if(d.copy==='png') await copyPng(); else await copyText(map[d.copy](),d.copy==='bk'?'dk-bk-out':'dk-out'); render(); })(); }
  else if(d.load){ const r=DK.saved.find(x=>x.id===d.load); if(r){ DK.fmt=r.fmt; DK.name=r.name; DK.main={...r.main}; DK.extra={...r.extra}; DK.side={...r.side}; DK.modal=null; DK.msg=`Cargué «${r.name}».`; dkDraft(); } render(); }
  else if(d.del){ DK.saved=DK.saved.filter(x=>x.id!==d.del); dkStoreSaved(); render(); }
  else if(d.restore){ try{ const arr=JSON.parse(DK.bk); if(Array.isArray(arr)){ for(const r of arr) if(r&&r.name&&r.main&&!DK.saved.find(x=>x.id===r.id)) DK.saved.push(r); dkStoreSaved(); DK.msg='Restauré los mazos de la copia de seguridad.'; DK.bk=''; } else DK.msg='La copia de seguridad no es válida.'; }catch(e){ DK.msg='La copia de seguridad no es válida.'; } render(); }
  else if(d.rv){ RV=d.rv;''')
# inc/dec controls are <i> elements inside tiles
rep("document.addEventListener('click',e=>{\n  const b=e.target.closest('button'); if(!b) return;",
    "document.addEventListener('click',e=>{\n  const ctl=e.target.closest('[data-inc],[data-dec]');\n  if(ctl){ const n=ctl.dataset.inc||ctl.dataset.dec; if(ctl.dataset.inc) dkAdd(n,ctl.dataset.sec); else dkDec(n,ctl.dataset.sec); render(); return; }\n  if(e.target.classList&&e.target.classList.contains('modal')){ DK.modal=null; DK.msg=''; render(); return; }\n  const b=e.target.closest('button'); if(!b) return;")
rep("  else if(id==='sq'){", "  else if(id==='dk-name'){ DK.name=e.target.value; dkDraft(); }\n  else if(id==='dq'){ DK.q=e.target.value; DK.limit=48; render('dq'); }\n  else if(id==='dkty'){ DK.type=e.target.value; DK.limit=48; render(); }\n  else if(id==='dk-imp'){ DK.imp=e.target.value; }\n  else if(id==='dk-bk'){ DK.bk=e.target.value; }\n  else if(id==='sq'){")
rep("  const ty=$('#ty'); if(ty) ty.value=EX.type;", "  const ty=$('#ty'); if(ty) ty.value=EX.type;\n  const dty=$('#dkty'); if(dty) dty.value=DK.type;")
open('src.html', 'w', encoding='utf-8').write(s)
print('patched', len(s))
