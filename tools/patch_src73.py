"""Ruleta de decks: dos series nuevas, Arc-V ('av') y VRAINS ('vr').  Cada una con su color (--ac-av rosa, --ac-vr dorado) en el selector de series, la rueda y el resultado.
Backup: src.before_patch73.html."""
import shutil

shutil.copy('src.html', 'src.before_patch73.html')
s = open('src.html', encoding='utf-8').read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


rep("--ac-tcg:#0a8fb8; --ac-gen:#7a49d6; --ac-dl:#10935e; --ac-md:#d4621f; --ac-tool:#3a63d6;", "--ac-tcg:#0a8fb8; --ac-gen:#7a49d6; --ac-dl:#10935e; --ac-md:#d4621f; --ac-tool:#3a63d6; --ac-av:#d63e78; --ac-vr:#b8860b;")
rep("--ac-tcg:#4ee1ff; --ac-gen:#b78bff; --ac-dl:#3ddc97; --ac-md:#ff9a5c; --ac-tool:#8fb4ff;", "--ac-tcg:#4ee1ff; --ac-gen:#b78bff; --ac-dl:#3ddc97; --ac-md:#ff9a5c; --ac-tool:#8fb4ff; --ac-av:#ff7aa8; --ac-vr:#ffd25a;", 2)
rep(".rs-zx{--sc:var(--ac-gen)}", ".rs-zx{--sc:var(--ac-gen)} .rs-av{--sc:var(--ac-av)} .rs-vr{--sc:var(--ac-vr)}")
rep("ROU_SERIES=['dm','gx','5d','zx'];", "ROU_SERIES=['dm','gx','5d','zx','av','vr'];")
rep("zx:['ZEXAL','--ac-gen']};", "zx:['ZEXAL','--ac-gen'],av:['ARC-V','--ac-av'],vr:['VRAINS','--ac-vr']};")
open('src.html', 'w', encoding='utf-8').write(s)
print('patch 73 ok')
