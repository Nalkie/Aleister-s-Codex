"""Estimación del precio de una versión: más sobria (el patch 58 inflaba las rarezas altas).
  1. mediana de las otras impresiones de la misma rareza de esa carta
  2. la impresión con precio de la rareza más cercana de esa carta
  3. el precio de la carta por lo que suele valer esa rareza (o la más cercana con muestras suficientes)
Backup: src.before_patch59.html."""
import shutil
shutil.copy('src.html', 'src.before_patch59.html')
s = open('src.html', encoding='utf-8').read()
i = s.index('function verPrice(n,d,p){')
j = s.index('function pxVer(v){')
s = s[:i] + r'''function verPrice(n,d,p){      // precio de una versión: el propio o una estimación en la misma escala que los precios por impresión
  const own=nz(p[3]); if(own) return {u:own,est:0};
  const med=a=>{ a=a.slice().sort((x,y)=>x-y); const m=a.length>>1; return a.length%2?a[m]:(a[m-1]+a[m])/2; };
  const pn=d.pn||[], rk=x=>rarRank(x,'tcg');
  const same=pn.filter(x=>x!==p&&x[2]===p[2]&&nz(x[3])).map(x=>nz(x[3]));
  if(same.length) return {u:med(same),est:1,why:'rar'};
  const priced=pn.filter(x=>nz(x[3]));
  if(priced.length){ const dm=Math.min(...priced.map(x=>Math.abs(rk(x[2])-rk(p[2])))); return {u:med(priced.filter(x=>Math.abs(rk(x[2])-rk(p[2]))===dm).map(x=>nz(x[3]))),est:1,why:'near'}; }
  const c=CARDS[n], ref=c?nz(c[C.PR]):0; if(!ref) return null;
  const VR=(DBINFO&&DBINFO.vr)||{}, ks=Object.keys(VR);
  const k=ks.length?VR[ks.slice().sort((a,b)=>Math.abs(rk(a)-rk(p[2]))-Math.abs(rk(b)-rk(p[2]))||VR[b].n-VR[a].n)[0]].k:1;
  return {u:ref*k,est:1,why:'card'};
}
''' + s[j:]
a = "v.why==='prints'?'Estimado: esta versión no tiene precio, se calcula con las otras impresiones de esta carta según lo que suele valer cada rareza':"
assert s.count(a) == 1
s = s.replace(a, "v.why==='near'?'Estimado: esta versión no tiene precio, se usa la de la rareza más cercana de esta carta':")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 59 ok')
