"""Student authoring envelope; source programme hashes remain immutable."""
import json
from pathlib import Path

POLICY = json.loads((Path(__file__).resolve().parents[1] / 'data/streetRoutePolicy.json').read_text())
MAX_REPEATABLE_STREET_LENGTH_M = POLICY['maxRepeatableLengthM']


def native_street_max_length(variant_id):
    return POLICY['fixedSpanMaxLengthM'].get(variant_id, MAX_REPEATABLE_STREET_LENGTH_M)
