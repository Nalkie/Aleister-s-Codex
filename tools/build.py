import json, re, os

ids = json.load(open('ids.json', encoding='utf-8'))
s = open('src.html', encoding='utf-8').read()

STR = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"")
used = set()
for m in re.finditer(r"\b[PN]\(\[(.*?)\]", s, re.S):
    for q in STR.finditer(m.group(1)):
        t = q.group(1) if q.group(1) is not None else q.group(2)
        used.add(t.replace("\\'", "'"))
for m in re.finditer(r"art:'([^']*)'", s):
    used.add(m.group(1))

missing = sorted(u for u in used if u not in ids)
print('cards used:', len(used), 'missing ids:', missing)

sub = {k: v for k, v in ids.items() if k in used}
out = s.replace('/*__IDS__*/{}', json.dumps(sub, ensure_ascii=False))
assert out != s
open('index.html', 'w', encoding='utf-8').write(out)

need = {str(v) + '.jpg' for v in sub.values()}
for f in os.listdir('images'):
    if f not in need:
        os.remove('images/' + f)
print('images kept', len(os.listdir('images')))
