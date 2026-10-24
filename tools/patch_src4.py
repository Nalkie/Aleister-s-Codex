"""Design pass: new style system (tools/style.css), a single page-header pattern, collapsible method notes and footer.
Run once from build/ (backs src.html up first)."""
import re, shutil

shutil.copy('src.html', 'src.before_patch4.html')
s = open('src.html', encoding='utf-8').read()
css = open('tools/style.css', encoding='utf-8').read()


def sub1(pattern, repl, flags=re.S):
    global s
    s, n = re.subn(pattern, (lambda m: repl(m)) if callable(repl) else (lambda m: repl), s, count=1, flags=flags)
    assert n == 1, pattern[:70]


# ---- style block ----
sub1(r'<style>.*?</style>', '<style>\n' + css + '</style>')

# ---- helpers ----
anchor = "function tbl(head,rows){"
assert anchor in s
s = s.replace(anchor, r'''const how=(html,title='Cómo se calcula')=>`<details class="how"><summary>${title}</summary><div class="how-in">${html}</div></details>`;
const pageHead=(title,lede,howHtml='',note='')=>`<section class="first"><div class="phead"><h2>${title}</h2><p class="lede">${lede}</p>${howHtml}${note?`<div class="note">${note}</div>`:''}</div>`;
const secHead=(title,lede='',howHtml='')=>`<section><div class="phead"><h2>${title}</h2>${lede?`<p class="lede">${lede}</p>`:''}${howHtml}</div>`;
''' + anchor, 1)

# ---- secondary sections: <section><h2>T</h2><p class="lede">L</p>  ->  secHead ----
s, n = re.subn(r'<section><h2>([^<]+)</h2><p class="lede">(.*?)</p>', lambda m: '${secHead(`' + m.group(1) + '`,`' + m.group(2) + '`)}', s, flags=re.S)
print('secondary headers rewritten:', n)

# ---- TCG ----
sub1(r'<section style="margin-top:32px"><h2>Mejores mazos</h2>.*?\n  \$\{grouped\(decks,',
     r'''${pageHead('Mejores mazos',`Los arquetipos más fuertes del TCG según ${D.total} decks de torneos recientes. Abrí un mazo para ver su receta real y sus cartas clave.`,
    how(`<p>Muestra: ${D.total} decks de torneos TCG entre el ${YGM.window[0]} y el ${YGM.window[1]} (WCQ Regionals, YCS, WCS y torneos comunitarios; sin OCG ni Genesys).</p><p>${tierLede()}</p><p>La barra muestra la parte de los decks de la muestra. Los arquetipos híbridos (por ejemplo Dark Magician Chaos Ritual) se cuentan aparte, como los publica la fuente.</p>`),
    `El último torneo cargado en YuGiOh Meta es del ${YGM.asof}: la banlist vigente desde el 19 oct todavía no aparece en estos resultados.`)}
  ${grouped(decks,''')
# ---- Genesys ----
sub1(r'<section style="margin-top:32px"><h2>Mejores mazos en Genesys</h2>.*?\n  \$\{grouped\(decks,',
     r'''${pageHead('Mejores mazos en Genesys',`Genesys es el formato por puntos: cada carta tiene un costo y la lista suma hasta 100. Muestra de ${D.total} decks de torneos Genesys. Cada receta marca los puntos de sus cartas.`,
    how(`<p>Decks de torneos Genesys entre el ${YGM.window[0]} y el ${YGM.window[1]}.</p><p>${tierLede()}</p><p>Los puntos son los actuales de la base de YuGiOh Meta. Una receta puede sumar más de 100 si el torneo usó los puntos anteriores al ajuste del 5 oct. Los monstruos Link y Pendulum no se pueden usar en este formato.</p>`))}
  ${grouped(decks,''')
# ---- Duel Links ----
sub1(r'<section style="margin-top:20px"><h2>Mejores mazos · \$\{DL_FMT\[dlFormat\]\}</h2>.*?\n  \$\{body\}</section>',
     r'''${pageHead(`Mejores mazos · ${DL_FMT[dlFormat]}`,`Los arquetipos más usados en Duel Links según los decks publicados en Duel Links Meta. Abrí un mazo para ver su receta con copias, rareza y cómo conseguir cada carta.`,
    how(`<p>${dlFormat==='speed'?'Los tiers son los que publica Duel Links Meta para cada arquetipo.':'Duel Links Meta no asigna tiers en Rush.'}</p><p>Muestra: ${D.total} decks entre el ${DLD.window[0]} y el ${DLD.window[1]}. El % es la parte de la muestra.</p><p>La receta es el deck real reciente más parecido al promedio del arquetipo; el % de cada carta es en cuántos decks del arquetipo aparece. Solo se listan arquetipos con al menos ${dlFormat==='speed'?8:3} decks o con una victoria. ${dlFormat==='rush'?'Las cartas de Rush Duel no están en la base de imágenes.':''}</p>`))}
  ${body}</section>''')
# ---- buscador / cajas / banlist ----
sub1(r'<section style="margin-top:32px"><h2>Buscador de cartas</h2>\s*<p class="lede">(.*?)</p>',
     lambda m: "${pageHead('Buscador de cartas',`" + m.group(1) + "`)}")
sub1(r'<section style="margin-top:32px"><h2>Cajas y sets</h2>\s*<p class="lede">(.*?)</p>',
     lambda m: "${pageHead('Cajas y sets',`" + m.group(1) + "`)}")
sub1(r'<section style="margin-top:32px"><h2>Banlist por formato</h2>\s*<p class="lede">(.*?)</p>',
     lambda m: "${pageHead('Banlist por formato',`" + m.group(1) + "`)}")
sub1(r'(?<!`)<div class="note">\$\{note\}</div>', r"${how(`<p>${note}</p>`,'Fuente y reglas')}")

# ---- header pills ----
sub1(r"\$\('#asof'\)\.textContent=`.*?`;",
     "$('#asof').innerHTML=[`TCG y Genesys: hasta ${YGM.asof}`,`Duel Links: hasta ${DLD.asof}`,`Página generada el ${BUILT}`].map(x=>`<span class=\"pill\">${x}</span>`).join('');")

# ---- footer ----
sub1(r'<footer>\s*<strong>Fuentes y límites</strong>\s*<ul>', '<footer>\n  <details class="foot"><summary>Fuentes y límites</summary>\n  <ul>')
sub1(r'</ul>\s*</footer>', '</ul>\n  </details>\n</footer>')
open('src.html', 'w', encoding='utf-8').write(s)
print('patched', len(s))
