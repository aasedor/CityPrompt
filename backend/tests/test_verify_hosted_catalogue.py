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


def test_shipped_contract_covers_current_release_including_five_trial_buildings():
    root = Path(__file__).parents[2]
    rows = verify.load_expected(root / "backend/app/data/native_model_contract.json",
                                root / "seed/model-library/rlasm-architectural-clay/library.json",
                                [root / "seed/claude-five-trial/library.json"])
    assert len(rows) == 59
    assert sum(row["local_trial_only"] for row in rows) == 0
    assert len({row["asset_id"] for row in rows}) == 59
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

def module_fixture():
    path=Path(__file__).parents[2] / 'seed/model-library/rlasm-architectural-clay/vancouverism-classic-storey-program-v001.json'
    wanted=verify.load_storey_modules(path)[1]
    wanted.update(sha256=DIGEST,bytes=len(GLB),dimensions_m=[10,12,6])
    row=binding(wanted['variant_id'])
    row['metadata']['rlasm'].update(candidate=wanted['candidate'],delivery_format='architectural_clay_module_v1',
        storey_program_id=wanted['storey_program_id'],source_model_sha256=json.loads(path.read_text())['source']['sha256'])
    row['metadata']['lego'].update(role='floor',repeatable_z=True,min_floors=16,max_floors=40,
        occupied_storeys=1,family='vancouver-balcony-podium-tower',allow_inset_footprint=True,
        placement_contract={'mode':'authored_storey_program','continuous_resize_allowed':False,
                            'storey_program_id':wanted['storey_program_id']})
    return wanted,row


def test_required_authored_floor_is_verified_as_a_module_not_a_complete_building():
    wanted,row=module_fixture()
    report=verify.verify_catalogue([wanted],[row],'private-test',Storage(),Storage(denied=True))
    assert report[0]['status']=='verified'


@pytest.mark.parametrize('section,key,value',[
    ('lego','repeatable_z',False),('lego','min_floors',17),('lego','max_floors',16),
    ('lego','occupied_storeys',2),('lego','family','other-family'),
    ('lego','generation_archetype_id','other-variant'),('lego','allow_inset_footprint',False),
    ('lego','placement_contract',{'mode':'stretch'}),('rlasm','source_model_sha256','0'*64),
])
def test_module_audit_rejects_bytes_with_unusable_or_conflicting_programme_metadata(section,key,value):
    wanted,row=module_fixture()
    row['metadata'][section][key]=value
    report=verify.verify_catalogue([wanted],[row],'private-test',Storage(),Storage(denied=True))[0]
    assert report['status']=='failed'
    assert 'invalid_runtime_binding' in report['issues']

def test_required_authored_module_cannot_be_satisfied_by_only_its_native_assembly():
    wanted={**expected(), 'role':'floor','storey_program_id':'reviewed-program'}
    report=verify.verify_catalogue([wanted],[binding()],'private-test',Storage(),Storage(denied=True))
    assert report[0]['status']=='failed'


@pytest.mark.parametrize("message,http,passed", [
    ("Authorization", 400, True),
    ("Invalid range", 400, False),
    ("Authorization", 500, False),
])
def test_r2_unsigned_authorization_rejection_is_narrowly_recognized(message, http, passed):
    denied = ClientError({"Error": {"Code": "InvalidArgument", "Message": message},
                          "ResponseMetadata": {"HTTPStatusCode": http}}, "GetObject")
    result = verify.verify_catalogue([expected()], [binding()], "private-test", Storage(),
                                    Storage({"library/house.glb": denied}))[0]
    assert (result["status"] == "verified") is passed
    if not passed:
        assert result["issues"] == ["privacy_unverified"]


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
    assert "lod_urls" in db.fetch.call_args.args[0]
    db.close.assert_awaited_once()


def test_target_requires_explicit_environment_and_never_echoes_errors(monkeypatch, capsys):
    for name in verify.REQUIRED_ENV:
        monkeypatch.delenv(name, raising=False)
    assert verify.main(["--verify-target"]) == 2
    output = capsys.readouterr().out
    assert "target_configuration_missing" in output
    assert "Traceback" not in output


@pytest.mark.parametrize("lod", [None, {}, {"0": ""}, {"0": None}])
def test_absent_or_empty_lod_retains_the_renderer_model_url_fallback(lod):
    row = {**binding(), "lod_urls": lod}
    result = verify.verify_catalogue([expected()], [row], "private-test", Storage(), Storage(denied=True))[0]
    assert result["status"] == "verified"


@pytest.mark.parametrize("level", ["0", "1", "2", "3"])
def test_every_renderable_lod_must_resolve_to_verified_private_source_bytes(level):
    row = {**binding(), "lod_urls": json.dumps({level: "/api/v1/files/library/alternate.glb"})}
    good = verify.verify_catalogue([expected()], [row], "private-test", Storage(), Storage(denied=True))[0]
    assert good["status"] == "verified"
    bad = verify.verify_catalogue([expected()], [row], "private-test",
                                  Storage({"library/alternate.glb": GLB[:-1] + b"x"}), Storage(denied=True))[0]
    assert bad["issues"] == ["hash_mismatch"]
    assert bad["private_storage"] == "unverified"


@pytest.mark.parametrize("lod", [{"0": "https://example.invalid/model.glb?secret=private"},
                                 {"1": 42}, ["/api/v1/files/library/house.glb"], "not-json"])
def test_unsafe_or_malformed_lod_is_reported_without_leaking_url(lod):
    result = verify.verify_catalogue([expected()], [{**binding(), "lod_urls": lod}],
                                     "private-test", Storage(), Storage(denied=True))[0]
    assert result["issues"] == ["unsafe_lod_url"]
    assert "secret=private" not in json.dumps(result)


def test_public_alternate_lod_cannot_hide_behind_private_base_model():
    row = {**binding(), "lod_urls": {"0": "/api/v1/files/library/public-alternate.glb"}}
    result = verify.verify_catalogue([expected()], [row], "private-test", Storage(),
                                     Storage({"library/house.glb": failure()}))[0]
    assert result["issues"] == ["object_publicly_readable"]
    assert result["private_storage"] == "unverified"
