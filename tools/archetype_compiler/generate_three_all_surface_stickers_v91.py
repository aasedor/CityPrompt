"""Generate bounded, multi-reference exterior stickers for the V91 pilots."""
from __future__ import annotations

import argparse
import base64
import hashlib
import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from PIL import Image

from generate_facade_sheets import OPENAI_IMAGES_EDIT_URL, OPENAI_MODEL_ID, load_openai_api_key


REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "artifacts/three-all-surface-stickers-v91/surface-stickers"
MAX_ATTEMPTS = 2

RESEARCH = {
    "med_villa_tuscan": [
        "https://raccoltanormativa.consiglio.regione.toscana.it/articolo?anc=art50&dl_a=y&dl_id=&dl_t=text%2Fxml&dl_id=&dl_t=text%2Fxml",
    ],
    "deco_theater_egyptian_revival": [
        "https://npgallery.nps.gov/GetAsset/92b9d2a5-3df1-48e2-ab48-b66d5d1282ed",
        "https://planning.lacity.gov/plndoc/Staff_Reports/2023/05-04-2023/Item_04_Report_of_Sign_Addition_at_Netflix_Egyptian_Theatre.pdf",
    ],
    "grand-magasin-belle-epoque": [
        "https://haussmann.galerieslafayette.com/en/the-galeries-lafayette-dome",
        "https://www.groupegalerieslafayette.com/latest-news/galeries-lafayette-group-completes-the-restoration-of-its-haussmann-flagships-iconic-dome",
    ],
}


def face(name: str, size: str, instruction: str) -> dict[str, str]:
    return {"name": name, "size": size, "instruction": instruction}


TARGETS: dict[str, dict[str, Any]] = {
    "med_villa_tuscan": {
        "title": "Tuscan Farmhouse Villa",
        "reference_dir": "frontend/public/archetypes/buildings/mediterranean_villa_estate",
        "index": 0,
        "identity": (
            "three-storey ochre Tuscan farmhouse, rough pale-stone quoins, exactly three deep round loggia arches, "
            "dark green timber shutters, restrained rear service openings and one broad weathered terracotta hip roof"
        ),
        "faces": [
            face("front", "1536x1024", "exact public frontage with three loggia arches and aligned shuttered windows"),
            face("left", "1024x1024", "left end elevation visible in the oblique reference; sparse shuttered domestic openings and stone corner returns"),
            face("right", "1024x1024", "right end elevation of the same house; related but not mirrored domestic window rhythm and continuous stone base"),
            face("rear", "1536x1024", "quiet rear garden elevation with service door and restrained shuttered openings; no ceremonial loggia"),
            face("roof", "1536x1024", "strict top-down roof plan showing one complete rectangular terracotta hip roof, ridge, hips, eaves and subtle weathering"),
        ],
    },
    "deco_theater_egyptian_revival": {
        "title": "Egyptian Revival Theater",
        "reference_dir": "frontend/public/archetypes/buildings/deco_theater_mainstreet",
        "index": 2,
        "identity": (
            "1920s Egyptian Revival movie palace with warm sand pylon facade, battered upper wall, winged-sun relief, "
            "turquoise lotus capitals and cornices, deep triple-door vestibule, marquee, long auditorium side walls and stepped stage house"
        ),
        "faces": [
            face("front", "1536x1024", "exact public pylon facade with four aligned lotus columns, tall upper glazing and three recessed entrance portals"),
            face("left", "1536x1024", "complete long left auditorium elevation from front pylon return to rear stage house; sparse exit doors, vents and Egyptian cornice datums"),
            face("right", "1536x1024", "complete long right auditorium elevation with a distinct but construction-consistent exit/service rhythm; no repeated marquee"),
            face("rear", "1536x1024", "plain but occupied rear stage-house elevation with loading doors, service windows, vents and continued sand/turquoise material bands"),
            face("roof", "1536x1024", "strict top-down stepped flat-roof plan with front roof, main auditorium membrane and raised rear stage-house roof; parapets and bounded equipment"),
        ],
    },
    "grand-magasin-belle-epoque": {
        "title": "Belle Epoque Grand Magasin",
        "reference_dir": "frontend/public/archetypes/buildings/grand-magasin",
        "index": 0,
        "identity": (
            "Belle Epoque Paris department store with pale limestone piers, dark iron-and-glass display bays, gilded open rails, "
            "eight occupied corner-block elevations, a central stained-glass court dome, smaller corner cupola and four zinc mansard wings"
        ),
        "faces": [
            face("front", "1536x1024", "main long shopping frontage with aligned iron-and-glass bays, limestone piers and entrance canopy"),
            face("front_right", "1024x1536", "narrow front-right chamfer elevation, vertically continuous and registered to adjacent floor/cornice datums"),
            face("right", "1536x1024", "right street elevation with the same five storeys, display-bay construction and a secondary entrance rhythm"),
            face("rear_right", "1024x1536", "narrow rear-right chamfer with occupied glazing and continuous gilded cornice datums"),
            face("rear", "1536x1024", "complete rear/service street elevation, still architecturally finished, with delivery portals and reduced but aligned glazing"),
            face("rear_left", "1024x1536", "narrow rear-left chamfer with continuous limestone/iron construction and no blank wall"),
            face("left", "1536x1024", "left street elevation matching the exact oblique evidence, with five storeys of iron glazing and limestone piers"),
            face("front_left", "1024x1536", "principal corner entrance chamfer beneath the smaller dome; vertically aligned curved-display-bay language without perspective"),
            face("roof", "1536x1024", "strict top-down complete roof plan: four standing-seam zinc mansard wings around an interior court, large central stained-glass dome, smaller corner cupola, dormers and chimneys"),
        ],
    },
}


def refs(spec: dict[str, Any]) -> list[Path]:
    root = REPO / spec["reference_dir"]
    index = int(spec["index"])
    return [root / f"variant_{index}.png", root / f"variant_{index}_angle_60.jpg", root / f"variant_{index}_angle_90.jpg"]


def prompt(spec: dict[str, Any], surface: dict[str, str]) -> str:
    name = surface["name"]
    if name == "roof":
        capture = (
            "Produce one rectified orthographic TOP-DOWN ROOF STICKER for a professional Blender model. "
            "The roof footprint must fill the image with no street, sky, neighbouring buildings, trees, people, labels or border. "
            "Preserve plan proportions, ridge axes, roof breaks, domes, cupolas, dormers and equipment from the three references. "
            "Use flat overcast material capture lighting; remove directional cast shadows while retaining material relief."
        )
    else:
        capture = (
            f"Produce one rectified orthographic {name.replace('_', '-').upper()} ELEVATION STICKER for a professional Blender model. "
            "Show the entire wall from ground datum to eave, edge-to-edge, with no perspective, sky, pavement, neighbouring buildings, "
            "trees, people, cars, labels, border or isolated object. Use flat overcast capture lighting with no directional cast shadows. "
            "Keep every floor and cornice datum level. Do not copy the ceremonial front entrance onto a secondary elevation."
        )
    return (
        f"{capture}\n\nBuilding identity: {spec['identity']}.\n"
        f"Surface-specific construction: {surface['instruction']}.\n\n"
        "The first image is the exact street identity, the second is the exact oblique massing view, and the third is the exact roof plan. "
        "Treat them as one building. Infer only hidden construction; never change the counted storeys, primary silhouette, material zones or opening hierarchy. "
        "Every visible field must be occupied architectural construction—no blank white, grey or mono-coloured placeholder surfaces. "
        "Generate a texture/elevation asset, not a beauty rendering."
    )


def png_bytes(path: Path) -> bytes:
    with Image.open(path) as image:
        buffer = io.BytesIO()
        image.convert("RGB").save(buffer, format="PNG", optimize=True)
        return buffer.getvalue()


def generate(api_key: str, model: str, prompt_text: str, references: list[Path], size: str) -> Image.Image:
    response = requests.post(
        OPENAI_IMAGES_EDIT_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        data={"model": model, "prompt": prompt_text, "n": "1", "size": size, "quality": "high", "output_format": "png"},
        files=[("image[]", (path.name, png_bytes(path), "image/png")) for path in references],
        timeout=360,
    )
    if response.status_code != 200:
        detail = response.text[:700].replace(api_key, "[redacted]")
        raise RuntimeError(f"OpenAI image edit returned {response.status_code}: {detail}")
    data = response.json().get("data") or []
    encoded = data[0].get("b64_json") if data else None
    if not encoded:
        raise RuntimeError("OpenAI image edit returned no b64_json image")
    return Image.open(io.BytesIO(base64.b64decode(encoded))).convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--model", default=OPENAI_MODEL_ID)
    parser.add_argument("--only", choices=("all", *TARGETS), default="all")
    args = parser.parse_args()
    selected = TARGETS.items() if args.only == "all" else [(args.only, TARGETS[args.only])]
    api_key = None if args.dry_run else load_openai_api_key(None)
    calls = 0
    failures: list[str] = []
    for variant, spec in selected:
        target_out = OUT / variant
        target_out.mkdir(parents=True, exist_ok=True)
        reference_paths = refs(spec)
        missing = [str(path) for path in reference_paths if not path.exists()]
        if missing:
            raise SystemExit(f"missing exact references for {variant}: {missing}")
        surfaces = []
        for surface in spec["faces"]:
            output = target_out / f"{surface['name']}.png"
            prompt_text = prompt(spec, surface)
            item = {
                "surface": surface["name"], "output": output.name, "size": surface["size"],
                "prompt_sha256": hashlib.sha256(prompt_text.encode("utf-8")).hexdigest(),
                "prompt": prompt_text, "status": "planned" if args.dry_run else "pending",
            }
            if not args.dry_run and output.exists() and not args.force:
                item["status"] = "cached"
            elif not args.dry_run:
                last_error: Exception | None = None
                for attempt in range(MAX_ATTEMPTS):
                    try:
                        image = generate(str(api_key), args.model, prompt_text, reference_paths, surface["size"])
                        image.save(output, format="PNG", optimize=True)
                        if not output.exists() or output.stat().st_size < 50_000:
                            raise RuntimeError("generated image is missing or unexpectedly small")
                        calls += 1
                        item.update({"status": "generated", "attempt": attempt + 1, "px": list(image.size)})
                        break
                    except Exception as exc:
                        last_error = exc
                        if attempt + 1 < MAX_ATTEMPTS:
                            time.sleep(1.0)
                else:
                    item.update({"status": "failed", "error": str(last_error)})
                    failures.append(f"{variant}:{surface['name']}")
            surfaces.append(item)
        manifest = {
            "schema": "all-surface-sticker-source@1", "variant_id": variant,
            "title": spec["title"], "provider": "openai", "model": args.model,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "reference_images": [str(path.relative_to(REPO)).replace("\\", "/") for path in reference_paths],
            "research_sources": RESEARCH[variant], "api_calls_this_run": calls,
            "max_attempts_per_output": MAX_ATTEMPTS, "surfaces": surfaces,
        }
        (target_out / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"[v91-stickers] {variant}: {len(surfaces)} surfaces", flush=True)
    print(f"[v91-stickers] paid calls this run={calls}; failures={len(failures)}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
