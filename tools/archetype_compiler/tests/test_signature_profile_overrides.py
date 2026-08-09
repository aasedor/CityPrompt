from __future__ import annotations

import json


def test_extension_requires_explicit_declaration_to_override_existing_profile(tmp_path, monkeypatch):
    import signature_profiles

    base = tmp_path / "profiles.json"
    extensions = tmp_path / "profiles.d"
    extensions.mkdir()
    base.write_text(json.dumps({
        "schema": "architectural-signatures@1",
        "profiles": {"existing": {"identity": "old"}},
    }), encoding="utf-8")
    (extensions / "override.json").write_text(json.dumps({
        "schema": "architectural-signatures@1",
        "override_profiles": ["existing"],
        "profiles": {"existing": {"identity": "new"}},
    }), encoding="utf-8")
    monkeypatch.setattr(signature_profiles, "PROFILE_PATH", base)
    monkeypatch.setattr(signature_profiles, "PROFILE_EXTENSION_DIR", extensions)

    assert signature_profiles.load_signature_profiles(base)["existing"]["identity"] == "new"
