"""Ficha táctica de Duel Links: el cuarto bloque se llama «Skill y ajustes» y lista el Skill antes de los ajustes al ir primero o segundo (no hay Side Deck).  Backup: src.before_patch65.html."""
import shutil

shutil.copy('src.html', 'src.before_patch65.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b):
    global s
    assert s.count(a) == 1, a[:80]
    s = s.replace(a, b)


rep("${sec(4,'Plan de Side Deck',`<div class=\"pc-sides\">",
    "${sec(4,fmtKey==='dl'?'Skill y ajustes':'Plan de Side Deck',`${(c.skills||[]).length?`<ul>${c.skills.map(k=>`<li>${cn(k.name)} <span class=\"pc-why\">${L(k.why)}</span></li>`).join('')}</ul>`:''}<div class=\"pc-sides\">")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 65 ok')
