"""Rebuild index.html from src.html without redoing sprites and data: reuses the art tables of the last full build.
Run from build/ after tools/build_db.py has run once:  python tools/page_only.py"""
import datetime, json, re

prev = open('index.html', encoding='utf-8').read()
get = lambda name: re.search(r'const %s = (\{.*?\});' % name, prev).group(1)
def _uri(k):   # the side art is a CSS mask: browsers refuse masks loaded from files when the page is opened with a double click, a data URI always works
    import base64
    return 'data:image/png;base64,' + base64.b64encode(open(f'art/line-{k}.png', 'rb').read()).decode()

src = open('src.html', encoding='utf-8').read()
ygm = json.load(open('dl/ygmdata.json', encoding='utf-8'))
dld = json.load(open('dl/dldata.json', encoding='utf-8'))
out = src
out = out.replace('/*__GUIDEX__*/', open('tools/guide_extra.js', encoding='utf-8').read())
import i18n
out = i18n.apply(out)        # inglés: envuelve los textos en español con t() e inyecta los diccionarios (antes de meter los datos grandes)
out = out.replace('/*__ARTS__*/{}', get('ARTS'))
out = out.replace('/*__ARTPOS__*/{}', get('ARTPOS'))
out = out.replace('/*__ALIAS__*/{}', '{}')
out = out.replace('/*__YGMDATA__*/{}', json.dumps(ygm, ensure_ascii=False, separators=(',', ':')))
out = out.replace("/*__BUILT__*/''", repr(datetime.date.today().isoformat()))
out = out.replace('/*__GENIDS__*/{}', get('GENIDS'))
out = out.replace('/*__DLDATA__*/{}', json.dumps(dld, ensure_ascii=False, separators=(',', ':')))
out = out.replace('/*__LINE_ALEISTER__*/art/line-aleister.png', _uri('aleister')).replace('/*__LINE_ECCLESIA__*/art/line-ecclesia.png', _uri('ecclesia')).replace('/*__LINE_DL__*/art/line-dl.png', _uri('dl'))

open('index.html', 'w', encoding='utf-8').write(out)
print('index.html', len(out))
