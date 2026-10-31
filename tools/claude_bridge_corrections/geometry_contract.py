"""Pure geometric constraints for the bounded Claude bridge correction batch."""
import math


def end_louvre_profile(xa, xb, left, right, base, top, reverse, clearance=.08):
    """A vertical slat clipped above its diagonal, in x/z face coordinates."""
    if not left <= xa < xb <= right or top <= base or right <= left:
        raise ValueError('Invalid end-bay/slat bounds')

    def lower(x):
        fraction = (right - x) / (right - left) if reverse else (x - left) / (right - left)
        return base + fraction * (top - base) + clearance

    za, zb = lower(xa), lower(xb)
    if max(za, zb) >= top:
        return None
    return [(xa, za), (xb, zb), (xb, top), (xa, top)]


def approach_stair_treads(deck_edge, deck_top, max_riser=.2, tread=.35):
    """Descending occupied tread intervals from a bridge landing to grade."""
    if min(deck_top, max_riser, tread) <= 0:
        raise ValueError('Stair dimensions must be positive')
    count = math.ceil(deck_top / max_riser)
    return [(deck_edge + i * tread, deck_edge + (i + 1) * tread,
             deck_top * (count - i) / count) for i in range(count)]
