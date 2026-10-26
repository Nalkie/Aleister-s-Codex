"""Revisión 2: cartas más usadas y "Sobre ..." en todos los formatos del TCG, pills que no desbordan en móvil, "1 victoria", fecha local de hoy,
el constructor quita las cartas que no existen al pasar a un formato retro, texto de Goat para principiantes. Backup: src.before_patch28.html."""
import shutil
shutil.copy('src.html', 'src.before_patch28.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


# "1 victorias"
n = s.count("${d.wins} victorias")
assert n >= 3, n
s = s.replace("${d.wins} victorias", "${d.wins} ${d.wins===1?'victoria':'victorias'}")

# fecha local (no UTC) para "hoy"
rep("const dmy=d=>{", "const localToday=()=>{ const d=new Date(); return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0'); };\nconst dmy=d=>{")
assert s.count("const today=new Date().toISOString().slice(0,10)") == 2
s = s.replace("const today=new Date().toISOString().slice(0,10)", "const today=localToday()")

# cartas más usadas y "Sobre Advanced"
rep("  ${outsideSection(all,k,'Ganadores fuera del meta','Arquetipos que no llegan al tier 3 (menos de 2% del peso de resultados y menos de 2,5% de los decks) pero ganaron al menos un torneo en la muestra.')}\n  ${secHead(`Sobre ${I.n}`,I.lede)}",
    "  ${outsideSection(all,k,'Ganadores fuera del meta','Arquetipos que no llegan al tier 3 (menos de 2% del peso de resultados y menos de 2,5% de los decks) pero ganaron al menos un torneo en la muestra.')}\n  ${usage.length?secHead('Cartas más usadas',`Calculado sobre las ${listsTotal} listas analizadas de los ${withCards.length} arquetipos del ranking, solo cartas presentes en 2 o más mazos. Tocá una carta para verla.`)+cardChips(usage)+'</section>':''}\n  ${secHead(`Sobre ${I.n}`,I.lede)}")
rep("  const cnt=b=>Object.values(F.ban).filter(v=>v===b).length;\n  const safe=u=>", "  const usage=(()=>{ const m=new Map(); for(const d of withCards) for(const [n,p] of d.cards){ const e=m.get(n)||{s:0,k:0}; e.s+=d.lists*p/100; e.k++; m.set(n,e); } return [...m].filter(([,e])=>e.k>=2).sort((a,b)=>b[1].s-a[1].s).slice(0,36).map(([n,e])=>[n,Math.round(e.s/listsTotal*100)]); })();\n  const cnt=b=>Object.values(F.ban).filter(v=>v===b).length;\n  const safe=u=>")
rep("  return fmtBar(TCGF)+(TCGF==='adv'?viewTCGAdv():viewMetaFmt(TCGF));",
    "  return fmtBar(TCGF)+(TCGF==='adv'?viewTCGAdv()+viewAboutAdv():viewMetaFmt(TCGF));")
rep("function viewMetaFmt(k){", r'''function viewAboutAdv(){
  const I=RETRO_ES.adv;
  return `<section>${secHead(`Sobre ${I.n}`,I.lede).replace('<section>','')}
    <h3 style="margin-top:var(--s3)">Cómo se juega</h3><ul class="rrules">${I.rules.map(x=>`<li>${esc(x)}</li>`).join('')}</ul><p class="lede">${esc(I.meta)}</p>
    <p style="margin:var(--s3) 0"><button class="sbtn" data-gobfmt="tcg">Ver la banlist completa</button> <button class="sbtn" data-gotab="deck" data-dkf="tcg">Armar un mazo de ${I.n}</button></p></section>`;
}
function viewMetaFmt(k){''')

# constructor: al pasar a un formato retro se quitan las cartas que no existen
rep("  else if(d.dkfmt){ DK.fmt=d.dkfmt; DK.msg='';",
    "  else if(d.dkfmt){ DK.fmt=d.dkfmt; DK.msg=''; if(FMT_RETRO[DK.fmt]&&fmPool(DK.fmt)){ const gone=[]; for(const sec of SECS) for(const n of Object.keys(DK[sec])) if(fmLimit(DK.fmt,n)===-1){ gone.push(n); delete DK[sec][n]; } if(gone.length){ DK.msg=`Quité ${gone.length} ${gone.length===1?'carta que no existe':'cartas que no existen'} en ${FMT_ES[DK.fmt]}: ${gone.slice(0,4).join(', ')}${gone.length>4?'…':''}.`; toast(DK.msg); } }")

# Goat para principiantes
rep("'Entran Rescue Cat, Brain Control y Lightning Vortex; Confiscation y The Forceful Sentry pasan a prohibidas, y Delinquent Duo y Graceful Charity salen de la lista de prohibidas (quedan limitadas).'",
    "'Aparecen cartas nuevas de esa época como Rescue Cat, Brain Control y Lightning Vortex. Respecto de la lista anterior, Confiscation y The Forceful Sentry pasan a prohibidas, y Delinquent Duo y Graceful Charity dejan de estar prohibidas y quedan limitadas (1 copia).'")

# pills que no desbordan
rep(".fmtbar{margin:var(--s4) 0 0}", ".fmtbar{margin:var(--s4) 0 0}\n.seg.mini{flex-wrap:wrap;max-width:100%}\n.seg.mini .pill{max-width:100%;white-space:normal;overflow-wrap:anywhere}")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 28 ok')
