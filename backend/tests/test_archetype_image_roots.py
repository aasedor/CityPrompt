import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_ROOT = REPO_ROOT / "frontend" / "public" / "archetypes"

DOMAIN_CONTRACTS = {
    "buildingArchetypes.json": ("buildings", "/archetypes/buildings/"),
    "openSpaceArchetypes.json": ("openspaces", "/archetypes/openspaces/"),
    "streetPathArchetypes.json": ("streets", "/archetypes/streets/"),
}


def _thumbnail_urls(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "thumbnailUrl" and isinstance(child, str):
                yield child
            yield from _thumbnail_urls(child)
    elif isinstance(value, list):
        for child in value:
            yield from _thumbnail_urls(child)


def test_catalogue_thumbnail_urls_use_authoritative_roots():
    data_root = REPO_ROOT / "frontend" / "src" / "data"

    for filename, (directory, web_prefix) in DOMAIN_CONTRACTS.items():
        assert (PUBLIC_ROOT / directory).is_dir()
        catalogue = json.loads((data_root / filename).read_text(encoding="utf-8"))
        urls = list(_thumbnail_urls(catalogue))
        assert urls, f"{filename} should contain thumbnail URLs"
        assert all(url.startswith(web_prefix) for url in urls)


def test_openai_generator_writes_only_to_authoritative_roots():
    source = (
        REPO_ROOT / "scripts" / "render-community-archetype-images-openai.mjs"
    ).read_text(encoding="utf-8")

    for directory, web_prefix in DOMAIN_CONTRACTS.values():
        assert f"path.join(publicRoot, '{directory}')" in source
        assert f"webPrefix: '{web_prefix.rstrip('/')}'" in source

    for legacy_root in (
        "path.join(publicRoot, 'parks-plazas')",
        "path.join(publicRoot, 'streets-pathways')",
        "webPrefix: '/archetypes/parks-plazas'",
        "webPrefix: '/archetypes/streets-pathways'",
    ):
        assert legacy_root not in source
