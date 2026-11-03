"""Segunda tanda del 2026-11-02 (después de tools/patch_playcards_nov02.py): kewl-tune no juega Mulcharmy Fuwalos en el Main (está en el Side de la lista), así que sale otra interrupción
angosta; y la ficha gen/white-forest-azamina pasa a llamarse gen/angelechy-white-forest, que es como el ranking de gen llama hoy a ese mazo.  Una sola vez."""
import json, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TRIM_ES = 'Interrupciones angostas: yendo primero conviene cederlas por cartas que protejan el tablero que armás.'
TRIM_EN = 'Narrow interruptions: going first they are better swapped for cards that protect the board you build.'
f = 'src/playcards/adv.json'
d = json.load(open(f, encoding='utf-8'))
s = d['adv/kewl-tune']['side']['first']
assert s['out'][0]['card'] == 'Mulcharmy Fuwalos', 'ya aplicado'
s['out'] = [{'card': 'Droll & Lock Bird', 'qty': 2, 'why': {'es': TRIM_ES, 'en': TRIM_EN}}, {'card': 'Ghost Mourner & Moonlit Chill', 'qty': 1, 'why': {'es': TRIM_ES, 'en': TRIM_EN}}]
open(f, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
f = 'src/playcards/gen.json'
d = json.load(open(f, encoding='utf-8'))
if 'gen/white-forest-azamina' not in d:
    sys.exit('ya aplicado')
d = {('gen/angelechy-white-forest' if k == 'gen/white-forest-azamina' else k): v for k, v in d.items()}
d['gen/angelechy-white-forest']['updated'] = '2026-11-02'
open(f, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('ok')
