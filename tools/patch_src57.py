"""Precio de cada versión de la carta (impresión), en dólares y en pesos al dólar blue, con la misma lógica que el precio de la carta.
  * Si la impresión tiene precio propio, se usa ese.
  * Si no, se estima: la mediana de las otras impresiones de la misma rareza de esa carta; si no hay, el precio de la carta (con «≈» y el motivo en el título).
Se muestra en «Versiones de la carta» y en la tabla de expansiones y precio.  Backup: src.before_patch57.html."""
import shutil

shutil.copy('src.html', 'src.before_patch57.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep("function priceBlock(n,d){", r"""function verPrice(n,d,p){      // precio de una versión: el propio o una estimación (misma rareza de la misma carta, o el precio de la carta)
  const own=nz(p[3]); if(own) return {u:own,est:0};
  const same=(d.pn||[]).filter(x=>x!==p&&x[2]===p[2]&&nz(x[3])).map(x=>nz(x[3])).sort((a,b)=>a-b);
  if(same.length){ const m=same.length>>1; return {u:same.length%2?same[m]:(same[m-1]+same[m])/2,est:1,why:'rar'}; }
  const c=CARDS[n], ref=c?nz(c[C.PR]):0; return ref?{u:ref,est:1,why:'card'}:null;
}
function pxVer(v){
  if(!v) return 's/d';
  const tip=!v.est?'Precio de esta versión en TCGplayer':v.why==='rar'?'Estimado: esta versión no tiene precio, se usa la mediana de las otras impresiones de la misma rareza de esta carta':'Estimado: esta versión no tiene precio, se usa el precio de la carta';
  return `<span class="px" title="${esc(tip)}"><b>${v.est?'≈ ':''}US$ ${fUsd(v.u)}</b>${FXR.ars?`<i>AR$ ${fArs(v.u)}</i>`:''}</span>`;
}
function priceBlock(n,d){""")
rep("""<b class="pp">${p[3]>0?'$'+p[3].toFixed(2):'s/d'}</b></button>`; }).join('')}</div>
    ${rows.length>shown.length""", """<b class="pp">${pxVer(verPrice(n,d,p))}</b></button>`; }).join('')}</div>
    ${rows.length>shown.length""")
rep("<td>${p[3]>0?'US$ '+p[3]:''}</td></tr>`).join('')}</tbody></table></div>\n   ${d.pn.length>12&&!inSet", "<td>${pxVer(verPrice(n,d,p))}</td></tr>`).join('')}</tbody></table></div>\n   ${d.pn.length>12&&!inSet")
css = '''.pv .px{justify-content:center;gap:0 6px;font-size:.66rem}
.pv .pp .px b{font-size:.74rem}
.ptab .px{margin:0}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 57 ok')
