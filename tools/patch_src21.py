"""Links de eventos: Duel Links Meta sirve sus artículos en /articles/<url de la API> y YuGiOh Meta sus mazos en /top-decks/<url de la API>;
las URLs crudas de las APIs daban 404. Se normalizan al armar el link. Backup: src.before_patch21.html."""
import shutil
shutil.copy('src.html', 'src.before_patch21.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, cnt=1):
    global s
    assert s.count(a) == cnt, (s.count(a), a[:90])
    s = s.replace(a, b)


rep("const dmy=d=>{",
    "const dlmUrl=u=>'https://www.duellinksmeta.com'+(u.startsWith('/articles/')?u:'/articles'+u);   // la API devuelve /events/... pero el sitio lo sirve en /articles/events/...\n"
    "const ygmDeckUrl=u=>'https://www.yugiohmeta.com'+(u.startsWith('/top-decks/')?u:'/top-decks'+u);   // idem: /<torneo>/<mazo>/... vive en /top-decks/<torneo>/<mazo>/...\n"
    "const dmy=d=>{")
rep('href="https://www.duellinksmeta.com${esc(e.u)}"', 'href="${esc(dlmUrl(e.u))}"')
rep('<a href="https://www.yugiohmeta.com${esc(u)}"', '<a href="${esc(ygmDeckUrl(u))}"')
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 21 ok')
