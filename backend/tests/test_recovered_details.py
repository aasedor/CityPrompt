import json
from pathlib import Path

from app.api.v1.project_details import Prop, _DETAIL_MODELS


def test_recovered_catalogue_can_persist_and_holds_are_excluded():
    root = Path(__file__).resolve().parents[2]
    rows = json.loads((root / "frontend/src/features/parks/recoveredDetails.json").read_text())
    assert rows
    for row in rows:
        prop = Prop(id="qa-1", lng=-114.1, lat=51.05, angle=45, variant=row["id"])
        assert prop.variant == row["id"]
    assert not any("corten-planter-bench-v1" in v for v in _DETAIL_MODELS["props"])
