"""Fichas tácticas que dejaron de coincidir con las listas del día (2026-11-02): se rehacen sus ajustes de Side contra la lista real (solo entra lo que está en el Side de la lista
y solo sale lo que el mazo juega).  Desde la raíz del proyecto:  python tools/patch_playcards_nov02.py
Una sola vez: un segundo intento no encuentra el texto viejo y se detiene.  Guarda el JSON igual que está (indent=1, sin salto final)."""
import json, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TODAY = '2026-11-02'
FILES = ['src/playcards/' + f for f in sorted(os.listdir('src/playcards'))]
DATA = {f: json.load(open(f, encoding='utf-8')) for f in FILES}


def sheet(key):
    for f in FILES:
        if key in DATA[f]:
            return DATA[f][key]
    sys.exit('no encuentro la ficha ' + key)


def it(card, qty, es, en):
    return {'card': card, 'qty': qty, 'why': {'es': es, 'en': en}}


def keep(c, when, part, *cards):
    """Las entradas de ese plan que ya valían (por nombre de carta), en el orden dado."""
    old = {x['card']: x for x in c['side'][when][part]}
    for n in cards:
        if n not in old:
            sys.exit('la ficha ya no trae %s en %s.%s' % (n, when, part))
    return [old[n] for n in cards]


def plan(key, when, ins, outs):
    c = sheet(key)
    c['side'][when] = {'in': ins, 'out': outs}
    c['updated'] = TODAY
    return c


FUW_ES = 'Se activa solo si no controlás cartas: yendo primero, con tablero, queda muerta en la mano.'
FUW_EN = 'It only activates if you control no cards: going first, with a board, it sits dead in hand.'
SKULL_ES = 'Niega efectos activados en el Cementerio rival: útil contra mazos que se recuperan desde ahí.'
SKULL_EN = "Negates effects activated in the opponent's GY: useful against decks that recover from there."
TRIM_ES = 'Yendo segundo se recortan las interrupciones más angostas para meter una respuesta al tablero que el rival ya armó.'
TRIM_EN = 'Going second the narrowest interruptions are trimmed to make room for an answer to the board the opponent already built.'
TYPH_ES = 'Destruye una Mágica/Trampa boca arriba que frene tu jugada, y se activa desde la mano si el rival controla 2 o más y vos ninguna.'
TYPH_EN = 'Destroys a face-up Spell/Trap that slows your play, and it can be activated from hand if the opponent controls 2 or more and you control none.'
SLOTH_ES = 'Robás tantas cartas como cartas controle el rival y devolvés al fondo del Mazo todas menos una; sirve cuando vas segundo.'
SLOTH_EN = 'Draw as many cards as the opponent controls, then put all but one back on the bottom of the Deck; it fits when you go second.'

# --- adv/elfnote
c = sheet('adv/elfnote')
plan('adv/elfnote', 'first', [it('Skull Meister', 2, SKULL_ES, SKULL_EN)], [it('Mulcharmy Fuwalos', 2, FUW_ES, FUW_EN)])
plan('adv/elfnote', 'second', keep(c, 'second', 'in', 'Typhoon'), [it('Droll & Lock Bird', 1, TRIM_ES, TRIM_EN), it('Ghost Ogre & Snow Rabbit', 1, TRIM_ES, TRIM_EN)])

# --- adv/kewl-tune
c = sheet('adv/kewl-tune')
plan('adv/kewl-tune', 'first', keep(c, 'first', 'in', 'Mannadium Reframing') + [it('Skull Meister', 2, SKULL_ES, SKULL_EN)],
     [it('Mulcharmy Fuwalos', 3, 'Necesita que no controles cartas: yendo primero queda muerta.', 'It needs you to control no cards: going first it is dead.')])
plan('adv/kewl-tune', 'second', keep(c, 'second', 'in', "Harpie's Feather Duster"), keep(c, 'second', 'out', 'Ghost Ogre & Snow Rabbit'))

# --- adv/maliss
c = sheet('adv/maliss')
plan('adv/maliss', 'first', [
    it('Solemn Warning', 1, 'Por 2000 LP niega una Invocación o una activación que invoque por Especial y la destruye: cubre el turno rival cuando el motor Maliss ya armó el tablero.',
       "For 2000 LP it negates a Summon or an activation that Special Summons, and destroys it: it covers the opponent's turn once the Maliss engine has built the board."),
    it('Solemn Judgment', 1, "Frena la invocación o la activación que más duele en el turno rival.", "Stops the Summon or activation that hurts most on the opponent's turn."),
    it('Solemn Accusation', 1, 'Niega la activación de una Mágica/Trampa rival; se puede activar el turno en que se Setea si revelás otra Trampa boca abajo.',
       'Negates the activation of an opposing Spell/Trap; it can be activated the turn it is Set if you reveal another face-down Trap.')],
    [it('Mulcharmy Fuwalos', 3, FUW_ES, FUW_EN)])
plan('adv/maliss', 'second', [it('Evenly Matched', 2, 'Al final de la Battle Phase, si el rival controla más cartas que vos, destierra boca abajo las que sobran; sin cartas propias se activa desde la mano. Respuesta a un tablero armado yendo segundo.',
                                 'At the end of the Battle Phase, if the opponent controls more cards than you, it banishes the extras face-down; with no cards of your own it activates from hand. An answer to a built board going second.')],
     keep(c, 'second', 'out', 'Gold Sarcophagus', 'Terraforming'))

# --- adv/invoked
c = sheet('adv/invoked')
plan('adv/invoked', 'first', [it('Skull Meister', 3, SKULL_ES, SKULL_EN)], [it('Mulcharmy Fuwalos', 3, FUW_ES, FUW_EN)])
plan('adv/invoked', 'second', keep(c, 'second', 'in', 'Nibiru, the Primal Being'), [it('Mulcharmy Fuwalos', 2, 'Se recortan para meter una respuesta al tablero rival.', 'Trimmed to make room for an answer to the opposing board.')])

# --- adv/angelechy (Witness of the Ancient y Glitch Clutch Nullgainer ya no están en la lista: se quita esa tercera ruta)
c = sheet('adv/angelechy')
plan('adv/angelechy', 'first', [it('Skull Meister', 3, SKULL_ES, SKULL_EN)], keep(c, 'first', 'out', 'Angelechy Opening to e4', 'Mulcharmy Fuwalos'))
c['side']['first']['out'][1]['qty'] = 1
plan('adv/angelechy', 'second', [it('Typhoon', 2, TYPH_ES, TYPH_EN)], [it('Droll & Lock Bird', 1, TRIM_ES, TRIM_EN)] + keep(c, 'second', 'out', 'Terraforming'))
c['starters'] = [s for s in c['starters'] if 'Witness of the Ancient' not in s['cards']]

# --- adv/artmage
c = sheet('adv/artmage')
plan('adv/artmage', 'first', [it('Infinite Impermanence', 2, 'Niega el efecto de un monstruo rival boca arriba y, sin cartas propias, se activa desde la mano: interrupción extra para el turno rival yendo primero.',
                                 "Negates a face-up opposing monster's effect and, with no cards of your own, it activates from hand: extra interruption for the opponent's turn when you go first.")],
     [it('Mulcharmy Fuwalos', 2, FUW_ES, FUW_EN)])
plan('adv/artmage', 'second', keep(c, 'second', 'in', 'Pot of Sloth') + [it('Typhoon', 1, TYPH_ES, TYPH_EN)],
     [it('Mulcharmy Fuwalos', 2, 'Se recorta para meter respuestas al tablero rival.', 'Trimmed to make room for answers to the opposing board.')])

# --- dl/royal-rebel-s: Heavenly Selection ya no está en la lista
c = sheet('dl/royal-rebel-s')
plan('dl/royal-rebel-s', 'first', keep(c, 'first', 'in', 'Widespread Ruin'),
     [it('Kheiron the Star Knight', 1, 'Su daño perforante solo importa si atacás; yendo primero no atacás el primer turno y Widespread Ruin ya cubre ese hueco.',
         'Its piercing damage only matters if you attack; going first you do not attack on turn 1 and Widespread Ruin already covers that gap.')])

# --- dl/horus: el mazo juega 1 Fuwalos; Lava Golem ya está en 3 copias (más sería romper la banlist)
c = sheet('dl/horus')
plan('dl/horus', 'first', keep(c, 'first', 'in', 'Ghost Ogre & Snow Rabbit'),
     [it('Mulcharmy Fuwalos', 1, 'Fuwalos solo se activa si no controlás cartas, y yendo primero ya tenés Walls o Canopic en la mesa en el turno del rival.',
         'Fuwalos only activates if you control no cards, and going first you already have Walls or Canopic on the table on the opponent\'s turn.')])
plan('dl/horus', 'second', [it('Dark Ruler No More', 1, 'Yendo segundo el rival ya armó cuerpos: Dark Ruler No More niega los efectos de todos sus monstruos un turno y evita el daño, la respuesta a un tablero armado que el mazo no tiene.',
                               "Going second the opponent already built bodies: Dark Ruler No More negates every opposing monster effect for a turn and prevents damage, the answer to a built board the deck lacks.")],
     keep(c, 'second', 'out', 'Soul Servant'))

# --- dl/snake-eye: Hey, Trunade! ya no está en la lista
c = sheet('dl/snake-eye')
plan('dl/snake-eye', 'first', keep(c, 'first', 'in', 'Droll & Lock Bird'),
     [it('Mulcharmy Fuwalos', 1, 'Solo se activa si no controlás cartas: yendo primero el tablero Snake-Eye ya está armado en el turno rival y queda muerta en la mano.',
         "It only activates if you control no cards: going first the Snake-Eye board is already built on the opponent's turn and it sits dead in hand.")])

for f, d in DATA.items():
    open(f, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('ok')
