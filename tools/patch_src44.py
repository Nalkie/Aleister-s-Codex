"""Mismo criterio que el patch 43 para Genesys y OCG.
  * Genesys: ajuste de puntos de aniversario del 5 oct 2026 -> insignias «Puntos actuales» / «Puntos anteriores» y aviso.
  * OCG: lista de prohibidas y limitadas vigente desde el 1 oct 2026 -> insignias «Banlist actual» / «Banlist anterior» y aviso.
  * Edison, Goat y HAT son formatos históricos con lista fija: no cambian, no llevan aviso ni insignias.
La fecha de referencia de cada formato viaja en los datos (ref) y la calcula tools/ygm.py.  Backup: src.before_patch44.html."""
import shutil

shutil.copy('src.html', 'src.before_patch44.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


# ---- la receta sabe de qué clase de cambio habla y desde cuándo rige ----
rep("name,price:w.price,post:!!w.post,\n      who:`${w.author} · ${w.event}${w.place?', '+w.place:''} (${w.date}). ${w.post&&d.npost?`Es la lista más parecida al promedio de las ${d.npost} jugadas con la banlist vigente`:`Es la lista real reciente más parecida al promedio de ${d.sample} decks del arquetipo`}.`,",
    "name,price:w.price,post:!!w.post,vk:fmt==='gen'?'pts':'ban',ref:D.ref||'',\n      who:`${w.author} · ${w.event}${w.place?', '+w.place:''} (${w.date}). ${w.post&&d.npost?`Es la lista más parecida al promedio de las ${d.npost} jugadas con ${fmt==='gen'?'los puntos vigentes':'la banlist vigente'}`:`Es la lista real reciente más parecida al promedio de ${d.sample} decks del arquetipo`}.`,")
rep("const o={id:fmt+'-'+slug(name),n:name,npost:d.npost||0,tier:", "const o={id:fmt+'-'+slug(name),n:name,npost:d.npost||0,vk:fmt==='gen'?'pts':'ban',tier:")

# ---- insignia: banlist (TCG/OCG) o puntos (Genesys) ----
i = s.index('function vbadge(l){')
j = s.index("let RV='gal';")
s = s[:i] + '''function vbadge(l){
  if(!l||!l.vk) return '';
  const d=l.ref?dmy(l.ref):'';
  if(l.vk==='pts') return l.post
    ? `<span class="vb ok" title="Lista jugada desde el ${d}, con los puntos vigentes">Puntos actuales</span>`
    : `<span class="vb old" title="Lista jugada antes del ${d}: los puntos de sus cartas eran otros, así que puede sumar más de 100 con los puntos de hoy">Puntos anteriores</span>`;
  return l.post
    ? `<span class="vb ok" title="Lista jugada desde el ${d}, con la banlist vigente">Banlist actual</span>`
    : `<span class="vb old" title="Lista jugada antes del ${d}: puede incluir cartas que ya no se pueden usar como están">Banlist anterior</span>`;
}
''' + s[j:]
rep("/banlist actual/.test(x)?'u':''", "/(banlist|puntos) actual/.test(x)?'u':''")

# ---- chip de la fila y aviso: Genesys ----
i = s.index('function viewGEN(){')
j = s.index("let dlFormat='speed';")
seg = s[i:j]
a = "${d.top4} top 4`,"
assert seg.count(a) == 1
seg = seg.replace(a, "${d.top4} top 4${d.npost?` · ${d.npost} con puntos actuales`:''}`,")
g = "  ${grouped(decks,"
assert seg.count(g) == 1
seg = seg.replace(g, "  ${callout('gen_banner_title','gen_banner_desc')}\n" + g)
s = s[:i] + seg + s[j:]

# ---- chip de la fila y aviso: OCG (la misma función dibuja Edison, Goat y HAT, que no llevan ninguno de los dos) ----
i = s.index('function viewMetaFmt(k){')
j = s.index('function viewTCGAdv(){') if s.index('function viewTCGAdv(){') > i else None
# viewTCGAdv está definido después de la función I18N: buscamos el cierre de viewMetaFmt por la siguiente "function"
j = s.index('\nfunction ', i + 10)
seg = s[i:j]
a = "${fmt(d.pts)} del peso de resultados`,"
assert seg.count(a) == 1
seg = seg.replace(a, "${fmt(d.pts)} del peso de resultados${d.npost?` · ${d.npost} con banlist actual`:''}`,")
g = "  return head+`\n  ${grouped(decks,"
assert seg.count(g) == 1
seg = seg.replace(g, "  return head+`\n  ${k==='ocg'?callout('ocg_banner_title','ocg_banner_desc'):''}\n  ${grouped(decks,")
s = s[:i] + seg + s[j:]

# ---- textos traducibles ----
rep("  tcg_banner_desc:'Los datos y tiers reflejan los resultados de torneos del metajuego saliente. La nueva lista de prohibidas y limitadas aún no entra en vigor, por lo que las posiciones y ratios cambiarán en las próximas semanas conforme impacte el nuevo formato.'\n}};",
    """  tcg_banner_desc:'Los datos y tiers reflejan los resultados de torneos del metajuego saliente. La nueva lista de prohibidas y limitadas aún no entra en vigor, por lo que las posiciones y ratios cambiarán en las próximas semanas conforme impacte el nuevo formato.',
  gen_banner_title:'Formato en transición',
  gen_banner_desc:'Konami ajustó los puntos de Genesys el 5 de octubre (ajuste de aniversario, cientos de cartas). Los tiers incluyen torneos jugados con los puntos anteriores: algunas recetas pueden sumar más de 100 con los puntos de hoy y las posiciones pueden cambiar en las próximas semanas.',
  ocg_banner_title:'Formato en transición',
  ocg_banner_desc:'La lista de prohibidas y limitadas del OCG cambió el 1 de octubre. Parte de los decks de la muestra se jugó con la lista anterior: las recetas marcadas «Banlist anterior» pueden incluir cartas que ya no se pueden usar como están.'
}};""")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 44 ok')
