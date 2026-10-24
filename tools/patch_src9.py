"""Card detail: monster stats panel (attribute, level/rank/link, type, scale, ATK/DEF)."""
s=open('src.html',encoding='utf-8').read()
a="  $('#dx-chips').innerHTML="
assert s.count(a)==1
s=s.replace(a,"  $('#dx-stats').innerHTML=monsterStats(d);\n"+a,1)
b='    <div id="dx-tail"></div>'
assert s.count(b)==1
s=s.replace(b,'    <div id="dx-stats"></div>\n'+b,1)
fn='''const ATTR_ES={DARK:'Oscuro',LIGHT:'Luz',EARTH:'Tierra',WATER:'Agua',FIRE:'Fuego',WIND:'Viento',DIVINE:'Divino'};
function monsterStats(d){
  if(!d||!d.ty||!/Monster/.test(d.ty)||!d.st) return '';
  const [atk,def,lv,race,attr,lk,sc]=d.st, q=v=>v==null?'?':v;
  const link=/Link/.test(d.ty), xyz=/Xyz/.test(d.ty);
  const t=[];
  if(attr) t.push(['Atributo',`<i class="at at-${esc(attr)}"></i>${esc(ATTR_ES[attr]||attr)}`]);
  if(link) t.push(['Link',lk!=null?lk:'?']);
  else if(lv!=null) t.push([xyz?'Rango':'Nivel',`<span class="lvs">${lv}</span>`]);
  if(race) t.push(['Tipo',esc(race)]);
  if(sc!=null) t.push(['Escala',`${sc}`]);
  t.push(['ATK',q(atk)]); if(!link) t.push(['DEF',q(def)]);
  return `<div class="mstats">${t.map(([k,v])=>`<div><small>${k}</small><b>${v}</b></div>`).join('')}</div>`;
}
'''
s=s.replace("function cardDetail(n){",fn+"function cardDetail(n){",1)
css='''.mstats{display:grid;grid-template-columns:repeat(auto-fit,minmax(88px,1fr));gap:var(--s2);margin:var(--s3) 0}
.mstats>div{padding:var(--s2) var(--s3);border-radius:var(--r2);border:1px solid var(--line2);background:linear-gradient(150deg,color-mix(in srgb,var(--accent) 12%,var(--surface2)),var(--surface2))}
.mstats small{display:block;font:500 .64rem var(--f-data);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.mstats b{display:flex;align-items:center;gap:6px;font:700 1rem var(--f-display);line-height:1.3}
.mstats .lvs::before{content:"★ ";color:var(--t1)}
.at{width:12px;height:12px;border-radius:50%;display:inline-block;background:#9aa4d6}
.at-DARK{background:#8b5cf6}.at-LIGHT{background:#ffe27a}.at-EARTH{background:#b88a4a}.at-WATER{background:#4aa8ff}.at-FIRE{background:#ff6a4a}.at-WIND{background:#5fe0a0}.at-DIVINE{background:#ffd25a}
</style>'''
i=s.rindex('</style>'); s=s[:i]+css+s[i+8:]
open('src.html','w',encoding='utf-8').write(s)
