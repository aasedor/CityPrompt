"""Reusable physical-glazing profiles for generated LEGO buildings.

The profiles describe construction intent rather than renderer-specific shader
objects.  Blender consumes the optical values when exporting glTF; the profile
name is also exported as material metadata so City Prompt can preserve the
same classification when it switches between near and city-scale glazing LODs.
"""
from __future__ import annotations

from copy import deepcopy


GLASS_PROFILES: dict[str, dict[str, float | str]] = {
    "low_iron_clear": {
        "label": "Low-iron clear lobby glass",
        "tint": "#f1eee4",
        "roughness": 0.055,
        "transmission": 0.96,
        "ior": 1.52,
        "clearcoat": 0.32,
        "clearcoat_roughness": 0.045,
        "specular_ior_level": 0.50,
        "interior_depth_m": 0.72,
        "frame_depth_m": 0.12,
        "pane_recess_m": 0.065,
        "environment_intensity": 1.30,
        "interior_light_color": "#ffe1b5",
        "interior_light_strength": 0.58,
        "glass_emission_strength": 0.015,
        "baked_glass_emission": 0.05,
        "baked_glass_mix": 0.64,
    },
    "office_clear_occupied": {
        "label": "Ultra-clear occupied office glazing",
        "tint": "#f3f0e8",
        "roughness": 0.045,
        "transmission": 0.97,
        "ior": 1.52,
        "clearcoat": 0.38,
        "clearcoat_roughness": 0.038,
        "specular_ior_level": 0.52,
        "interior_depth_m": 0.88,
        "frame_depth_m": 0.24,
        "pane_recess_m": 0.14,
        "environment_intensity": 1.38,
        "interior_light_color": "#ffe0b0",
        "interior_light_strength": 0.68,
        "glass_emission_strength": 0.012,
        "baked_glass_emission": 0.075,
        "baked_glass_mix": 0.52,
        # Unmasked graph curtain walls need a bounded alpha contribution in
        # Eevee/glTF.  Fully opaque physical transmission mostly reflects the
        # world in these exterior views and hides the room cards, making clear
        # office glazing read as pale plastic.  Masked facade-sheet glass keeps
        # its binary alpha path and does not consume this value.
        "surface_alpha": 0.58,
    },
    "reflective_curtain_wall": {
        "label": "Neutral reflective curtain wall",
        "tint": "#d9e0dc",
        "roughness": 0.085,
        "transmission": 0.82,
        "ior": 1.50,
        "clearcoat": 0.42,
        "clearcoat_roughness": 0.075,
        "specular_ior_level": 0.58,
        "interior_depth_m": 0.82,
        "frame_depth_m": 0.15,
        "pane_recess_m": 0.09,
        "environment_intensity": 1.45,
        "interior_light_color": "#ffd9a6",
        "interior_light_strength": 0.55,
        "glass_emission_strength": 0.012,
        "baked_glass_emission": 0.02,
        "baked_glass_mix": 0.82,
    },
    "industrial_sash": {
        "label": "Industrial steel-sash glass",
        "tint": "#e7e1d6",
        "roughness": 0.10,
        "transmission": 0.86,
        "ior": 1.47,
        "clearcoat": 0.18,
        "clearcoat_roughness": 0.16,
        "specular_ior_level": 0.44,
        "interior_depth_m": 0.58,
        "frame_depth_m": 0.21,
        "pane_recess_m": 0.16,
        "environment_intensity": 1.18,
        "interior_light_color": "#ffd39a",
        "interior_light_strength": 0.78,
        "glass_emission_strength": 0.020,
        "baked_glass_emission": 0.09,
        "baked_glass_mix": 0.78,
    },
    "residential_low_e": {
        "label": "Residential low-e glazing",
        "tint": "#e9e4da",
        "roughness": 0.105,
        "transmission": 0.80,
        "ior": 1.49,
        "clearcoat": 0.28,
        "clearcoat_roughness": 0.11,
        "specular_ior_level": 0.48,
        "interior_depth_m": 0.62,
        "frame_depth_m": 0.13,
        "pane_recess_m": 0.085,
        "environment_intensity": 1.20,
        "interior_light_color": "#ffe0b8",
        "interior_light_strength": 0.52,
        "glass_emission_strength": 0.016,
        "baked_glass_emission": 0.09,
        "baked_glass_mix": 0.88,
    },
    "heritage_leaded_occupied": {
        "label": "Warm occupied heritage leaded glass",
        "tint": "#756c5b",
        "roughness": 0.13,
        "transmission": 0.62,
        "ior": 1.49,
        "clearcoat": 0.24,
        "clearcoat_roughness": 0.12,
        "specular_ior_level": 0.46,
        "interior_depth_m": 0.78,
        "frame_depth_m": 0.18,
        "pane_recess_m": 0.18,
        "environment_intensity": 1.12,
        "interior_light_color": "#ffc77d",
        "interior_light_strength": 0.66,
        "glass_emission_strength": 0.010,
        "baked_glass_emission": 0.075,
        "baked_glass_mix": 0.46,
    },
}

DEFAULT_GLASS_PROFILE = "low_iron_clear"


def glass_profile(name: str | None) -> dict[str, float | str]:
    """Return a defensive copy of a known profile, raising on misspellings."""
    key = name or DEFAULT_GLASS_PROFILE
    try:
        profile = deepcopy(GLASS_PROFILES[key])
    except KeyError as exc:
        raise ValueError(f"unknown glass profile {key!r}; choose one of {sorted(GLASS_PROFILES)}") from exc
    profile["id"] = key
    return profile


def glass_profile_for_grammar(grammar: dict) -> str:
    signature = grammar.get("architectural_signature") or {}
    return str(signature.get("glass_profile") or DEFAULT_GLASS_PROFILE)
