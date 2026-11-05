"""Gate of tools/playable.py and of the thematic roulette decks.  Sin red, <2 s.  python tests/check_playable.py
Outcome: no thematic deck (a deck we build, not one the anime showed) has an Extra Deck monster its Main Deck can never summon, a Ritual without its Spell or fewer than 10 starters.
Unit part: the rules find the bricks the audit of 2026-11-04 found (Tania without Polymerization, Zeman without a DARK Tuner...) and accept the decks that are fine."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import playable as P
fails = []


def check(c, m):
    print(('ok   ' if c else 'FAIL ') + m)
    if not c:
        fails.append(m)


def deck(main, extra):
    return {'main': [[n, c, 0] for n, c in main], 'extra': [[n, c, 0] for n, c in extra]}


codes = lambda d: {c for c, _ in P.problems(d)}
FILL = [('Amazoness Archer', 3), ('Amazoness Blowpiper', 3), ('Amazoness Paladin', 3), ('Amazoness Swords Woman', 3), ('Amazoness Tiger', 3)]
# the slot parser
check(P.slot('2 Fiend and/or Zombie monsters')[0]['races'] == ['Zombie', 'Fiend'] or set(P.slot('2 Fiend and/or Zombie monsters')[0]['races']) == {'Fiend', 'Zombie'}, 'slot: Fiend and/or Zombie')
check(P.slot('1 Level 5 or 6 monster')[0]['levels'] == [5, 6], 'slot: Level 5 or 6')
check(P.slot('1 non-Tuner Beast-Type monster')[0]['races'] == ['Beast'], 'slot: Beast does not also match Beast-Warrior')
check(P.slot('1 Beast-Warrior monster')[0]['races'] == ['Beast-Warrior'], 'slot: Beast-Warrior')
check(P.slot('1 DARK Tuner')[0] == {'tuner': True, 'attr': 'DARK'}, 'slot: DARK Tuner')
# fusion
check('EXTRA-UNREACHABLE' in codes(deck(FILL, [('Amazoness Pet Liger', 1)])), 'a Fusion with no Polymerization is flagged (Tania before the fix)')
check('EXTRA-UNREACHABLE' not in codes(deck(FILL + [('Polymerization', 2)], [('Amazoness Pet Liger', 1)])), 'with Polymerization and the materials it is fine')
check('EXTRA-UNREACHABLE' in codes(deck([('Sangan', 3), ('Polymerization', 3)], [('Master of Oz', 1)])), 'Polymerization without Big Koala / Des Kangaroo is flagged')
check('EXTRA-UNREACHABLE' not in codes(deck([('Big Koala', 2), ('Des Kangaroo', 2), ('Polymerization', 2)], [('Master of Oz', 1)])), 'Master of Oz with its materials is fine')
check('EXTRA-UNREACHABLE' in codes(deck([('Spirit Illusion', 3), ('Spirit Reaper', 3), ('Nightmare Horse', 3)], [('Reaper on the Nightmare', 1)])), 'a card that only mentions Fusion Summon in a later effect is not an enabler')
# synchro
check('EXTRA-UNREACHABLE' in codes(deck([('Berserk Gorilla', 3), ('Krebons', 3)], [('Zeman the Ape King', 1)])), 'Zeman without a DARK Tuner is flagged')
check('EXTRA-UNREACHABLE' not in codes(deck([('Berserk Gorilla', 3), ('Dark Resonator', 2)], [('Zeman the Ape King', 1)])), 'Dark Resonator (3) + Berserk Gorilla (4) summons Zeman (7)')
# xyz
check('EXTRA-UNREACHABLE' in codes(deck([('Aurora Wing', 3)], [('Ice Princess Zereort', 1)])), 'an Xyz without two monsters of its type and level is flagged')
check('EXTRA-UNREACHABLE' not in codes(deck([('Sirenorca', 3)], [('Ice Princess Zereort', 1)])), 'two Level 5 Winged Beasts summon Ice Princess Zereort')
# ritual
check('RITUAL-NO-SPELL' in codes(deck([('Black Luster Soldier', 1)], [])), 'a Ritual Monster without its Spell is flagged')
check('FEW-STARTERS' in codes(deck([('Sangan', 3)], [])), 'too few starters is flagged')
# data: every thematic deck of data/roulette.js is playable
bad = {d['id']: P.problems(d) for d in P.load_decks() if d['kind'] == 'thematic' and P.problems(d)}
check(not bad, 'every thematic deck is playable' + (': %s' % {k: [c for c, _ in v] for k, v in bad.items()} if bad else ''))
n = sum(1 for d in P.load_decks() if d['kind'] == 'thematic')
check(n >= 60, '%d thematic decks audited' % n)
print('%d fails' % len(fails))
sys.exit(1 if fails else 0)
