"""Texto en rojo en las recetas a las que no les aplica la banlist (o los puntos) actuales.
  * TCG: cuenta las cartas que hoy superan su límite (prohibida 0, limitada 1, semi-limitada 2) y las nombra.
  * OCG: aviso general (no tenemos su banlist por carta).
  * Genesys: suma los puntos de hoy y dice si la lista se pasa del tope de 100.
Backup: src.before_patch45.html."""
import shutil

shutil.copy('src.html', 'src.before_patch45.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


# la receta sabe de qué formato viene (el OCG usa la misma función que el TCG)
rep("name,price:w.price,post:!!w.post,vk:", "name,price:w.price,post:!!w.post,fk:fmt,vk:")

rep("function vbadge(l){", r'''function vwarn(l){
  if(!l||!l.vk||l.post) return '';
  const d=l.ref?dmy(l.ref):'';
  const all=[...l.main,...l.extra,...l.side];
  if(l.vk==='pts'){
    let t=0; for(const [n,k] of all){ const c=CARDS[canon(n)]; if(c&&c[C.GEN]>0) t+=c[C.GEN]*k; }
    return t>100
      ? `<p class="vwarn">Lista anterior al ajuste de puntos del ${d}: con los puntos de hoy suma ${t} de 100 y se pasa por ${t-100}. Hoy no sería legal tal cual.</p>`
      : `<p class="vwarn">Lista anterior al ajuste de puntos del ${d}: los costos de sus cartas eran otros. Con los puntos de hoy suma ${t} de 100.</p>`;
  }
  if(l.fk==='ocg') return `<p class="vwarn">Lista anterior a la banlist del OCG del ${d}: puede incluir cartas que ya no se pueden usar como están. Revisá la banlist antes de copiarla.</p>`;
  const have=new Map(); for(const [n,k] of all) have.set(canon(n),(have.get(canon(n))||0)+k);
  const over=[]; for(const [n,k] of have){ const c=CARDS[n]; if(!c) continue; const b=c[C.BAN]; const max=b===0?0:b===1?1:b===2?2:3; if(k>max) over.push(`${n} (usa ${k}, ${max?'máximo '+max:'prohibida'})`); }
  return over.length
    ? `<p class="vwarn">Lista anterior a la banlist del ${d}: hoy no es legal tal cual. ${over.slice(0,4).join('; ')}${over.length>4?` y ${over.length-4} más`:''}.</p>`
    : `<p class="vwarn">Lista anterior a la banlist del ${d}: no pasa ningún límite actual, pero se armó antes de los cambios y puede no reflejar el meta de hoy.</p>`;
}
function vbadge(l){''')

# se muestra justo debajo de los datos de la receta
rep("<div class=\"rstats\">${stats}</div>${note}<div class=\"decklist\">", "<div class=\"rstats\">${stats}</div>${vwarn(l)}${note}<div class=\"decklist\">")

css = '''.vwarn{margin:0;padding:var(--s2) var(--s3);border-radius:var(--r2);border:1px solid color-mix(in srgb,var(--red) 45%,transparent);background:color-mix(in srgb,var(--red) 10%,transparent);color:var(--red);font-size:.84rem;line-height:1.5;font-weight:600}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 45 ok')
