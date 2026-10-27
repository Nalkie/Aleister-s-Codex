"""Precios en el buscador de cartas: en dólares y en pesos argentinos al dólar blue.
  * Cada carta de la lista muestra su precio (US$ y AR$); «≈» si es una estimación, y el título explica de dónde sale.
  * El detalle de la carta suma una sección «Precios» con TCGplayer, Cardmarket, eBay, CoolStuffInc y Amazon (YGOPRODeck las junta), cada una en dólares y en pesos.
  * El dólar blue viene de los datos (tools/fetch_prices.py, dolarapi.com) y la página lo vuelve a pedir al abrirse; si no puede, queda el del build.
Backup: src.before_patch56.html."""
import shutil

shutil.copy('src.html', 'src.before_patch56.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


# ---- 1. ayudantes de precio y dólar blue ----
rep("const dmy=d=>{", r"""/* ---------- precios en dólares y pesos (dólar blue) ---------- */
const FXR={ars:0,date:'',src:'',eur:1.1};
function setFx(f){ if(f&&f.ars>0){ FXR.ars=f.ars; FXR.date=f.date||FXR.date; FXR.src=f.src||FXR.src; FXR.eur=f.eur||FXR.eur; } }
function refreshFx(){      // el dólar blue del día: si no se puede pedir, queda el que trajo el build
  try{ fetch('https://dolarapi.com/v1/dolares/blue').then(r=>r.ok?r.json():Promise.reject()).then(j=>{ if(j&&j.venta>0){ FXR.ars=+j.venta; FXR.date=String(j.fechaActualizacion||'').slice(0,10)||FXR.date; FXR.src='dolarapi.com'; render(); } }).catch(()=>{}); }catch(e){}
}
const nz=x=>{ x=Number(x); return x>0?x:0; };
const fUsd=u=>u>=100?Math.round(u).toLocaleString(LOC):u.toLocaleString(LOC,{minimumFractionDigits:2,maximumFractionDigits:2});
const fArs=u=>Math.round(u*FXR.ars).toLocaleString(LOC);
function pxTag(u,fl){      // precio de una carta: US$ y AR$ (≈ si es estimado)
  const est=fl&16, other=fl&32;
  const tip=est?'Estimado: no hay precio publicado, se calcula con cartas parecidas':other?'Precio de otra tienda (Cardmarket, eBay, CoolStuffInc o Amazon): TCGplayer no la tiene':'Precio en TCGplayer';
  return `<span class="px" title="${esc(tip)}"><b>${est?'≈ ':''}US$ ${fUsd(u)}</b>${FXR.ars?`<i>AR$ ${fArs(u)}</i>`:''}</span>`;
}
function priceBlock(n,d){
  const p=(d&&d.p||[]).map(nz);
  if(!p.some(Boolean)) return '';
  const eur=FXR.eur||1.1;
  const rows=[['TCGplayer',p[0],'USD'],['Cardmarket',p[1],'EUR'],['eBay',p[2],'USD'],['CoolStuffInc',p[3],'USD'],['Amazon',p[4],'USD']].filter(r=>r[1]);
  const body=rows.map(([st,v,cur])=>{ const u=cur==='EUR'?v*eur:v; return `<tr><td>${st}</td><td>${cur==='EUR'?'€ '+v.toLocaleString(LOC,{minimumFractionDigits:2}):'US$ '+fUsd(v)}</td><td>${cur==='EUR'?'≈ ':''}US$ ${fUsd(u)}</td><td>${FXR.ars?'AR$ '+fArs(u):''}</td></tr>`; }).join('');
  return `<p class="eff">Precios de venta actuales en cada tienda, que YGOPRODeck junta. No es la última venta: eso no lo publica ninguna fuente abierta.</p>
   <div class="tbl"><table class="ptab"><thead><tr><th>Tienda</th><th>Precio</th><th>En dólares</th><th>En pesos (dólar blue)</th></tr></thead><tbody>${body}</tbody></table></div>
   ${FXR.ars?`<p class="rnote">Dólar blue (venta): AR$ ${FXR.ars.toLocaleString(LOC)}${FXR.date?' al '+dmy(FXR.date):''}. Euro: US$ ${eur}.</p>`:''}`;
}
const dmy=d=>{""")

# ---- 2. la lista del buscador ----
rep("<b>${usedCount(c)?usedCount(c)+' estrat.':''}</b>${miniLims(c)}</span></button>`;}).join('')}</div>",
    "<b>${usedCount(c)?usedCount(c)+' estrat.':''}</b>${miniLims(c)}${CARDS[c][C.PR]>0?pxTag(CARDS[c][C.PR],CARDS[c][C.FL]):''}</span></button>`;}).join('')}</div>")

# ---- 3. el detalle ----
rep("+pjBlock(d)+isec('Versiones de la carta',versionsBlock(n,d))", "+pjBlock(d)+isec('Precios',priceBlock(n,d))+isec('Versiones de la carta',versionsBlock(n,d))")
rep("""   ${pr[0]!=null?'≈ US$ '+pr[0]+' (TCGplayer)':''}${pr[1]!=null?' · ≈ € '+pr[1]+' (Cardmarket)':''}. Precio de referencia.</p>""", "</p>")
rep("≈ US$ ${p.usd} · ¥${p.jpy.toLocaleString(LOC)} en Yuyu-tei", "≈ US$ ${p.usd}${FXR.ars?` (AR$ ${fArs(p.usd)})`:''} · ¥${p.jpy.toLocaleString(LOC)} en Yuyu-tei")
rep("≈ US$ ${p.usd} (estimado). Esta carta", "≈ US$ ${p.usd}${FXR.ars?` (AR$ ${fArs(p.usd)})`:''} (estimado). Esta carta")

# ---- 4. se cargan al abrir ----
rep("  DBINFO=j; TCGSETS=j.tcgsets; Object.assign(ALTS,j.alts||{});", "  DBINFO=j; TCGSETS=j.tcgsets; Object.assign(ALTS,j.alts||{}); setFx(j.fx); refreshFx();")

# ---- 5. estilos ----
css = '''/* precios en dólares y pesos */
.px{display:flex;flex-wrap:wrap;gap:0 8px;align-items:baseline;margin-top:2px;font:600 .72rem var(--f-data)}
.px b{color:var(--fg);font-weight:700}
.px i{font-style:normal;color:var(--muted);font-weight:500}
.cc .px{font-size:.68rem}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')

# ---- 6. fuente en el pie ----
rep("    <li>Puntos Genesys:", """    <li>Precios de las cartas: TCGplayer, Cardmarket, eBay, CoolStuffInc y Amazon, que junta <a href="https://ygoprodeck.com/">YGOPRODeck</a>. Si una carta no tiene precio en TCGplayer se muestra el de otra tienda, y si no tiene en ninguna se estima con la mediana de cartas parecidas (con «≈»). TrollAndToad no publica una API de precios y no está incluida; ninguna fuente abierta publica la última venta de cada carta. Pesos argentinos: dólar blue (venta) de <a href="https://dolarapi.com/">DolarApi</a>, que la página vuelve a pedir al abrirse.</li>
    <li>Puntos Genesys:""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 56 ok')
