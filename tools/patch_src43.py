"""Aviso «Formato en transición» sobre la tier list del TCG e insignias «Banlist actual» / «Banlist anterior» en cada receta.
El aviso usa I18N (claves tcg_banner_title y tcg_banner_desc) para poder traducirlo.
Las insignias salen de dl/ygmdata.json (who.post y npost, que escribe tools/ygm.py). Solo el TCG: Genesys se juega por puntos, no por la banlist de Konami.
Backup: src.before_patch43.html. Después: python tools/page_only.py"""
import shutil

shutil.copy('src.html', 'src.before_patch43.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


# ---- 1. la receta y la fila del mazo llevan la marca ----
rep("""    const list={kind:fmt==='gen'?'gen':FMT_RETRO[fmt]?fmt:'tcg',name,price:w.price,
      who:`${w.author} · ${w.event}${w.place?', '+w.place:''} (${w.date}). Es la lista real reciente más parecida al promedio de ${d.sample} decks del arquetipo.`,""",
    """    const list={kind:fmt==='gen'?'gen':FMT_RETRO[fmt]?fmt:'tcg',name,price:w.price,post:!!w.post,
      who:`${w.author} · ${w.event}${w.place?', '+w.place:''} (${w.date}). ${w.post&&d.npost?`Es la lista más parecida al promedio de las ${d.npost} jugadas con la banlist vigente`:`Es la lista real reciente más parecida al promedio de ${d.sample} decks del arquetipo`}.`,""")
rep("const o={id:fmt+'-'+slug(name),n:name,tier:d.out?'R':(d.tier||'R'),out:d.out,c:d.n,lists:d.sample,",
    "const o={id:fmt+'-'+slug(name),n:name,npost:d.npost||0,tier:d.out?'R':(d.tier||'R'),out:d.out,c:d.n,lists:d.sample,")

# ---- 2. insignia en la cabecera de la receta ----
rep("""<h3>Receta ${kind==='dl'?'más usual':'de referencia'}</h3><p class="who">""",
    """<h3>Receta ${kind==='dl'?'más usual':'de referencia'}${vbadge(l)}</h3><p class="who">""")
rep("let RV='gal';", """function vbadge(l){
  if(!l||l.kind!=='tcg') return '';
  return l.post
    ? '<span class="vb ok" title="Lista jugada desde el 19 de octubre, con la banlist vigente">Banlist actual</span>'
    : '<span class="vb old" title="Lista jugada antes del 19 de octubre: puede incluir cartas que ya no se pueden usar como están">Banlist anterior</span>';
}
let RV='gal';""")

# ---- 3. chip en la fila del mazo (solo la tier list del TCG) ----
rep("""const chips=metaTxt.split(' · ').map(x=>`<i class="${/victoria/.test(x)?'w':/top 4/.test(x)?'t':''}">${x}</i>`).join('');""",
    """const chips=metaTxt.split(' · ').map(x=>`<i class="${/victoria/.test(x)?'w':/top 4/.test(x)?'t':/banlist actual/.test(x)?'u':''}">${x}</i>`).join('');""")
i = s.index('function viewTCGAdv(){')
j = s.index('function viewGEN(){')
seg = s[i:j]
a = "${fmt(d.pts)} del peso de resultados`,"
assert seg.count(a) == 1
seg = seg.replace(a, "${fmt(d.pts)} del peso de resultados${d.npost?` · ${d.npost} con banlist actual`:''}`,")

# ---- 4. el aviso, justo antes de los tiers ----
g = "  ${grouped(decks,"
assert seg.count(g) == 1
seg = seg.replace(g, "  ${callout('tcg_banner_title','tcg_banner_desc')}\n" + g)
s = s[:i] + seg + s[j:]

# ---- 5. textos traducibles y componente ----
rep("function viewTCGAdv(){", """/* textos traducibles: para sumar un idioma se agrega otro objeto en I18N y se cambia LANG */
const I18N={es:{
  tcg_banner_title:'Formato en transición',
  tcg_banner_desc:'Los datos y tiers reflejan los resultados de torneos del metajuego saliente. La nueva lista de prohibidas y limitadas aún no entra en vigor, por lo que las posiciones y ratios cambiarán en las próximas semanas conforme impacte el nuevo formato.'
}};
let LANG='es';
const tr=k=>(I18N[LANG]&&I18N[LANG][k])||I18N.es[k]||k;
const CALLOUT_ICON='<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7 V12 L15.5 14"/></svg>';
function callout(titleKey,descKey){
  return `<aside class="callout" role="note"><span class="ci">${CALLOUT_ICON}</span><div><b data-i18n="${titleKey}">${esc(tr(titleKey))}</b><p data-i18n="${descKey}">${esc(tr(descKey))}</p></div></aside>`;
}
function viewTCGAdv(){""")

# ---- 6. estilos ----
css = '''/* aviso e insignias de banlist */
.callout{--wn:#f5a524;display:flex;gap:var(--s3);align-items:flex-start;margin:var(--s4) 0 0;padding:var(--s3) var(--s4);border-radius:var(--r2);border:1px solid color-mix(in srgb,var(--wn) 32%,transparent);background:color-mix(in srgb,var(--wn) 10%,transparent)}
.callout .ci{flex:none;width:20px;height:20px;margin-top:1px;color:color-mix(in srgb,var(--wn) 80%,var(--fg))}
.callout .ci svg{width:100%;height:100%;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.callout b{display:block;font:700 .86rem var(--f-display);color:color-mix(in srgb,var(--wn) 70%,var(--fg));line-height:1.3}
.callout p{margin:2px 0 0;font-size:.82rem;line-height:1.5;color:var(--muted);max-width:90ch}
.vb{display:inline-block;vertical-align:middle;margin-left:8px;font:600 .64rem var(--f-data);letter-spacing:.06em;text-transform:uppercase;padding:3px 9px;border-radius:99px;border:1px solid}
.vb.ok{color:var(--ac-dl);border-color:color-mix(in srgb,var(--ac-dl) 55%,transparent);background:color-mix(in srgb,var(--ac-dl) 14%,transparent)}
.vb.old{color:color-mix(in srgb,#f5a524 75%,var(--fg));border-color:color-mix(in srgb,#f5a524 45%,transparent);background:color-mix(in srgb,#f5a524 12%,transparent)}
.meta i.u{color:var(--ac-dl);border-color:color-mix(in srgb,var(--ac-dl) 50%,transparent);background:color-mix(in srgb,var(--ac-dl) 10%,transparent)}
@media(max-width:760px){.callout{padding:var(--s2) var(--s3);gap:var(--s2)}.callout .ci{width:17px;height:17px}.callout b{font-size:.8rem}.callout p{font-size:.76rem;line-height:1.45}}
'''
assert s.count('</style>') == 1
s = s.replace('</style>', css + '</style>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 43 ok')
