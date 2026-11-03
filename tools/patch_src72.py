"""Ruleta de decks: tocar una carta (la receta, los Reemplazos, la carta insignia) abre una vista previa en una ventana y ya no manda al buscador de golpe.  La ventana muestra la
carta en grande, su nombre en español, tipo, texto, estadísticas y los límites por formato; abajo, «Ver en el buscador» lleva a la ficha completa como antes.  Se cierra con Cerrar,
Esc o tocando fuera, y devuelve el foco a la carta.  Backup: src.before_patch72.html."""
import shutil

shutil.copy('src.html', 'src.before_patch72.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep("function rouVersion(id){",
    "const ROU_PV={open:false,from:null};\n"
    "function rouPvClose(){ const m=document.getElementById('rou-pv'); if(m) m.remove(); document.removeEventListener('keydown',rouPvKey); ROU_PV.open=false; const f=ROU_PV.from; ROU_PV.from=null; if(f&&document.contains(f)) f.focus({preventScroll:true}); }\n"
    "function rouPvKey(e){ if(e.key==='Escape') rouPvClose(); else if(e.key==='Tab'){ const m=document.getElementById('rou-pv'); if(!m) return; const f=[...m.querySelectorAll('button')]; if(!f.length) return; const a=f[0], z=f[f.length-1]; if(e.shiftKey&&document.activeElement===a){ e.preventDefault(); z.focus(); } else if(!e.shiftKey&&document.activeElement===z){ e.preventDefault(); a.focus(); } } }\n"
    "async function rouPreview(name){      // vista previa de una carta de la ruleta, sin salir de la ruleta\n"
    "  const n=canon(name); if(!CARDS[n]) return; rouPvClose(); ROU_PV.from=document.activeElement; ROU_PV.open=true;\n"
    "  document.body.insertAdjacentHTML('beforeend',`<div class=\"modal rou-pvbd\" id=\"rou-pv\"><div class=\"mbox rou-pvbox\" role=\"dialog\" aria-modal=\"true\" aria-label=\"Vista previa de la carta\">\n"
    "    <header><h3>${esc(n)}</h3><button class=\"abtn\" data-rpvclose=\"1\">Cerrar</button></header>\n"
    "    <div class=\"rou-pvbody\"><div class=\"rou-pvimg bigcard\">${cardImg(n,true)}</div><div class=\"rou-pvtxt\"><p class=\"esn\" id=\"rpv-es\"></p><div class=\"chips\" id=\"rpv-chips\"></div><p class=\"eff\" id=\"rpv-eff\">Cargando…</p><div id=\"rpv-stats\"></div>${limitChips(n)}</div></div>\n"
    "    <div class=\"rou-acts\"><button class=\"abtn pri\" data-rpvgo=\"${esc(n)}\">Ver en el buscador</button></div></div></div>`);\n"
    "  document.addEventListener('keydown',rouPvKey); const cb=document.querySelector('#rou-pv [data-rpvclose]'); if(cb) cb.focus({preventScroll:true});\n"
    "  let d; try{ d=await getDetail(n); }catch(e){ const el=document.getElementById('rpv-eff'); if(el) el.textContent='No se pudo cargar el detalle de la carta.'; return; }\n"
    "  if(!document.getElementById('rou-pv')) return;\n"
    "  document.getElementById('rpv-eff').textContent=d.d||(d.dl?'Carta de Duel Links sin texto en la base TCG.':'');\n"
    "  ensureES(); const es=esName(n); document.getElementById('rpv-es').textContent=es?'En español: '+es:'';\n"
    "  document.getElementById('rpv-stats').innerHTML=monsterStats(d); document.getElementById('rpv-chips').innerHTML=d.ty?`<span class=\"chip\">${esc(d.ty)}</span>`:'';\n"
    "}\n"
    "function rouVersion(id){")
rep("  else if(d.card){ const was=mode, y=window.scrollY; goCard(d.card);",
    "  else if(d.card&&mode==='rou'){ rouPreview(d.card); }\n  else if(d.card){ const was=mode, y=window.scrollY; goCard(d.card);")
rep("  if(d.rver){ rouVersion(d.rver); return; }",
    "  if(d.rver){ rouVersion(d.rver); return; }\n  if(d.rpvclose){ rouPvClose(); return; }\n  if(d.rpvgo){ const n=d.rpvgo; rouPvClose(); goCard(n); render(); window.scrollTo(0,0); return; }")
rep("  const b=e.target.closest('button'); if(!b) return;\n  const d=b.dataset;",
    "  if(e.target.id==='rou-pv'){ rouPvClose(); return; }\n  const b=e.target.closest('button'); if(!b) return;\n  const d=b.dataset;")
rep(".rou-vers{display:flex",
    ".mbox.rou-pvbox{width:min(640px,100%)} .rou-pvbody{display:grid;grid-template-columns:minmax(0,230px) minmax(0,1fr);gap:var(--s4);align-items:start} .rou-pvimg .cf{display:block;width:100%} .rou-pvtxt{display:grid;gap:var(--s2);min-width:0} .rou-pvtxt .eff{margin:0}\n"
    "@media(max-width:640px){.rou-pvbody{grid-template-columns:minmax(0,1fr)} .rou-pvimg{max-width:230px;margin:0 auto}}\n.rou-vers{display:flex")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 72 ok')
