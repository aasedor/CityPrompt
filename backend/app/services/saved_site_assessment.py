"""Assessment evidence is reusable only for the exact saved active boundary."""

from shapely.geometry import Polygon


def matching_assessment(metadata, boundary_id, site):
    saved = (metadata or {}).get("site_assessment")
    if not isinstance(saved, dict) or saved.get("boundary_id") != str(boundary_id) or site is None:
        return None
    try:
        original = Polygon(saved["coordinates"])
        if original.is_valid and site.equals(original) and isinstance(saved.get("assessment"), dict):
            return saved
    except (KeyError, TypeError, ValueError):
        pass
    return None
