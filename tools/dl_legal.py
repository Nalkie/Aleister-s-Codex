"""Duel Links banlist rules and power-ranking tiers, in one place so every consumer applies the same ones.

Banlist (Konami / Duel Links Meta, field banStatus of src/dl_bans.json):
  * Forbidden: 0 copies.
  * Limited 1 / 2 / 3: a limit shared by the whole group, not by each card. A deck may hold at most 1 / 2 / 3 cards in
    total out of all the cards that carry that label (two Limited 1 cards cannot be played together, not even one
    copy of each). Main, Extra and Side Deck count together.
  * Any card: at most 3 copies.
Rush Duel has its own copy of the list (the same card can have a different status in each format).

Tiers (Duel Links Meta "power rankings"): points from the latest 200 tournament tops (50 in Rush), computed by the
site from every community tournament. The tier is the band the points fall in; below the last band there is no tier.
"""
import json, os, re

# (minimum power, tier). The lower bound of each band is inclusive: Horus at exactly 27.0 is listed as Tier 1.
POWER_BANDS = {
    'speed': ((27, 1), (16, 2), (6, 3)),
    'rush': ((12, 1), (7, 2), (3, 3)),
}


def tier_of(power, fmt):
    """Tier 1-3 for a power ranking value, or None when the deck is below the last band (or has no power at all)."""
    if power is None:
        return None
    for floor, tier in POWER_BANDS[fmt]:
        if power >= floor:
            return tier
    return None


def load_bans(path='src/dl_bans.json'):
    """{(card name, is_rush): limit} where limit is 0 (forbidden) or 1-3 (the shared group), for the cards on the list."""
    out = {}
    for x in json.load(open(path, encoding='utf-8')):
        s = x.get('banStatus')
        if not s:
            continue
        if s == 'Forbidden':
            out[(x['name'], bool(x.get('rush')))] = 0
        else:
            m = re.match(r'Limited (\d)', s)
            if m:
                out[(x['name'], bool(x.get('rush')))] = int(m.group(1))
    return out


def violations(counts, bans, rush=False):
    """Why a deck is illegal. counts = {card name: copies in Main + Extra + Side}. Empty list when it is legal."""
    out, groups = [], {}
    for name, n in counts.items():
        if n <= 0:
            continue
        if n > 3:
            out.append(f'{name} x{n}: más de 3 copias')
        lim = bans.get((name, bool(rush)))
        if lim is None:
            continue
        if lim == 0:
            out.append(f'{name}: prohibida')
        else:
            groups.setdefault(lim, []).append((name, n))
    for lim, cards in sorted(groups.items()):
        total = sum(n for _, n in cards)
        if total > lim:
            out.append(f'Límite {lim}: {total} cartas, máximo {lim} (' + ', '.join(f'{a} x{b}' for a, b in cards) + ')')
    return out


def deck_counts(sections):
    """{card name: copies} from {'main': [[name, copies, ...], ...], 'extra': [...], 'side': [...]} (rows may carry extra fields)."""
    c = {}
    for sec in ('main', 'extra', 'side'):
        for row in sections.get(sec, []):
            c[row[0]] = c.get(row[0], 0) + row[1]
    return c


def api_deck_counts(deck):
    """Same, for a deck as the Duel Links Meta API returns it ({'main': [{'card': {'name'}, 'amount'}, ...], ...})."""
    c = {}
    for sec in ('main', 'extra', 'side'):
        for e in deck.get(sec, []):
            c[e['card']['name']] = c.get(e['card']['name'], 0) + e['amount']
    return c
