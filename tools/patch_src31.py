"""1) Sin destellos: se quitan el barrido de luz periódico y el parpadeo de las cartas con efecto foil (queda un solo brillo al pasar el mouse) y el
brillo que recorría las barras de uso. 2) Los personajes y las otras vías de obtención salen de "Cajas y sets" a su propia pestaña "Obtención".
Backup: src.before_patch31.html."""
import shutil
shutil.copy('src.html', 'src.before_patch31.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# ---------- 1) destellos ----------
rep(".fmtbar{margin:var(--s4) 0 0}", """.fmtbar{margin:var(--s4) 0 0}
/* sin destellos: el foil queda fijo y solo brilla una vez al pasar el mouse; las barras no se iluminan solas */
.fill{animation:none!important}
.cf[data-fo]::before{animation:none!important}
.bigcard .cf[data-fo]:not([data-fo="n"])::after,.pv .cf[data-fo]:not([data-fo="n"])::after{animation:none!important;background-position:150% 0}
.bigcard:hover .cf[data-fo]:not([data-fo="n"])::after,.pv:hover .cf[data-fo]:not([data-fo="n"])::after{animation:fshine 1.2s ease-out 1!important}""")

# ---------- 2) pestaña Obtención ----------
rep("body.ex,body.sets,body.ban,body.ev{--accent:var(--ac-tool)}", "body.ex,body.sets,body.obt,body.ban,body.ev{--accent:var(--ac-tool)}")
a = s.index('<button class="tool" role="tab" id="tab-sets"')
b = s.index('</button>', a) + len('</button>')
s = s[:b] + '\n    <button class="tool" role="tab" id="tab-obt" data-mode="obt"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="6" cy="7" r="2.5"/><circle cx="18" cy="7" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8.2 8.3 L10.8 15.7 M15.8 8.3 L13.2 15.7 M8.5 7 H15.5"/></svg>Obtención</button>' + s[b:]
rep("const n=mode==='sets'?SETS.card:EX.card,", "const n=(mode==='sets'||mode==='obt')?SETS.card:EX.card,")
rep("if(mode==='sets'||mode==='ev') render(SETS.focusQ);", "if(mode==='sets'||mode==='obt'||mode==='ev') render(SETS.focusQ);")
rep("typeof mode!=='undefined'&&mode==='sets') render();", "typeof mode!=='undefined'&&(mode==='sets'||mode==='obt')) render();")
rep("if(mode!=='sets'||SETS.card!==n||!$('#sx-tail')) return;", "if((mode!=='sets'&&mode!=='obt')||SETS.card!==n||!$('#sx-tail')) return;")
rep("if(mode!=='sets'||SETS.card!==n||!$('#sx-live')) return;", "if((mode!=='sets'&&mode!=='obt')||SETS.card!==n||!$('#sx-live')) return;")
rep("if(mode==='ev'||mode==='sets') render(); }).catch(()=>{});", "if(mode==='ev'||mode==='sets'||mode==='obt') render(); }).catch(()=>{});")
rep("['ex','sets','ban','deck','guide','ev'].includes(mode)||(mode==='tcg'&&TCGF!=='adv')", "['ex','sets','obt','ban','deck','guide','ev'].includes(mode)||(mode==='tcg'&&TCGF!=='adv')")
rep("if(mode==='sets'&&SETS.card) fillSInsp(SETS.card);", "if((mode==='sets'||mode==='obt')&&SETS.card) fillSInsp(SETS.card);")
rep("sets:['Cajas y sets',viewSets],", "sets:['Cajas y sets',viewSets],obt:['Obtención',viewSets],")
rep("    if(f==='dl'){ SETS.kind='set'; loadSets('dl').then(()=>{ const s=(SETS.data.dl||[]).find(x=>x.n===i); if(s){ SETS.kind=s.kind; render(); } }); }",
    "    if(f==='dl'){ SETS.kind='set'; loadSets('dl').then(()=>{ const s=(SETS.data.dl||[]).find(x=>x.n===i); if(s){ SETS.kind=s.kind; if(s.kind!=='set'&&mode==='sets'){ mode='obt'; SETS._scope='obt'; } render(); } }); }")
rep("function viewSets(){\n  const fmt=SETS.fmt, data=SETS.data[fmt];", r'''function viewSets(){
  const obt=mode==='obt', scope=obt?'obt':'sets';
  if(SETS._scope!==scope){   // cada pestaña muestra sus propias listas: Cajas y sets = expansiones y cajas · Obtención = personajes y otras vías
    SETS._scope=scope; SETS.sel=null; SETS.card=null; SETS.q=''; SETS.limit=80; SETS.cl=SCL; SETS.cq=''; SETS.rf='all';
    if(obt){ SETS.fmt='dl'; if(SETS.kind==='set') SETS.kind='char'; } else if(SETS.kind!=='set') SETS.kind='set';
  }
  const fmt=SETS.fmt, data=SETS.data[fmt];''')
a = s.index("  const head=`${pageHead('Cajas y sets',")
b = s.index("  if(!data){ loadSets(fmt);", a)
new_head = r'''  const head=obt
    ? `${pageHead('Obtención en Duel Links','Qué cartas da cada personaje (al subir de nivel, en la Puerta y en su mazo de personaje) y cada vía especial: tickets, eventos, misiones y Card Trader. Tocá una carta para verla a la derecha, con cómo conseguirla.')}
    <div class="seg" role="group" aria-label="Tipo">${['char','other'].map(k=>`<button data-skind="${k}" aria-pressed="${SETS.kind===k}">${KIND_ES[k]}</button>`).join('')}</div>
    ${SETS.kind==='other'?`<div class="seg" role="group" aria-label="Modo"><button data-srush="0" aria-pressed="${!SETS.rush}">Speed Duel</button><button data-srush="1" aria-pressed="${SETS.rush}">Rush Duel</button></div>`:''}`
    : `${pageHead('Cajas y sets','Mirá qué cartas trae cada expansión del TCG, o cada caja y estructura de Duel Links. Tocá una carta para verla en grande, con cada rareza y su precio. Los personajes y las vías de obtención (tickets, eventos, misiones) están en la pestaña Obtención.')}
    <div class="seg" role="group" aria-label="Juego"><button data-sfmt="tcg" aria-pressed="${fmt==='tcg'}">TCG</button><button data-sfmt="dl" aria-pressed="${fmt==='dl'}">Duel Links</button></div>`;
'''
s = s[:a] + new_head + s[b:]
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 31 ok')
