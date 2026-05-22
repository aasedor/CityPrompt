"""Prompt-only render test for any authored archetype against live Gemini.

Generalized from _render_test_equestrian.py. Isolates the variable we changed:
generates from the PROMPT ALONE (no reference image, no base map / mask) so the
output quality reflects the authored text only. The production pipeline also
sends archetype reference images + a map composite, which can only improve
fidelity over this.

Mirrors backend render: model gemini-3.1-flash-image-preview, responseModalities
[TEXT, IMAGE], 2K, thinkingBudget. Temp 1.0 per the Gemini-3 image tuning note.
Read-only w.r.t. the catalog; writes PNGs to artifacts/<id>-pilot/.

Usage:
  python scripts/_render_test_archetype.py <archetype_id> [variant_id ...]
  python scripts/_render_test_archetype.py            # defaults to equestrian_center

With no variant ids, auto-picks the two most size-contrasting variants
(smallest + largest by suggested area) to show the scale span.
"""
from __future__ import annotations

import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "frontend" / "src" / "data"
CATALOGS = [DATA_DIR / "openSpaceArchetypes.json", DATA_DIR / "buildingArchetypes.json"]
MODEL = "gemini-3.1-flash-image-preview"

# Prompt wrapper mirrors globe/useGlobeAIRender.ts buildPrompt() for a
# ground-level (non-building) zone.
PITCH = ("oblique aerial (~40deg camera elevation above ground; ~50deg from "
         "nadir) view, ground-level zones only on photorealistic 3D terrain.")
LIGHTING = ("Golden hour, low warm southwest sun creating strong directional "
            "light. Long crisp shadows with deep material contrast.")


def get_api_key() -> str:
    for env in (ROOT / ".env", ROOT / "backend" / ".env"):
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("GEMINI_API_KEY=") and not line.startswith("#"):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("GEMINI_API_KEY not found in .env")


def find_arch(arch_id: str):
    for path in CATALOGS:
        arr = json.loads(path.read_text(encoding="utf-8"))["archetypes"]
        for a in arr:
            if a.get("id") == arch_id:
                return a
    raise SystemExit(f"archetype id not found in any catalog: {arch_id}")


def variant_area(v: dict, arch: dict) -> float:
    for f in ("suggestedAreaSqm", "maxAreaSqm", "minAreaSqm"):
        if v.get(f) is not None:
            return float(v[f])
    return float(arch.get("suggestedAreaSqm") or 0)


def pick_contrasting(arch: dict) -> list[dict]:
    variants = arch.get("variants", []) or []
    if len(variants) <= 2:
        return variants
    ordered = sorted(variants, key=lambda v: variant_area(v, arch))
    return [ordered[0], ordered[-1]]


def build_prompt(arch: dict, variant: dict) -> str:
    # getZoneArchetypePrompt(): mapOverlay + " Style: " + variant.description
    rp = arch.get("renderPrompt", {}) or {}
    overlay = rp.get("mapOverlay") or arch.get("prompt", {}).get("subject", "")
    style = variant.get("description", "")
    negative = rp.get("negative", "")
    return (
        f"{PITCH}\n{LIGHTING}\n\n"
        f"ZONE (entire frame): {overlay} Style: {style}\n\n"
        f"Do not include: {negative}"
    )


def generate(api_key: str, prompt: str, out_path: Path) -> bool:
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODEL}:generateContent?key={api_key}")
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"],
            "temperature": 1.0,
            "imageConfig": {"imageSize": "2K"},
            "thinkingConfig": {"thinkingBudget": 8192},
        },
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"  HTTP {e.code}: {e.read().decode('utf-8')[:500]}")
        return False
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        return False

    cands = body.get("candidates", [])
    if not cands:
        print(f"  No candidates. Response: {json.dumps(body)[:400]}")
        return False
    for part in cands[0].get("content", {}).get("parts", []):
        inline = part.get("inlineData") or part.get("inline_data")
        if inline and inline.get("data"):
            out_path.write_bytes(base64.b64decode(inline["data"]))
            print(f"  saved {out_path.relative_to(ROOT)} "
                  f"({out_path.stat().st_size // 1024} KB)")
            return True
    print(f"  No image part. Text: {json.dumps(body)[:400]}")
    return False


def main() -> int:
    arch_id = sys.argv[1] if len(sys.argv) > 1 else "equestrian_center"
    arch = find_arch(arch_id)
    out = ROOT / "artifacts" / f"{arch_id}-pilot"
    out.mkdir(parents=True, exist_ok=True)

    if len(sys.argv) > 2:
        by_id = {v["id"]: v for v in arch["variants"]}
        chosen = [by_id[vid] for vid in sys.argv[2:]]
    else:
        chosen = pick_contrasting(arch)

    api_key = get_api_key()
    for v in chosen:
        area = variant_area(v, arch)
        print(f"\n=== {v['id']}: {v.get('label')} ({int(area)} m2) ===")
        prompt = build_prompt(arch, v)
        print(f"  prompt chars: {len(prompt)}")
        generate(api_key, prompt, out / f"{v['id']}_promptonly.png")
    print(f"\nDone. Outputs in {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
