"""Estimación del precio de una versión sin precio propio, en la misma escala que los precios por impresión (patch 57 usaba el precio de la carta, que está en otra escala).
  1. otra impresión de la misma rareza de esa carta (mediana)
  2. las demás impresiones de la carta, llevadas a esta rareza con la proporción típica entre rarezas (data/index.js: vr.m)
  3. el precio de la carta por lo que suele valer esa rareza respecto de la carta (vr.k)
Backup: src.before_patch58.html."""
import shutil
shutil.copy('src.html', 'src.before_patch58.html')
s = open('src.html', encoding='utf-8').read()
i = s.index('function verPrice(n,d,p){')
j = s.index('function pxVer(v){')
s = s[:i] + r'''function verPrice(n,d,p){      // precio de una versión: el propio o una estimación en la misma escala que los precios por impresión
  const own=nz(p[3]); if(own) return {u:own,est:0};
  const med=a=>{ a=a.slice().sort((x,y)=>x-y); const m=a.length>>1; return a.length%2?a[m]:(a[m-1]+a[m])/2; };
  const pn=d.pn||[], VR=(DBINFO&&DBINFO.vr)||{};
  const same=pn.filter(x=>x!==p&&x[2]===p[2]&&nz(x[3])).map(x=>nz(x[3]));
  if(same.length) return {u:med(same),est:1,why:'rar'};
  const norm=pn.filter(x=>nz(x[3])&&VR[x[2]]).map(x=>nz(x[3])/VR[x[2]].m);
  if(norm.length&&VR[p[2]]) return {u:med(norm)*VR[p[2]].m,est:1,why:'prints'};
  const c=CARDS[n], ref=c?nz(c[C.PR]):0;
  return ref?{u:VR[p[2]]?ref*VR[p[2]].k:ref,est:1,why:'card'}:null;
}
''' + s[j:]
a = "v.why==='rar'?'Estimado: esta versión no tiene precio, se usa la mediana de las otras impresiones de la misma rareza de esta carta':'Estimado: esta versión no tiene precio, se usa el precio de la carta'"
assert s.count(a) == 1
s = s.replace(a, "v.why==='rar'?'Estimado: esta versión no tiene precio, se usa la mediana de las otras impresiones de la misma rareza de esta carta':v.why==='prints'?'Estimado: esta versión no tiene precio, se calcula con las otras impresiones de esta carta según lo que suele valer cada rareza':'Estimado: esta versión no tiene precio, se calcula con el precio de la carta según lo que suele valer esta rareza'")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 58 ok')
