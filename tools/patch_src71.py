"""Ruleta de decks: versiones de un mismo personaje.  Un personaje sigue siendo UNA porción de la rueda; si tiene más de un mazo (otra etapa, otro arco, otro deck), una vez elegido
aparece bajo su nombre un selector «Versión» con un botón por mazo y se cambia sin volver a girar (la dirección compartida lleva el mazo elegido).  Backup: src.before_patch71.html."""
import shutil

shutil.copy('src.html', 'src.before_patch71.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep("function rouHero(d){",
    "function rouVersion(id){ if(ROU.spinning||!rouDeck(id)) return; ROU.deck=rouDeck(id).id; ROU.fresh=false; ROU.note=''; ROU.refocus=`[data-rver=\"${rouDeck(id).id}\"]`; render(); }\n"
    "function rouVers(d){          // los otros mazos del mismo personaje (una sola porción en la rueda): un botón por versión\n"
    "  const sib=ROU.data.decks.filter(x=>x.character===d.character&&x.series===d.series); if(sib.length<2) return '';\n"
    "  const nm=x=>sib.filter(y=>y.name===x.name).length>1?`${x.name} · ${rouArc(x)}`:x.name;\n"
    "  return `<div class=\"rou-vers\" role=\"group\" aria-label=\"Versión del mazo\"><span class=\"rou-vl\">Versión</span>${sib.map(x=>`<button data-rver=\"${esc(x.id)}\" aria-pressed=\"${x.id===d.id}\" title=\"${esc(rouArc(x)||'')}\">${esc(nm(x))}</button>`).join('')}</div>`;\n"
    "}\n"
    "function rouHero(d){")
rep("""<p class="rou-deckname">${esc(d.name)}${arc?` · ${esc(arc)}`:''}</p>""",
    """<p class="rou-deckname">${esc(d.name)}${arc?` · ${esc(arc)}`:''}</p>${rouVers(d)}""")
rep("  if(d.rser){ rouSeries(d.rser); return; }", "  if(d.rser){ rouSeries(d.rser); return; }\n  if(d.rver){ rouVersion(d.rver); return; }")
rep(".rou-acts{", ".rou-vers{display:flex;flex-wrap:wrap;align-items:center;gap:var(--s2);margin:var(--s2) 0 var(--s1)} .rou-vl{font:500 .68rem var(--f-data);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}\n"
    ".rou-vers button{font:600 .8rem var(--f-body);color:var(--fg);background:var(--surface);border:1px solid var(--line);border-radius:999px;padding:4px 12px;cursor:pointer} .rou-vers button:hover{border-color:var(--accent)} .rou-vers button[aria-pressed=\"true\"]{background:var(--accent);border-color:var(--accent);color:var(--bg,#0b1020)}\n.rou-acts{")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 71 ok')
