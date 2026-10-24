"""Builder: banned cards visible but not addable, Duel Links deck rules, deck notes, Genesys points per card, alternate arts, real-card PNG.
Works on src.html (backup: src.before_patch16.html). Each replacement asserts that its anchor is unique."""
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:80])
    s = s.replace(a, b)


# ---- state, draft, notes
rep("const DK={fmt:'tcg',name:'Mi mazo',main:{},extra:{},side:{},target:'auto',", "const DK={fmt:'tcg',name:'Mi mazo',notes:'',main:{},extra:{},side:{},target:'auto',")
rep("if(d) Object.assign(DK,{fmt:d.fmt||'tcg',name:d.name||'Mi mazo',main:d.main||{},extra:d.extra||{},side:d.side||{}}); }", "if(d) Object.assign(DK,{fmt:d.fmt||'tcg',name:d.name||'Mi mazo',notes:d.notes||'',main:d.main||{},extra:d.extra||{},side:d.side||{}}); }")
rep("localStorage.setItem('codex_draft',JSON.stringify({fmt:DK.fmt,name:DK.name,main:DK.main,extra:DK.extra,side:DK.side}));", "localStorage.setItem('codex_draft',JSON.stringify({fmt:DK.fmt,name:DK.name,notes:DK.notes,main:DK.main,extra:DK.extra,side:DK.side}));")

# ---- rules + adding cards
a = s.index("function dkAdd(n,forceSec){")
b = s.index("function dkDec(n,sec)")
s = s[:a] + r'''const toast = t => { const el=$('#toast'); if(!el) return; el.textContent=t; el.classList.add('on'); clearTimeout(toast.h); toast.h=setTimeout(()=>el.classList.remove('on'),4200); };
const DL_MIN=20, DL_MAX=30, DL_EXTRA=9;     // Duel Links: Main de 20 a 30, Extra hasta 9, sin Side Deck (por ahora)
function dkWhy(n){
  const c=CARDS[n];
  if(DK.fmt==='gen'&&c[C.GEN]===-3) return `${n}: en Genesys no se pueden usar monstruos Link ni Péndulo.`;
  return `No se pueden usar cartas prohibidas: ${n} está prohibida en ${FMT_ES[DK.fmt]}.`;
}
function dkRefuse(msg){ DK.msg=msg; toast(msg); }
function dkAdd(n,forceSec){
  const c=CARDS[n]; if(!c) return;
  const max=dkMax(n);
  if(max===0) return dkRefuse(dkWhy(n));
  if(dkCopies(n)>=max) return dkRefuse(`Máximo ${max} ${max===1?'copia':'copias'} de ${n} en ${FMT_ES[DK.fmt]}.`);
  const sec=forceSec||(DK.target==='side'&&DK.fmt!=='dl'?'side':(c[C.CAT]==='e'?'extra':'main'));
  if(sec==='side'&&DK.fmt==='dl') return dkRefuse('Duel Links todavía no tiene Side Deck.');
  if(sec==='extra'&&c[C.CAT]!=='e') return dkRefuse('Solo los monstruos del Extra Deck van en el Extra Deck.');
  if(sec==='main'&&c[C.CAT]==='e') return dkRefuse('Los monstruos del Extra Deck van en el Extra Deck'+(DK.fmt==='dl'?'.':' o en el Side Deck.'));
  DK[sec][n]=(DK[sec][n]||0)+1; DK.msg=''; dkDraft();
}
''' + s[b:]

# ---- issues
rep("  if(DK.fmt==='dl'){ if(m<30||m>40) out.push(`Main Deck: ${m} cartas (las recetas de Duel Links usan 30)`); }",
    "  if(DK.fmt==='dl'){ if(m<DL_MIN||m>DL_MAX) out.push(`Main Deck: ${m} cartas, tiene que tener entre ${DL_MIN} y ${DL_MAX}`); if(e>DL_EXTRA) out.push(`Extra Deck: ${e} cartas, el máximo es ${DL_EXTRA}`); if(sd) out.push(`Duel Links no tiene Side Deck: sacá las ${sd} cartas del Side`); }")
rep("    if(max===0){ out.push(`${n}: no se puede usar en ${FMT_ES[DK.fmt]}`); bad.add(n); }", "    if(max===0){ out.push(dkWhy(n)); bad.add(n); }")

# ---- text export / import with notes
rep(r"""function dkText(){ return SECS.map(s=>{ const rows=Object.entries(DK[s]); return rows.length?`# ${SEC_ES[s]}\n`+rows.map(([n,k])=>`${k}x ${n}`).join('\n'):''; }).filter(Boolean).join('\n\n'); }""",
    r"""function dkText(){ return SECS.map(s=>{ const rows=Object.entries(DK[s]); return rows.length?`# ${SEC_ES[s]}\n`+rows.map(([n,k])=>`${k}x ${n}`).join('\n'):''; }).concat(DK.notes.trim()?['# Cómo funciona\n'+DK.notes.trim()]:[]).filter(Boolean).join('\n\n'); }""")
rep(r"""    let sec='main';
    for(const line of t.split(/\r?\n/)){ const l=line.trim(); if(!l) continue;
      const h=l.match(/^#?\s*(main|extra|side)\b/i); if(h&&!/^\d/.test(l)){ sec=h[1].toLowerCase(); continue; }""",
    r"""    let sec='main', inNotes=false;
    for(const line of t.split(/\r?\n/)){ const l=line.trim();
      if(/^#\s*(c[oó]mo funciona|notas?)\b/i.test(l)){ inNotes=true; continue; }
      if(inNotes){ next.notes+=(next.notes?'\n':'')+line; continue; }
      if(!l) continue;
      const h=l.match(/^#?\s*(main|extra|side)\b/i); if(h&&!/^\d/.test(l)){ sec=h[1].toLowerCase(); continue; }""")
rep("  const next={main:{},extra:{},side:{}}; let miss=0, ok=0;", "  const next={main:{},extra:{},side:{},notes:''}; let miss=0, ok=0;")
rep("  DK.main=next.main; DK.extra=next.extra; DK.side=next.side; dkDraft();\n", "  DK.main=next.main; DK.extra=next.extra; DK.side=next.side; if(next.notes.trim()) DK.notes=next.notes.trim(); dkDraft();\n")

# ---- save / load / new / recipe / format switch
rep("const rec={id:Date.now().toString(36),name,fmt:DK.fmt,main:DK.main,extra:DK.extra,side:DK.side,ts:", "const rec={id:Date.now().toString(36),name,fmt:DK.fmt,notes:DK.notes,main:DK.main,extra:DK.extra,side:DK.side,ts:")
rep("DK.target='auto'; DK.msg=`Cargué la receta de ${DK.name}. Podés editarla.`; dkDraft();", "DK.target='auto'; DK.notes=''; DK.msg=`Cargué la receta de ${DK.name}. Podés editarla.`; dkDraft();")
rep("if(a==='new'){ DK.main={}; DK.extra={}; DK.side={}; DK.name='Mi mazo'; DK.msg='Mazo nuevo.'; dkDraft(); }", "if(a==='new'){ DK.main={}; DK.extra={}; DK.side={}; DK.name='Mi mazo'; DK.notes=''; DK.msg='Mazo nuevo.'; dkDraft(); }")
rep("if(r){ DK.fmt=r.fmt; DK.name=r.name; DK.main={...r.main};", "if(r){ DK.fmt=r.fmt; DK.name=r.name; DK.notes=r.notes||''; DK.main={...r.main};")
rep("else if(d.dkfmt){ DK.fmt=d.dkfmt; DK.msg=''; dkDraft(); render(); }", "else if(d.dkfmt){ DK.fmt=d.dkfmt; DK.msg=''; if(DK.fmt==='dl'&&DK.target==='side') DK.target='auto'; dkDraft(); render(); }")

# ---- tiles in the deck: Genesys points per card + alternate art button
a = s.index("function dkTile(n,k,sec){")
b = s.index("function dkModal(){")
s = s[:a] + r'''function dkTile(n,k,sec){
  const g=CARDS[n]?CARDS[n][C.GEN]:0;
  const pts=DK.fmt!=='gen'?'':g>0?`<span class="tm"><b class="vv" title="${g} puntos por copia">${g*k} pts</b>${k>1?`<small class="mini">${g} × ${k}</small>`:''}</span>`:g===-1?'<span class="tm"><b class="vv">? pts</b></span>':'<span class="tm"><small class="mini">0 pts</small></span>';
  return `<div class="tile s-${sec}${k>1?' k'+Math.min(k,3):''}"><span class="art">${cardImg(n)}<b class="cnt">×${k}</b>${(()=>{const b=banMark(n,DK.fmt==='dl'?'dl':DK.fmt==='tcg'?'tcg':'');return /class="bi/.test(b)?b:'';})()}</span><span class="tn">${esc(n)}</span>${pts}
    <span class="ctl"><i data-dec="${esc(n)}" data-sec="${sec}" title="Quitar una copia" role="button">−</i><i data-inc="${esc(n)}" data-sec="${sec}" title="Agregar una copia" role="button">+</i>${ALTS[n]?`<i data-artcyc="${esc(n)}" title="Cambiar el arte de la carta" role="button">◐</i>`:''}</span></div>`;
}
''' + s[b:]

# ---- builder view
a = s.index("function viewDeck(){")
b = s.index("/* ---------- ENRUTADO ---------- */")
s = s[:a] + r'''const dkExists = n => { const c=CARDS[n]; if(DK.fmt==='tcg') return c[C.BAN]>=0; if(DK.fmt==='gen') return c[C.GEN]!==-2; const d=c[C.DL]; return d>=0&&d<=4; };
function viewDeck(){
  const q=DK.q.trim();
  const names=searchNames(NAMES.filter(n=>(DK.type==='all'||CARDS[n][C.CAT]===DK.type)&&dkExists(n)&&CARDS[n][C.SH]!==-1),q,(a,b)=>usedCount(b)-usedCount(a)||a.localeCompare(b));
  const shown=names.slice(0,DK.limit);
  const issues=dkIssues(), pts=dkPoints(), dl=DK.fmt==='dl';
  const pickTile=n=>{ const c=CARDS[n]; const bad=dkMax(n)===0;
    let b=''; if(DK.fmt!=='gen'){ b=banMark(n,dl?'dl':'tcg'); b=/class="bi/.test(b)?b:''; } else if(bad) b=banIcon(0,'Los monstruos Link y Péndulo no se pueden usar en Genesys');
    const g=DK.fmt==='gen'&&c[C.GEN]>0?c[C.GEN]+' pts':'';
    const es=q?esName(n):'';
    return `<button class="tile add${bad?' unusable':''}" data-add="${esc(n)}" title="${esc(n)}${bad?' · no se puede usar en '+FMT_ES[DK.fmt]:''}"><span class="art">${cardImg(n)}<b class="plus">+</b>${b}</span><span class="tn">${esc(n)}</span><span class="tm">${g?`<b class="vv">${g}</b>`:''}${bad?`<b class="vv no">${DK.fmt==='gen'?'no permitida':'prohibida'}</b>`:''}${es?`<small class="mini">${esc(es)}</small>`:''}</span></button>`; };
  const sec=s=>{ const rows=Object.entries(DK[s]); if(!rows.length&&s!=='main') return ''; return `<div class="dsec ${s}"><h4>${SEC_ES[s]} · ${dkCount(s)} cartas</h4>${rows.length?`<div class="gal">${rows.map(([n,k])=>dkTile(n,k,s)).join('')}</div>`:'<div class="dkempty">Vacío. Buscá cartas a la derecha y tocalas para agregarlas, o importá un mazo.</div>'}</div>`; };
  return `${pageHead('Constructor de mazos','Armá un mazo con las reglas de cada formato, guardalo en este navegador y exportalo.',
    how('<p>Elegí el formato: la banlist del TCG, los puntos de Genesys y los cupos de límite de Duel Links se aplican mientras armás. Se ven todas las cartas del formato, también las prohibidas: si tocás una te avisa que no se puede usar.</p><p>Tocá una carta de la derecha para agregarla (los monstruos del Extra Deck van solos a su sección). Usá «Side» para mandar la carta al Side Deck. En cada carta del mazo podés restar o sumar copias, y cambiar el arte si tiene más de uno.</p><p>Duel Links: Main Deck de 20 a 30 cartas (las recetas actuales suelen usar 30), hasta 9 en el Extra Deck y sin Side Deck por ahora.</p><p>Debajo del mazo hay un espacio para escribir cómo funciona y sus combos. Exportá como YDK, enlace YDKE, imagen PNG con las cartas reales o lista de texto. También podés importar cualquiera de esos formatos y abrir las recetas del meta en el constructor.</p>','Cómo se usa'))}
    <div class="dkbar">
      <div class="seg" role="group" aria-label="Formato">${['tcg','gen','dl'].map(f=>`<button data-dkfmt="${f}" aria-pressed="${DK.fmt===f}">${FMT_ES[f]}</button>`).join('')}</div>
      <label class="sr" for="dk-name">Nombre del mazo</label><input type="text" id="dk-name" value="${esc(DK.name)}" placeholder="Nombre del mazo" maxlength="60">
      <button class="abtn pri" data-dk="save">Guardar</button><button class="abtn" data-dk="saved">Mis mazos (${DK.saved.length})</button>
      <button class="abtn" data-dk="import">Importar</button><button class="abtn" data-dk="export">Exportar</button><button class="abtn danger" data-dk="new">Nuevo</button>
    </div>
    <div class="dkgrid">
      <div class="dkdeck">
        <div class="dkstats">${rstat('Main',`${dkCount('main')}<em>${dl?DL_MIN+'–'+DL_MAX:'40–60'}</em>`)}${rstat('Extra',`${dkCount('extra')}<em>/ ${dl?DL_EXTRA:15}</em>`)}${dl?'':rstat('Side',`${dkCount('side')}<em>/ 15</em>`)}${DK.fmt==='gen'?rstat('Puntos',`${pts.t}<em>/ 100</em>`,`<div class="pbar${pts.t>100?' over':''}"><i style="width:${Math.min(100,pts.t)}%"></i></div>`):''}</div>
        <div class="dkissues">${issues.length?issues.map(x=>`<span>${esc(x)}</span>`).join(''):(dkCount('main')?'<span class="ok">El mazo cumple las reglas de '+FMT_ES[DK.fmt]+'</span>':'')}</div>
        <p class="dkmsg">${DK.modal?'':esc(DK.msg)}</p>
        ${sec('main')}${sec('extra')}${sec('side')}
        <div class="dsec notes"><h4>Cómo funciona y combos</h4><label class="sr" for="dk-notes">Cómo funciona el mazo y sus combos</label><textarea id="dk-notes" maxlength="4000" placeholder="Escribí el plan del mazo, la jugada básica, los combos principales, qué cartas guardar para el turno del rival…">${esc(DK.notes)}</textarea><p class="rnote">Se guarda con el mazo, se incluye en la imagen PNG y en la lista de texto.</p></div>
      </div>
      <div class="dkpick">
        <div class="filters"><label class="sr" for="dq">Buscar carta</label><input id="dq" type="search" placeholder="Buscar carta (inglés o español)" value="${esc(DK.q)}" autocomplete="off" spellcheck="false">
          <label class="sr" for="dkty">Tipo</label><select id="dkty"><option value="all">Todos los tipos</option><option value="m">Monstruos</option><option value="e">Extra Deck</option><option value="s">Hechizos</option><option value="t">Trampas</option></select></div>
        ${dl?'':`<div class="seg" style="margin:0" role="group" aria-label="Agregar a"><button data-dktarget="auto" aria-pressed="${DK.target==='auto'}">Agregar al mazo</button><button data-dktarget="side" aria-pressed="${DK.target==='side'}">Agregar al Side</button></div>`}
        <p class="lede" style="margin:0;font-size:.82rem">${names.length.toLocaleString('es-AR')} cartas de ${FMT_ES[DK.fmt]}, también las prohibidas (con la marca roja). Solo las que tienen arte.${q?' Acepta errores de tipeo.':''}</p>
        <div class="gal">${shown.map(pickTile).join('')}</div>
        ${names.length>shown.length?'<button class="abtn" data-dkmore="1">Mostrar más</button>':''}
      </div>
    </div>${dkModal()}</section>`;
}

''' + s[b:]

# ---- events: alternate art cycle, notes
rep("  const ctl=e.target.closest('[data-inc],[data-dec]');\n", "  const cyc=e.target.closest('[data-artcyc]');\n  if(cyc){ const n=cyc.dataset.artcyc, a=ALTS[n]; if(a){ setArt(n,a[(a.indexOf(cardId(n))+1)%a.length]); render(); } return; }\n  const ctl=e.target.closest('[data-inc],[data-dec]');\n")
rep("  else if(id==='dk-name'){ DK.name=e.target.value; dkDraft(); }", "  else if(id==='dk-name'){ DK.name=e.target.value; dkDraft(); }\n  else if(id==='dk-notes'){ DK.notes=e.target.value; dkDraft(); }")

# ---- toast element
rep("<main id=\"app\"></main>", "<main id=\"app\"></main>\n<div id=\"toast\" class=\"toast\" role=\"status\" aria-live=\"polite\"></div>")

open('src.html', 'w', encoding='utf-8').write(s)
print('patch16 builder ok')
