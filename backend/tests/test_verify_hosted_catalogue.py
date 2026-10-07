"""Hosted verification must cover every selection without writing or leaking secrets."""

import hashlib
import io
import json
from pathlib import Path
import struct
from unittest.mock import AsyncMock

from botocore.exceptions import ClientError
import pytest

from scripts import verify_hosted_catalogue as verify


GLB = struct.pack("<4sII", b"glTF", 2, 20) + struct.pack("<I4s", 0, b"JSON")
DIGEST = hashlib.sha256(GLB).hexdigest()


def expected(variant="house"):
    return {"asset_id": f"pick-{variant}", "variant_id": variant, "candidate": f"{variant}-v1",
            "sha256": DIGEST, "bytes": len(GLB), "dimensions_m": [10, 12, 6],
            "local_trial_only": False}


def binding(variant="house"):
    return {"id": "test-id", "name": "Test", "is_public": True,
            "model_url": f"/api/v1/files/library/{variant}.glb", "metadata": {
                "rlasm": {"candidate": f"{variant}-v1", "variant_id": variant, "model_sha256": DIGEST,
                          "delivery_format": "architectural_clay", "method_version": "6.1",
                          "runtime_enabled": True, "continuous_resize_allowed": False},
                "lego": {"enabled": True, "family": "test-family", "role": "assembled",
                         "repeatable_z": False, "native_floors": 2, "min_floors": 2, "max_floors": 2,
                         "source_variant_id": variant, "generation_archetype_id": variant,
                         "width_m": 10, "depth_m": 12, "height_m": 6}}}


def failure(code="AccessDenied"):
    return ClientError({"Error": {"Code": code, "Message": "secret-storage-credential"}}, "GetObject")


class Storage:
    """Read-only external boundary; writes are intentionally unavailable."""
    def __init__(self, values=None, denied=False):
        self.values = values or {}
        self.denied = denied
        self.bodies = []

    def get_object(self, *, Bucket, Key):
        assert Bucket == "private-test"
        if self.denied:
            raise failure()
        value = self.values.get(Key, GLB)
        if isinstance(value, Exception):
            raise value
        body = io.BytesIO(value)
        self.bodies.append(body)
        return {"Body": body}


def test_shipped_contract_covers_all_49_library_choices_not_native_fixtures():
    root = Path(__file__).parents[2]
    rows = verify.load_expected(root / "backend/app/data/native_model_contract.json",
                                root / "seed/model-library/rlasm-architectural-clay/library.json")
    assert len(rows) == 49
    assert len({row["asset_id"] for row in rows}) == 49
    assert {"infill_duplex", "vancouverism_classic", "montreal_depanneur_modern"} <= {row["variant_id"] for row in rows}
    assert "validation_timber_sanctuary_church_glazed_gable" not in {row["asset_id"] for row in rows}


def test_unknown_current_candidate_fails_instead_of_silently_shrinking_scope(tmp_path):
    contract, library = tmp_path / "contract.json", tmp_path / "library.json"
    contract.write_text(json.dumps({"schema": "cityprompt.native-model-contract@1", "records": [
        {"asset_id": "missing", "variant_id": "house", "revision": "unknown-v1", "current": True}]}))
    library.write_text(json.dumps({"schema": "cityprompt.rlasm-architectural-clay-library@1", "entries": []}))
    with pytest.raises(ValueError, match="candidate"):
        verify.load_expected(contract, library)


def test_exact_runtime_binding_private_bytes_and_hash_are_verified():
    private = Storage()
    rows = verify.verify_catalogue([expected()], [binding()], "private-test", private, Storage(denied=True))
    assert rows[0]["status"] == "verified"
    assert rows[0]["sha256"] == DIGEST
    assert rows[0]["bytes"] == 20
    assert rows[0]["private_storage"] == "verified"
    assert all(body.closed for body in private.bodies)


def test_missing_stale_and_storage_failures_are_all_collected_and_redacted():
    variants = ["missing", "stale", "storage", "corrupt", "private-row"]
    bindings = [binding(v) for v in variants[1:]]
    bindings[0]["metadata"]["rlasm"]["model_sha256"] = "0" * 64
    bindings[-1]["is_public"] = False
    storage = Storage({"library/storage.glb": failure("NoSuchKey"), "library/corrupt.glb": b"bad bytes"})
    rows = verify.verify_catalogue([expected(v) for v in variants], bindings, "private-test", storage, Storage(denied=True))
    assert len(rows) == 5
    assert [row["issues"] for row in rows] == [["missing_binding"], ["stale_binding"],
                                              ["missing_object"], ["size_mismatch"], ["binding_not_public"]]
    assert "secret-storage-credential" not in json.dumps(rows)


@pytest.mark.parametrize("url", ["https://example.invalid/library/house.glb?token=secret", "/api/v1/files/../secret", "/api/v1/files/library/house.glb?token=secret", "https://[invalid"])
def test_external_or_unsafe_binding_urls_cannot_pass(url):
    row = binding()
    row["model_url"] = url
    result = verify.verify_catalogue([expected()], [row], "private-test", Storage(), Storage(denied=True))[0]
    assert result["issues"] == ["unsafe_model_url"]
    assert "token=secret" not in json.dumps(result)


def test_public_object_and_runtime_metadata_mismatch_do_not_pass():
    row = binding("wrong-runtime")
    row["metadata"]["lego"]["source_variant_id"] = "different"
    rows = verify.verify_catalogue([expected("public"), expected("wrong-runtime")],
                                  [binding("public"), row], "private-test", Storage(), Storage())
    assert rows[0]["issues"] == ["object_publicly_readable"]
    assert rows[1]["issues"] == ["invalid_runtime_binding"]


def test_same_candidate_bad_alias_cannot_be_hidden_by_a_good_alias():
    bad = binding()
    bad["metadata"]["rlasm"]["model_sha256"] = "0" * 64
    rows = verify.verify_catalogue([expected()], [binding(), bad], "private-test", Storage(), Storage(denied=True))
    assert rows[0]["issues"] == ["stale_binding"]


def test_private_user_copy_cannot_block_valid_shared_binding():
    private_copy = binding()
    private_copy["is_public"] = False
    private_copy["metadata"]["rlasm"]["model_sha256"] = "0" * 64
    row = verify.verify_catalogue([expected()], [binding(), private_copy], "private-test",
                                  Storage(), Storage(denied=True))[0]
    assert row["status"] == "verified"


def test_optional_module_cannot_block_or_replace_base_assembly():
    module = binding()
    module["metadata"]["rlasm"]["delivery_format"] = "architectural_clay_module_v1"
    module["metadata"]["rlasm"]["model_sha256"] = "0" * 64
    module["metadata"]["lego"]["role"] = "floor"
    good = verify.verify_catalogue([expected()], [binding(), module], "private-test",
                                   Storage(), Storage(denied=True))[0]
    assert good["status"] == "verified"
    missing = verify.verify_catalogue([expected()], [module], "private-test",
                                      Storage(), Storage(denied=True))[0]
    assert missing["issues"] == ["missing_assembly_binding"]


def test_all_public_complete_assembly_aliases_must_pass():
    alias = {**binding(), "model_url": "/api/v1/files/library/alias.glb"}
    row = verify.verify_catalogue([expected()], [binding(), alias], "private-test",
                                  Storage(), Storage(denied=True))[0]
    assert row["status"] == "verified"
    assert row["private_storage"] == "verified"


def test_trial_only_flag_is_preserved_as_a_release_blocker():
    trial = {**expected(), "local_trial_only": True}
    row = verify.verify_catalogue([trial], [binding()], "private-test", Storage(), Storage(denied=True))[0]
    assert row["status"] == "failed"
    assert row["issues"] == ["local_trial_only"]


@pytest.mark.parametrize("body,issue", [(b"x" * 20, "invalid_glb"),
                                      (GLB[:-1] + b"x", "hash_mismatch"),
                                      (RuntimeError("secret-provider-url"), "storage_unavailable")])
def test_storage_corruption_and_transport_failures_are_sanitized(body, issue):
    row = verify.verify_catalogue([expected()], [binding()], "private-test",
                                  Storage({"library/house.glb": body}), Storage(denied=True))[0]
    assert row["issues"] == [issue]
    assert "secret-provider-url" not in json.dumps(row)


def test_failed_anonymous_probe_cannot_claim_private_storage():
    row = verify.verify_catalogue([expected()], [binding()], "private-test", Storage(),
                                  Storage({"library/house.glb": failure("InternalError")}))[0]
    assert row["issues"] == ["privacy_unverified"]
    assert row["private_storage"] == "unverified"


def test_private_alias_does_not_hide_public_alias_for_the_same_candidate():
    public_alias = {**binding(), "model_url": "/api/v1/files/library/public-house.glb"}
    row = verify.verify_catalogue([expected()], [binding(), public_alias], "private-test", Storage(),
                                  Storage({"library/house.glb": failure()}))[0]
    assert row["issues"] == ["object_publicly_readable"]
    assert row["private_storage"] == "unverified"


@pytest.mark.asyncio
async def test_database_fetch_uses_read_only_transaction(monkeypatch):
    db = AsyncMock()
    transaction = AsyncMock()
    def begin(**kwargs):
        assert kwargs == {"readonly": True}
        return transaction
    db.transaction = begin
    db.fetch.return_value = [binding()]
    monkeypatch.setattr(verify, "connect_database", AsyncMock(return_value=db))
    assert (await verify.read_bindings("never-printed-secret"))[0]["is_public"] is True
    db.close.assert_awaited_once()


def test_target_requires_explicit_environment_and_never_echoes_errors(monkeypatch, capsys):
    for name in verify.REQUIRED_ENV:
        monkeypatch.delenv(name, raising=False)
    assert verify.main(["--verify-target"]) == 2
    output = capsys.readouterr().out
    assert "target_configuration_missing" in output
    assert "Traceback" not in output
