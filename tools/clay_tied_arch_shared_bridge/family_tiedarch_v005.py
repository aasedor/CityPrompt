"""Preserved v004 geometry with guarded outer quay ends beside stair openings."""
import family_tiedarch_v004 as previous
from family_tiedarch_v004 import PALETTE, LIGHT_RIG, manifest
import family_tiedarch as F
BASE_QUAYS = previous.compact_quays


def guarded_quays():
    BASE_QUAYS()
    b = F.RBatch()
    for side in (-1, 1):
        x = side * 25.95
        # Leave exactly the stair corridor between its two handrails open.
        for start, stop in ((-7.85, -4.73), (-.57, 7.85)):
            b.beam('rail', (x, start, F.ZQ + 1.17), (x, stop, F.ZQ + 1.17), .08)
            b.beam('rail', (x, start, F.ZQ + .1), (x, stop, F.ZQ + .1), .05)
            count = max(1, round((stop - start) / .15))
            for k in range(count + 1):
                y = start + (stop - start) * k / count
                width = .07 if k in (0, count) else .025
                b.beam('rail', (x, y, F.ZQ + .1), (x, y, F.ZQ + 1.17), width)
    b.flush('outer quay end guard returns')


def build():
    original = previous.compact_quays
    try:
        # The base builder already installs the single common plan transform.
        previous.compact_quays = guarded_quays
        previous.build()
    finally:
        previous.compact_quays = original
