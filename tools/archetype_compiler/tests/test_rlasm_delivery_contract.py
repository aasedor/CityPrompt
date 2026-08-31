from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import pytest

from rlasm_delivery_contract import (
    CONTRACT_SCHEMA,
    RlasmDeliveryContractError,
    load_delivery_contract,
    validate_delivery_glb,
)


def _write_glb(path: Path, document: dict) -> None:
    payload = json.dumps(document, separators=(",", ":")).encode("utf-8")
    payload += b" " * ((-len(payload)) % 4)
    total = 12 + 8 + len(payload)
    path.write_bytes(
        b"glTF"
        + struct.pack("<II", 2, total)
        + struct.pack("<II", len(payload), 0x4E4F534A)
        + payload
    )


def _contract_payload(source: Path, source_hash: str) -> dict:
    return {
        "schema": CONTRACT_SCHEMA,
        "candidate": "source-keeper-v004",
        "delivery_version": "cityprompt-v002",
        "source_glb": str(source),
        "source_sha256": source_hash,
        "exclude_object_prefixes": ["source_meadow_", "source_tree_"],
        "optical_materials": [
            {
                "name": "SRC_V0_CLEAR_PLATE_GLASS",
                "source_role": "locked plate-glass optical field",
                "source_sha256": "a" * 64,
                "base_color": [0.96, 0.95, 0.93, 0.22],
                "roughness": 0.018,
                "metallic": 0.0,
                "transmission": 0.86,
                "ior": 1.46,
            }
        ],
    }


def test_contract_fails_closed_on_source_hash_mismatch(tmp_path: Path) -> None:
    source = tmp_path / "source.glb"
    _write_glb(source, {"asset": {"version": "2.0"}})
    payload = _contract_payload(source, "0" * 64)
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(RlasmDeliveryContractError, match="hash mismatch"):
        load_delivery_contract(contract_path)


def test_delivery_requires_source_specific_optical_export_and_no_context(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.glb"
    _write_glb(source, {"asset": {"version": "2.0"}})
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    payload = _contract_payload(source, source_hash)
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(payload), encoding="utf-8")
    contract = load_delivery_contract(contract_path)

    delivery = tmp_path / "delivery.glb"
    _write_glb(
        delivery,
        {
            "asset": {"version": "2.0"},
            "nodes": [{"name": "architecture"}],
            "materials": [
                {
                    "name": "SRC_V0_CLEAR_PLATE_GLASS",
                    "alphaMode": "BLEND",
                    "pbrMetallicRoughness": {
                        "baseColorFactor": [0.96, 0.95, 0.93, 0.22],
                        "metallicFactor": 0.0,
                        "roughnessFactor": 0.018,
                    },
                    "extensions": {
                        "KHR_materials_transmission": {"transmissionFactor": 0.86},
                        "KHR_materials_ior": {"ior": 1.46},
                    },
                    "extras": {
                        "rlasm_source_role": "locked plate-glass optical field",
                        "rlasm_source_sha256": "a" * 64,
                    },
                }
            ],
        },
    )

    proof = validate_delivery_glb(delivery, contract)

    assert proof["delivery_version"] == "cityprompt-v002"
    assert proof["optical_materials"][0]["source_sha256"] == "a" * 64
    assert proof["node_count"] == 1


def test_delivery_rejects_generic_transparent_material_substitution(
    tmp_path: Path,
) -> None:
    source = tmp_path / "source.glb"
    _write_glb(source, {"asset": {"version": "2.0"}})
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    payload = _contract_payload(source, source_hash)
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(payload), encoding="utf-8")
    contract = load_delivery_contract(contract_path)
    delivery = tmp_path / "delivery.glb"
    _write_glb(
        delivery,
        {
            "asset": {"version": "2.0"},
            "nodes": [{"name": "architecture"}],
            "materials": [{
                "name": "SRC_V0_CLEAR_PLATE_GLASS",
                "alphaMode": "BLEND",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [0.96, 0.95, 0.93, 0.22],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.018,
                },
                "extensions": {
                    "KHR_materials_transmission": {"transmissionFactor": 0.5},
                    "KHR_materials_ior": {"ior": 1.46},
                },
                "extras": {
                    "rlasm_source_role": "locked plate-glass optical field",
                    "rlasm_source_sha256": "a" * 64,
                },
            }],
        },
    )

    with pytest.raises(RlasmDeliveryContractError, match="transmission changed"):
        validate_delivery_glb(delivery, contract)


def test_delivery_rejects_opaque_glass_and_leaked_context(tmp_path: Path) -> None:
    source = tmp_path / "source.glb"
    _write_glb(source, {"asset": {"version": "2.0"}})
    source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    payload = _contract_payload(source, source_hash)
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(payload), encoding="utf-8")
    contract = load_delivery_contract(contract_path)
    delivery = tmp_path / "delivery.glb"
    _write_glb(
        delivery,
        {
            "asset": {"version": "2.0"},
            "nodes": [{"name": "source_meadow_grade"}],
            "materials": [{"name": "SRC_V0_CLEAR_PLATE_GLASS"}],
        },
    )

    with pytest.raises(RlasmDeliveryContractError, match="evidence-only objects"):
        validate_delivery_glb(delivery, contract)
