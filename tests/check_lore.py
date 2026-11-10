"""Gate test de la sección Lore.  Sin red.  Run from the project root:  python tests/check_lore.py

Outcome: lo que la página muestra como historia de un arquetipo está completo, bilingüe, con cartas que existen y fuentes https directas.
  * tools/lore.problems() rechaza cada tipo de entrada mala (párrafo corto, carta inventada, URL de reddit, creador sin título, «banish», raya larga...)
  * Todas las entradas de src/lore/ pasan el validador y data/lore.js coincide con ellas
  * La página: pestaña Lore, ruta ?mode=lore, vista, carga en diferido, sin tocar la red
"""
import copy, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import lore

fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


WORDS = ' '.join(['palabra'] * 60)
WORDS_EN = ' '.join(['word'] * 60)


def good():
    return {'slug': 'demo', 'kind': 'archetype', 'name': 'Demo', 'badge': {'es': 'Un gancho', 'en': 'A hook'}, 'origin': {'es': 'Serie', 'en': 'Series'},
            'blocks': [{'h': {'es': 'Uno', 'en': 'One'}, 'p': {'es': WORDS, 'en': WORDS_EN}, 'cards': ['Dark Magician']} for _ in range(3)],
            'creators': [], 'sources': [{'name': 'Yugipedia: Demo', 'url': 'https://yugipedia.com/wiki/Demo', 'checked': '2026-11-07'}], 'notes': {'es': '', 'en': ''}}


names = lore.card_names()
check('Dark Magician' in names, 'the card base has Dark Magician (fixture sanity)')
check(lore.problems({'demo': good()}, names) == [], 'a well-formed entry passes')


def bad(mut, label, needle):
    e = good()
    mut(e)
    pr = lore.problems({'demo': e}, names)
    check(any(needle in x for x in pr), 'rejects: ' + label + ('' if any(needle in x for x in pr) else ' (got %s)' % pr[:2]))


bad(lambda e: e['blocks'][0]['p'].update(es='muy corto'), 'a short Spanish paragraph', 'palabras')
bad(lambda e: e['blocks'][0]['p'].update(en=' '.join(['w'] * 200)), 'a long English paragraph', 'palabras')
bad(lambda e: e['blocks'][0]['p'].update(en=WORDS), 'English identical to Spanish', 'idéntico')
bad(lambda e: e['blocks'][0].update(cards=['Carta Que No Existe']), 'a card that does not exist', 'no existe')
bad(lambda e: e['blocks'][0].update(cards=[]), 'a block with no cards', 'cartas')
bad(lambda e: e['blocks'][0].update(cards=['Dark Magician', 'Dark Magician Girl', 'Dark Magician of Chaos', 'Magician of Black Chaos']), 'a block with 4 cards', 'cartas')
bad(lambda e: e.update(blocks=e['blocks'][:2]), 'only 2 blocks', 'bloques')
bad(lambda e: e['badge'].update(es='x' * 95), 'a badge over 90 characters', 'caracteres')
bad(lambda e: e['badge'].update(en=''), 'an empty English badge', 'vacío')
bad(lambda e: e['blocks'][0]['p'].update(es=WORDS + ' banish'), 'banish in Spanish', 'desterrar')
bad(lambda e: e['blocks'][0]['h'].update(es='Título — largo'), 'an em dash', 'raya larga')
bad(lambda e: e.update(slug='otro'), 'a slug that is not the file name', 'slug')
bad(lambda e: e.update(kind='personaje'), 'a kind that is not archetype or character', 'kind')
bad(lambda e: e.pop('kind'), 'an entry with no kind', 'claves')
bad(lambda e: e.update(extra=1), 'an unknown key', 'claves')
bad(lambda e: e['sources'].append({'name': 'x', 'url': 'http://yugipedia.com/x', 'checked': '2026-11-07'}), 'an http source', 'https')
bad(lambda e: e['sources'].append({'name': 'x', 'url': 'https://www.reddit.com/r/yugioh/x', 'checked': '2026-11-07'}), 'a reddit source', 'no se puede abrir')
bad(lambda e: e['sources'].append({'name': 'x', 'url': 'https://www.youtube.com/watch?v=abc', 'checked': '2026-11-07'}), 'YouTube as a reading source', 'YouTube solo vale como creador')
bad(lambda e: e['sources'].append(dict(e['sources'][0])), 'a repeated URL', 'se repite')
bad(lambda e: e.update(sources=[]), 'no sources', 'fuentes')
cre = {'author': 'Canal', 'title': 'Título', 'url': 'https://www.youtube.com/watch?v=abc123', 'platform': 'YouTube', 'checked': '2026-11-07', 'why': {'es': 'Repaso', 'en': 'Overview'}}
e = good(); e['creators'] = [cre]
check(lore.problems({'demo': e}, names) == [], 'a verified-looking YouTube creator passes')
bad(lambda e: e.update(creators=[dict(cre, title='')]), 'a creator with no title', 'title')
bad(lambda e: e.update(creators=[dict(cre, url='https://www.youtube.com/@canal')]), 'a YouTube channel URL instead of a video', 'enlace directo')
bad(lambda e: e.update(creators=[dict(cre, url='https://twitter.com/x/status/1')]), 'a creator on twitter', 'no se puede abrir')
bad(lambda e: e.update(creators=[cre, dict(cre, url='https://www.youtube.com/watch?v=b'), dict(cre, url='https://www.youtube.com/watch?v=c')]), 'three creators', 'como máximo 2')
bad(lambda e: e.update(creators=[dict(cre, checked='ayer')]), 'a creator date that is not a date', 'fecha')

entries = lore.load_entries()
check(len(entries) >= 8, 'at least 8 archetypes have lore (%d)' % len(entries))
pr = lore.problems(entries, names)
check(pr == [], 'every lore entry validates' + ('' if not pr else ': ' + '; '.join(pr[:3])))
if os.path.exists('data/lore.js'):
    t = open('data/lore.js', encoding='utf-8').read()
    got = json.loads(t[t.index(',') + 1:-2])
    check([x['slug'] for x in got] == sorted(entries, key=lambda k: entries[k]['name'].lower()) and all(x == entries[x['slug']] for x in got), 'data/lore.js matches src/lore/')
else:
    check(False, 'data/lore.js exists (run python tools/lore.py)')

src = open('src.html', encoding='utf-8').read()
check('id="tab-lore" data-mode="lore"' in src and "lore:['Lore',viewLore]" in src and "lore:['lore','']" in src, 'the Lore tab, its mode and its route are wired')
check("loadData('lore')" in src and 'function viewLore' in src, 'the page loads data/lore.js on demand')
check('target="_blank" rel="noopener noreferrer"' in src[src.index('function loreEntry'):src.index('function viewLore')], 'source and creator links open safely in a new tab')
check('data-card="${esc(n)}"' in src[src.index('function loreEntry'):src.index('function viewLore')], 'each illustrating card opens in Cartas')
en = json.load(open('tools/i18n_en.json', encoding='utf-8'))
check(en.get('Lore de arquetipos, cartas y personajes') == 'Archetype, card and character lore', 'the section title is translated')
check("data-lkind=\"${k}\"" in src and 'LORE.kind' in src and "if(d.lkind){ LORE.kind=d.lkind; render(); return; }" in src, 'the Lore page filters by kind (Todo / Arquetipos / Personajes)')
check('class="lsrc"><summary>Fuentes y licencia' in src and 'Adaptado de Yugipedia' in src[src.index('class="lsrc"'):src.index('class="lsrc"') + 900] and '.lsrc>summary' in src, 'sources and license sit inside a collapsed details in every entry')
check(any(e['kind'] == 'character' for e in entries.values()), 'at least one character entry exists (%d)' % sum(1 for e in entries.values() if e['kind'] == 'character'))
print('failed:', len(fails))
sys.exit(1 if fails else 0)
