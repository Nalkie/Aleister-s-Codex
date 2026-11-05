"""2026-11-04: playability of the thematic roulette decks (tools/playable.py).  Each deck below had an Extra Deck monster the Main Deck could never pay for (a Fusion without
Polymerization, a Synchro without the Tuner or the level, a Rank without two monsters of its level) or too few monsters to start.  The fix adds the few cards that make the Extra Deck
reachable, as `fill` rows (the era note says why), and never touches the anime cards.  Run once from the project root:  python tools/patch_roulette_playable_nov04.py"""
import json, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POLY = 'Polymerization'
# deck id -> [(card, copies, why)]   (the why is shown in the ref of the row: Spanish, short)
FIX = {
    'odion-trap-guardian-thematic': [(POLY, 2, 'Master of Oz es una Fusión: sin Polymerization no se puede invocar'), ('Big Koala', 2, 'material de Master of Oz'), ('Des Kangaroo', 2, 'material de Master of Oz')],
    'tristan-taylor-warriors-machines-thematic': [(POLY, 1, 'Super Roboyarou es una Fusión: sin Polymerization no se puede invocar'), ('Roboyarou', 1, 'material de Super Roboyarou'),
                                                  ('Robolady', 1, 'material de Super Roboyarou')],
    'yami-bakura-nightmare-troubadour-underworld': [(POLY, 1, 'The Duke of Demise es una Fusión: sin Polymerization no se puede invocar')],
    'yami-bakura-wc-2008-vampires': [(POLY, 2, 'Reaper on the Nightmare es una Fusión (Spirit Reaper + Nightmare Horse): sin Polymerization no se puede invocar')],
    'yami-yugi-world-championship-2016-atem': [('Apprentice Magician', 1, 'arranque: monstruo de nivel bajo del arquetipo Mago'), ('Breaker the Magical Warrior', 1, 'arranque del arquetipo Mago'),
                                               ('Skilled Dark Magician', 1, 'arranque del arquetipo Mago'), ("Magician's Valkyria", 1, 'arranque del arquetipo Mago')],
    'jim-fossil-thematic': [('Millennium Golem', 2, 'Fossil Warrior Skull Knight pide una Roca y un monstruo de nivel 5 o 6: la Roca de nivel 6 lo hace posible')],
    'tania-amazoness-thematic': [(POLY, 2, 'Amazoness Pet Liger es una Fusión: sin Polymerization no se puede invocar')],
    'aporia-transer-genex': [('Genex Controller', 2, 'Genex Ally Triarm pide a Genex Controller como Tuner')],
    'devack-transer-beasts': [('Dark Resonator', 2, 'Zeman the Ape King pide un Tuner DARK más una Bestia: Dark Resonator (nivel 3) más Berserk Gorilla (nivel 4) suma 7')],
    'tetsu-tf5-stygian': [('Dark Resonator', 2, 'Tuner Demonio de nivel 3: con Stygian Street Patrol (nivel 4) suma 7 para Chaos King Archfiend y Psychic Lifetrancer')],
    'tetsu-tf6-warriors': [('Jutte Fighter', 2, 'Goyo Guardian pide un Tuner TIERRA: Jutte Fighter (nivel 2) más un monstruo de nivel 4 suma 6'), ('Nimble Momonga', 2, 'Junk Warrior pide Junk Synchron más un no Tuner: Momonga (nivel 2) suma nivel 5'), ('Turret Warrior', 2, 'Junk Destroyer: Junk Synchron más un monstruo de nivel 5 suma 8')],
    'mizar-thematic': [('Photon Crusher', 3, 'arranque LIGHT de nivel 4 que se invoca de Normal: el Main solo tenía 8 monstruos así')],
    'yusei-vjump-synchron': [],
    'aporia-transer-monarch': [],
    'bruno-transer-hope': [('Nimble Momonga', 2, 'Junk Warrior pide Junk Synchron más un no Tuner: Momonga (nivel 2) suma nivel 5'), ('Jutte Fighter', 2, 'Goyo Guardian pide un Tuner TIERRA: Jutte Fighter (nivel 2) más un monstruo de nivel 4 suma 6')],
    'rio-ice-winged-beast-thematic': [('Sirenorca', 3, 'Ice Princess Zereort pide 2 Bestias Aladas de nivel 5')],
}
# Anime Extra Deck monsters whose own Tuner is not in the list and cannot be added without rebuilding it: dropped with the reason (sheet `drop`).
DROP = {'aporia-transer-monarch': [('Geo Genex', 'Pide a Genex Controller más un no Tuner TIERRA que la lista no juega'), ('Thermal Genex', 'Pide a Genex Controller más un no Tuner FUEGO que la lista no suma'),
                                   ('Vindikite R-Genex', 'Pide un Tuner Genex más un no Tuner VIENTO de nivel 5 que la lista no juega'), ('Windmill Genex', 'Pide a Genex Controller más un no Tuner VIENTO de nivel 4 que la lista no juega')],
        'aporia-transer-genex': [('Ancient Sacred Wyvern', 'Pide un Tuner LIGHT que la lista no juega')],
        'yusei-vjump-synchron': [('Drill Warrior', 'Pide a Drill Synchron, que la lista no juega'), ('Nitro Warrior', 'Pide a Nitro Synchron, que la lista no juega'),
                                 ('Road Warrior', 'Pide a Road Synchron, que la lista no juega')]}
PLAYREF = 'Jugabilidad (herramienta tools/playable.py): '


def main():
    done = 0
    for f in sorted(os.listdir('src/roulette')):
        if not f.endswith('.json'):
            continue
        path = 'src/roulette/' + f
        data = json.load(open(path, encoding='utf-8'))
        touched = False
        for key, rows in FIX.items():
            if key not in data:
                continue
            touched = touched or False
            add = data[key].setdefault('add', [])
            for card, why in DROP.get(key, []):
                if not any(x[0] == card for x in data[key].setdefault('drop', [])):
                    data[key]['drop'].append([card, why])
                    touched = True
            for card, qty, why in rows:
                if any(a[0] == card and str(a[4]).startswith(PLAYREF) for a in add):
                    continue
                add.append([card, qty, 'fill', '', PLAYREF + why])
                touched = True
                done += 1
        if touched:
            json.dump(data, open(path, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
    print('rows added:', done)


if __name__ == '__main__':
    main()
