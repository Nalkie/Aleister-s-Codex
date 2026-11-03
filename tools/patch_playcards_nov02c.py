"""Tercera tanda del 2026-11-02: gen/angelechy-white-forest.  La lista de hoy tiene en el Side Cosmic Cyclone y Gravity Collapse (no Annihilate Retroglight, Mystical Space Typhoon ni Twin Twisters) y
juega Fuwalos en el Main (no Mulcharmy Purulia ni Fifty Fifty?).  Una sola vez."""
import json, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
f = 'src/playcards/gen.json'
d = json.load(open(f, encoding='utf-8'))
c = d['gen/angelechy-white-forest']
first, second = c['side']['first'], c['side']['second']
assert first['in'][0]['card'] == 'Annihilate Retroglight', 'ya aplicado'
gc = [x for x in first['in'] if x['card'] == 'Gravity Collapse'][0]
gc['qty'] = 2
first['in'] = [gc]
first['out'] = [{'card': 'Mulcharmy Fuwalos', 'qty': 2, 'why': {'es': 'Necesita que no controles cartas, algo que casi nunca pasa yendo primero tras armar el tablero.', 'en': 'It needs you to control no cards, which almost never happens going first after building the board.'}}]
second['in'] = [{'card': 'Cosmic Cyclone', 'qty': 2, 'why': {'es': 'Por 1000 LP destierra una Mágica o Trampa del campo: rompe una carta rival ya puesta cuando vas segundo.', 'en': 'For 1000 LP it banishes a Spell or Trap on the field: it breaks an already set opposing card when you go second.'}}]
second['out'] = [{'card': 'Mulcharmy Fuwalos', 'qty': 2, 'why': {'es': 'Se recorta para meter una respuesta fija al fondo de campo rival.', 'en': "Trimmed to make room for a fixed answer to the opponent's backrow."}}]
open(f, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('ok')
