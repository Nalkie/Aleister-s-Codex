"""2026-11-03: the Side of four lists changed (the downloaded decks), so the plans of adv/chaos-ritual, adv/invoked, adv/kewl-tune and adv/maliss name cards the lists no longer side.
Each plan is rewritten with cards the list does carry in its Side.  The new reasons are written from the card text of src/ygo_all.json; not played in the game.  Run once from the project root."""
import json, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = 'src/playcards/adv.json'
D = json.load(open(F, encoding='utf-8'))
TODAY = '2026-11-03'


def it(card, qty, es, en):
    return {'card': card, 'qty': qty, 'why': {'es': es, 'en': en}}


def old(key, when, part, card):
    for x in D[key]['side'][when][part]:
        if x['card'] == card:
            return x
    sys.exit('ya aplicado o cambió: %s %s.%s %s' % (key, when, part, card))


def plan(key, when, ins, outs):
    D[key]['side'][when] = {'in': ins, 'out': outs}
    D[key]['updated'] = TODAY


ACCUSATION = old('adv/maliss', 'first', 'in', 'Solemn Accusation')
ARREST = it('Mistaken Arrest', 2, 'Hasta el final de tu próximo turno nadie puede agregar cartas del Deck a la mano salvo robando: corta las búsquedas del rival.',
            'Until the end of your next turn nobody can add cards from the Deck to the hand except by drawing: it cuts the opponent\'s searches.')
TRUNADE = it('Hey, Space Trunade!', 1, 'Devuelve hasta 2 cartas del campo a la mano: abre el tablero rival para el turno de quiebre.',
             'Returns up to 2 cards from the field to the hand: it opens the opposing board for the breaking turn.')
CALLED = it('Called by the Grave', 1, 'Destierra un monstruo del Cementerio rival y niega a los de su mismo nombre hasta el final del turno siguiente: protege el tablero contra su recuperación.',
            'Banishes a monster from the opponent\'s GY and negates those with its name until the end of the next turn: it protects the board against their recovery.')
DROLL = it('Droll & Lock Bird', 1, 'Se cede una interrupción angosta para meter la respuesta.', 'A narrow interruption is given up to make room for the answer.')

# adv/chaos-ritual
k = 'adv/chaos-ritual'
plan(k, 'first', [old(k, 'first', 'in', 'Solemn Judgment'), {**ACCUSATION, 'qty': 1}], [old(k, 'first', 'out', 'Mulcharmy Fuwalos')])
plan(k, 'second', [old(k, 'second', 'in', 'Nibiru, the Primal Being'), TRUNADE], [old(k, 'second', 'out', 'Mulcharmy Fuwalos'), DROLL])
# adv/invoked
k = 'adv/invoked'
plan(k, 'first', [old('adv/maliss', 'first', 'in', 'Solemn Judgment'), {**ACCUSATION, 'qty': 2}], [old(k, 'first', 'out', 'Mulcharmy Fuwalos')])
# adv/kewl-tune
k = 'adv/kewl-tune'
plan(k, 'first', [old(k, 'first', 'in', 'Mannadium Reframing'), CALLED], [old(k, 'first', 'out', 'Droll & Lock Bird')])
# adv/maliss
k = 'adv/maliss'
plan(k, 'first', [old(k, 'first', 'in', 'Solemn Judgment'), ARREST], [old(k, 'first', 'out', 'Mulcharmy Fuwalos')])
json.dump(D, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('ok')
