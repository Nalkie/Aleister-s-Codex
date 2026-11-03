"""Placement of a tournament deck as YuGiOh Meta publishes it: 1, 2, 3.5 (Top 4), 8 (Top 8), ...  Shared by build_db.py (TCG / Genesys events) and formats_meta.py (OCG events)."""


def in_top8(p):
    """True for a published placement of 1 to 8; 3.5 (Top 4) is a float, so `isinstance(p, int)` dropped every Top 4."""
    return isinstance(p, (int, float)) and not isinstance(p, bool) and 0 < p <= 8
