"""Cuarta tanda del 2026-11-02: las 6 fichas que quedaron fuera después del refresco (dl/dark-magician, hat/geargia, hat/infernity, ocg/mitsurugi-chaos-ritual; ocg/sky-striker y ocg/trirealm-rift
solo necesitan que el validador acepte una lista sin Side, ver tools/playcards.py).  Una sola vez."""
import json, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FILES = ['src/playcards/' + f for f in sorted(os.listdir('src/playcards'))]
DATA = {f: json.load(open(f, encoding='utf-8')) for f in FILES}
TODAY = '2026-11-02'


def sheet(key):
    for f in FILES:
        if key in DATA[f]:
            return DATA[f][key]
    sys.exit('no encuentro ' + key)


def it(card, qty, es, en):
    return {'card': card, 'qty': qty, 'why': {'es': es, 'en': en}}


def keep(c, when, part, *cards):
    old = {x['card']: x for x in c['side'][when][part]}
    for n in cards:
        if n not in old:
            sys.exit('ya aplicado o cambió: %s en %s.%s' % (n, when, part))
    return [old[n] for n in cards]


def plan(key, when, ins, outs):
    c = sheet(key)
    c['side'][when] = {'in': ins, 'out': outs}
    c['updated'] = TODAY


TRIM_ES = 'Yendo segundo se recorta lo más angosto para meter una respuesta al tablero que el rival ya armó.'
TRIM_EN = 'Going second the narrowest card is trimmed to make room for an answer to the board the opponent already built.'

# dl/dark-magician: Lava Golem ya no está en la lista
c = sheet('dl/dark-magician')
plan('dl/dark-magician', 'first', keep(c, 'first', 'in', 'D.D. Crow', 'Ghost Belle & Haunted Mansion'),
     [it('Soul Servant', 1, 'Es la carta de ranura libre de la lista; yendo primero se cede por una interrupción del Cementerio.', "It is the list's flex slot; going first it is traded for a Graveyard interruption."),
      it('Illusion of Chaos', 1, 'Dos copias son más de las que hacen falta; se recorta una para sumar techs.', 'Two copies are more than needed; one is trimmed to add techs.')])

# hat/geargia: Trap Stun y Needle Ceiling ya no están en el Main; el Side trae solo 1 Maxx "C"
c = sheet('hat/geargia')
plan('hat/geargia', 'first', keep(c, 'first', 'in', 'Black Horn of Heaven', 'Debunk'),
     keep(c, 'first', 'out', 'Mind Control') + [it('Compulsory Evacuation Device', 1, 'Sin monstruos rivales en el campo en el primer turno no tiene blanco.', 'With no opposing monsters on the field in the first turn it has no target.')])
plan('hat/geargia', 'second', [it('D.D. Crow', 1, 'Efecto rápido desde la mano: destierra una carta del Cementerio rival.', "Quick Effect from hand: banishes a card from the opponent's GY."),
                               it('Debunk', 1, 'Anula un efecto activado desde la mano o el Cementerio del rival.', "Negates an effect the opponent activates from the hand or the GY.")],
     [it('Dark Hole', 1, 'Destruye también tus propios monstruos, y el mazo necesita mantener sus Xyz.', 'It also destroys your own monsters, and the deck needs to keep its Xyz.'),
      it('Fire Hand', 1, TRIM_ES, TRIM_EN)])

# hat/infernity: Night Beam no está en el Side; Vanity's Emptiness juega 2
c = sheet('hat/infernity')
plan('hat/infernity', 'second', [it('Dark Hole', 1, 'Destruye todos los monstruos del campo: rompe el tablero que el rival armó yendo primero.', 'Destroys every monster on the field: it breaks the board the opponent built going first.'),
                                 it('Mind Control', 1, 'Toma un monstruo rival hasta el final del turno: sirve contra el boss de su tablero.', "Takes an opposing monster until the end of the turn: it works against the boss of their board.")],
     [it("Vanity's Emptiness", 2, "Bloquea también tus propias Invocaciones Especiales, que necesitás para romper el campo.", "It also blocks your own Special Summons, which you need to break the board.")])

# ocg/mitsurugi-chaos-ritual: Solemn Judgment no está en el Side y el Main juega Fuwalos (no Purulia)
c = sheet('ocg/mitsurugi-chaos-ritual')
plan('ocg/mitsurugi-chaos-ritual', 'first',
     keep(c, 'first', 'in', 'Nibiru, the Primal Being') + [it('Dominus Impulse', 1, 'Si el rival controla una carta se activa desde la mano y niega el efecto que invoca por Especial: corta la jugada rival sin gastar el turno.', 'If the opponent controls a card it activates from hand and negates the effect that Special Summons: it cuts the opposing play without spending your turn.')],
     [it('Mulcharmy Fuwalos', 2, 'Solo se activa sin cartas en tu campo; yendo primero con mesa queda muerta.', 'It only activates with no cards on your field; going first with a board it sits dead.')])

for key in ('ocg/sky-striker', 'ocg/trirealm-rift'):
    sheet(key)['updated'] = TODAY       # sin cambios de contenido: su lista no publica Side y el validador ya lo acepta

for f, d in DATA.items():
    open(f, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('ok')
