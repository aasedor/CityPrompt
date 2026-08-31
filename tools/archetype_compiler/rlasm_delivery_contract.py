"""Validation and audit helpers for City Prompt RLASM delivery derivatives.

The accepted RLASM candidate remains immutable.  A delivery contract names the
exact source GLB, the evidence-only objects that may be omitted, and every
source-conditioned optical value that must survive the Blender -> glTF export.
No generic material repair is inferred from a material name.
"""
from __future__ import annotations

import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONTRACT_SCHEMA = "cityprompt.rlasm.delivery-contract@1"
DELIVERY_SCHEMA = "cityprompt.rlasm.delivery@1"


class RlasmDeliveryContractError(ValueError):
    """Raised when a delivery derivative cannot be proven source-specific."""


@dataclass(frozen=True)
class OpticalMaterialContract:
    name: str
    base_color: tuple[float, float, float, float]
    roughness: float
    metallic: float
    transmission: float
    ior: float
    source_role: str
    source_sha256: str


@dataclass(frozen=True)
class DeliveryContract:
    candidate: str
    delivery_version: str
    source_glb: Path
    source_sha256: str
    exclude_object_prefixes: tuple[str, ...]
    optical_materials: tuple[OpticalMaterialContract, ...]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _unit_interval(value: Any, label: str) -> float:
    number = float(value)
    if not 0.0 <= number <= 1.0:
        raise RlasmDeliveryContractError(f"{label} must be within [0, 1]")
    return number


def _sha256(value: Any, label: str) -> str:
    text = str(value or "").lower()
    if len(text) != 64 or any(char not in "0123456789abcdef" for char in text):
        raise RlasmDeliveryContractError(f"{label} must be a lowercase SHA-256")
    return text


def load_delivery_contract(path: Path) -> DeliveryContract:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != CONTRACT_SCHEMA:
        raise RlasmDeliveryContractError(f"schema must be {CONTRACT_SCHEMA}")

    candidate = str(payload.get("candidate") or "").strip()
    delivery_version = str(payload.get("delivery_version") or "").strip()
    if not candidate or not delivery_version:
        raise RlasmDeliveryContractError("candidate and delivery_version are required")

    source_glb = Path(str(payload.get("source_glb") or ""))
    if not source_glb.is_absolute():
        source_glb = (path.parent / source_glb).resolve()
    if not source_glb.is_file():
        raise RlasmDeliveryContractError(f"source_glb does not exist: {source_glb}")
    source_sha256 = _sha256(payload.get("source_sha256"), "source_sha256")
    actual_source_sha256 = sha256_file(source_glb)
    if actual_source_sha256 != source_sha256:
        raise RlasmDeliveryContractError(
            f"source_glb hash mismatch: expected {source_sha256}, got {actual_source_sha256}"
        )

    prefixes = tuple(str(item).strip() for item in payload.get("exclude_object_prefixes", []))
    if any(not prefix for prefix in prefixes) or len(prefixes) != len(set(prefixes)):
        raise RlasmDeliveryContractError(
            "exclude_object_prefixes must contain unique non-empty strings"
        )

    optical_materials: list[OpticalMaterialContract] = []
    for index, raw in enumerate(payload.get("optical_materials", [])):
        label = f"optical_materials[{index}]"
        name = str(raw.get("name") or "").strip()
        source_role = str(raw.get("source_role") or "").strip()
        if not name or not source_role:
            raise RlasmDeliveryContractError(f"{label} requires name and source_role")
        color = tuple(
            _unit_interval(value, f"{label}.base_color[{channel}]")
            for channel, value in enumerate(raw.get("base_color", []))
        )
        if len(color) != 4 or color[3] >= 1.0:
            raise RlasmDeliveryContractError(
                f"{label}.base_color must be RGBA with alpha below 1"
            )
        ior = float(raw.get("ior"))
        if not 1.0 <= ior <= 2.5:
            raise RlasmDeliveryContractError(f"{label}.ior must be within [1, 2.5]")
        optical_materials.append(
            OpticalMaterialContract(
                name=name,
                base_color=color,  # type: ignore[arg-type]
                roughness=_unit_interval(raw.get("roughness"), f"{label}.roughness"),
                metallic=_unit_interval(raw.get("metallic", 0.0), f"{label}.metallic"),
                transmission=_unit_interval(
                    raw.get("transmission"), f"{label}.transmission"
                ),
                ior=ior,
                source_role=source_role,
                source_sha256=_sha256(raw.get("source_sha256"), f"{label}.source_sha256"),
            )
        )

    if len({item.name for item in optical_materials}) != len(optical_materials):
        raise RlasmDeliveryContractError("optical material names must be unique")

    return DeliveryContract(
        candidate=candidate,
        delivery_version=delivery_version,
        source_glb=source_glb,
        source_sha256=source_sha256,
        exclude_object_prefixes=prefixes,
        optical_materials=tuple(optical_materials),
    )


def read_glb_json(path: Path) -> dict[str, Any]:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise RlasmDeliveryContractError(f"not a binary glTF file: {path}")
    version, total_length = struct.unpack_from("<II", data, 4)
    if version != 2 or total_length != len(data):
        raise RlasmDeliveryContractError(f"invalid GLB header: {path}")
    chunk_length, chunk_type = struct.unpack_from("<II", data, 12)
    if chunk_type != 0x4E4F534A:
        raise RlasmDeliveryContractError(f"GLB first chunk is not JSON: {path}")
    return json.loads(data[20 : 20 + chunk_length].decode("utf-8").rstrip(" \x00"))


def validate_delivery_glb(path: Path, contract: DeliveryContract) -> dict[str, Any]:
    document = read_glb_json(path)
    node_names = [str(node.get("name") or "") for node in document.get("nodes", [])]
    leaked = [
        name
        for name in node_names
        if any(name.startswith(prefix) for prefix in contract.exclude_object_prefixes)
    ]
    if leaked:
        raise RlasmDeliveryContractError(
            f"evidence-only objects remain in delivery GLB: {leaked[:5]}"
        )

    materials = {
        str(material.get("name") or ""): material
        for material in document.get("materials", [])
    }
    for optical in contract.optical_materials:
        material = materials.get(optical.name)
        if material is None:
            raise RlasmDeliveryContractError(
                f"required optical material is missing: {optical.name}"
            )
        pbr = material.get("pbrMetallicRoughness") or {}
        color = pbr.get("baseColorFactor") or [1, 1, 1, 1]
        metallic = float(pbr.get("metallicFactor", 1.0))
        roughness = float(pbr.get("roughnessFactor", 1.0))
        transmission = (material.get("extensions") or {}).get(
            "KHR_materials_transmission", {}
        ).get("transmissionFactor", 0.0)
        ior = (material.get("extensions") or {}).get("KHR_materials_ior", {}).get(
            "ior", 1.5
        )
        extras = material.get("extras") or {}
        if material.get("alphaMode") != "BLEND" or float(color[3]) >= 1.0:
            raise RlasmDeliveryContractError(
                f"{optical.name} did not export blended transparency"
            )
        if len(color) != 4 or any(
            abs(float(actual) - expected) > 0.0001
            for actual, expected in zip(color, optical.base_color)
        ):
            raise RlasmDeliveryContractError(
                f"{optical.name} base color changed during export: {color}"
            )
        if abs(metallic - optical.metallic) > 0.0001:
            raise RlasmDeliveryContractError(
                f"{optical.name} metallic value changed during export: {metallic}"
            )
        if abs(roughness - optical.roughness) > 0.0001:
            raise RlasmDeliveryContractError(
                f"{optical.name} roughness changed during export: {roughness}"
            )
        if abs(float(transmission) - optical.transmission) > 0.0001:
            raise RlasmDeliveryContractError(
                f"{optical.name} transmission changed during export: {transmission}"
            )
        if abs(float(ior) - optical.ior) > 0.01:
            raise RlasmDeliveryContractError(
                f"{optical.name} IOR changed during export: {ior}"
            )
        if (
            extras.get("rlasm_source_role") != optical.source_role
            or extras.get("rlasm_source_sha256") != optical.source_sha256
        ):
            raise RlasmDeliveryContractError(
                f"{optical.name} lost its source-specific optical provenance"
            )

    return {
        "schema": DELIVERY_SCHEMA,
        "candidate": contract.candidate,
        "delivery_version": contract.delivery_version,
        "source_glb": str(contract.source_glb),
        "source_sha256": contract.source_sha256,
        "delivery_glb": str(path.resolve()),
        "delivery_sha256": sha256_file(path),
        "removed_object_prefixes": list(contract.exclude_object_prefixes),
        "optical_materials": [
            {
                "name": item.name,
                "source_role": item.source_role,
                "source_sha256": item.source_sha256,
                "base_color": list(item.base_color),
                "roughness": item.roughness,
                "metallic": item.metallic,
                "transmission": item.transmission,
                "ior": item.ior,
            }
            for item in contract.optical_materials
        ],
        "node_count": len(document.get("nodes", [])),
        "material_count": len(document.get("materials", [])),
        "image_count": len(document.get("images", [])),
        "review_boundary": (
            "Runtime delivery derivative only; the accepted source candidate remains immutable."
        ),
    }
