"""Small, trusted ComfyUI workflows. No paid nodes or client-supplied graphs.

Based on Comfy-Org/workflow_templates: image_flux2_klein_image_edit_4b_distilled
and video_wan2_2_5B_ti2v. Qwen uses the installed native Image 2.1 encoder.
"""

from __future__ import annotations

from dataclasses import dataclass
import io
from urllib.parse import urlsplit

import httpx
from PIL import Image


@dataclass(frozen=True)
class Preset:
    id: str
    label: str
    kind: str
    diffusion: str
    encoder: str
    vae: str
    max_edge: int
    steps: int
    prompt: str


IMAGE_PROMPT = "Refine this architectural view into a realistic architectural photograph. Preserve the camera, buildings, streets and planting. Natural materials, soft daylight and restrained colour."
VIDEO_PROMPT = "Very slow smooth camera push-in. Buildings remain rigid. Existing people walk naturally and foliage moves gently. Preserve the lighting. One continuous shot."
PRESETS = {
    p.id: p
    for p in (
        Preset(
            "flux-klein",
            "FLUX.2 Klein 4B · image",
            "image",
            "flux-2-klein-4b-fp8.safetensors",
            "qwen_3_4b.safetensors",
            "flux2-vae.safetensors",
            768,
            4,
            IMAGE_PROMPT,
        ),
        Preset(
            "qwen-image",
            "Qwen Image 2.1 · image",
            "image",
            "qwen_image_2.1_int8_convrot.safetensors",
            "qwen3vl_8b_w4a8.safetensors",
            "qwen_image_2.1_vae_bf16.safetensors",
            512,
            8,
            IMAGE_PROMPT,
        ),
        Preset(
            "wan-video",
            "Wan 2.2 5B · short video",
            "video",
            "wan2.2_ti2v_5B_fp16.safetensors",
            "umt5_xxl_fp8_e4m3fn_scaled.safetensors",
            "wan2.2_vae.safetensors",
            640,
            20,
            VIDEO_PROMPT,
        ),
    )
}


class ComfyFailure(Exception):
    pass


def client(settings) -> httpx.AsyncClient:
    url = urlsplit(settings.comfy_trials_base_url)
    if (
        url.scheme != "http"
        or url.hostname not in {"127.0.0.1", "localhost", "::1"}
        or url.username
        or url.password
        or url.query
        or url.fragment
        or url.path not in {"", "/"}
    ):
        raise ComfyFailure("Local trials require a loopback ComfyUI URL.")
    return httpx.AsyncClient(
        base_url=settings.comfy_trials_base_url.rstrip("/"), timeout=30, trust_env=False
    )


def prepare_source(data: bytes, preset: Preset) -> tuple[bytes, int, int]:
    image = Image.open(io.BytesIO(data))
    if image.width * image.height > 32_000_000:
        raise ValueError("Source image exceeds the local trial pixel limit.")
    image = image.convert("RGB")
    scale = min(1, preset.max_edge / max(image.size))
    w, h = (max(64, round(edge * scale / 32) * 32) for edge in image.size)
    image = image.resize((w, h), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    image.save(output, "PNG")
    return output.getvalue(), w, h


def workflow(
    preset: Preset, image: str, prompt: str, seed: int, w: int, h: int, job_id: str
) -> dict:
    def node(kind, **inputs):
        return {"class_type": kind, "inputs": inputs}

    p = preset
    graph = {
        "1": node("UNETLoader", unet_name=p.diffusion, weight_dtype="default"),
        "2": node(
            "CLIPLoader",
            clip_name=p.encoder,
            type={
                "flux-klein": "flux2",
                "qwen-image": "qwen_image",
                "wan-video": "wan",
            }[p.id],
            device="default",
        ),
        "3": node("VAELoader", vae_name=p.vae),
        "4": node("LoadImage", image=image),
    }
    if p.id == "qwen-image":
        graph.update(
            {
                "5": node(
                    "TextEncodeQwenImage21",
                    clip=["2", 0],
                    vae=["3", 0],
                    prompt=prompt,
                    negative_prompt="",
                    resolution=0,
                    **{"images.image_1": ["4", 0]},
                ),
                "8": node(
                    "KSampler",
                    model=["1", 0],
                    positive=["5", 0],
                    negative=["5", 1],
                    latent_image=["5", 2],
                    seed=seed,
                    steps=p.steps,
                    cfg=1,
                    sampler_name="euler",
                    scheduler="simple",
                    denoise=1,
                ),
            }
        )
    elif p.id == "flux-klein":
        graph.update(
            {
                "5": node("CLIPTextEncode", clip=["2", 0], text=prompt),
                "6": node("ConditioningZeroOut", conditioning=["5", 0]),
                "7": node("VAEEncode", pixels=["4", 0], vae=["3", 0]),
                "11": node("ReferenceLatent", conditioning=["5", 0], latent=["7", 0]),
                "12": node("ReferenceLatent", conditioning=["6", 0], latent=["7", 0]),
                "13": node(
                    "CFGGuider",
                    model=["1", 0],
                    positive=["11", 0],
                    negative=["12", 0],
                    cfg=1,
                ),
                "14": node("RandomNoise", noise_seed=seed),
                "15": node("KSamplerSelect", sampler_name="euler"),
                "16": node("Flux2Scheduler", steps=p.steps, width=w, height=h),
                "17": node("EmptyFlux2LatentImage", width=w, height=h, batch_size=1),
                "8": node(
                    "SamplerCustomAdvanced",
                    noise=["14", 0],
                    guider=["13", 0],
                    sampler=["15", 0],
                    sigmas=["16", 0],
                    latent_image=["17", 0],
                ),
            }
        )
    else:
        graph.update(
            {
                "5": node("CLIPTextEncode", clip=["2", 0], text=prompt),
                "6": node(
                    "CLIPTextEncode",
                    clip=["2", 0],
                    text="Warped architecture, flicker, sudden camera movement, cuts, changing windows.",
                ),
                "7": node(
                    "Wan22ImageToVideoLatent",
                    vae=["3", 0],
                    start_image=["4", 0],
                    width=w,
                    height=h,
                    length=49,
                    batch_size=1,
                ),
                "11": node("ModelSamplingSD3", model=["1", 0], shift=8),
                "8": node(
                    "KSampler",
                    model=["11", 0],
                    positive=["5", 0],
                    negative=["6", 0],
                    latent_image=["7", 0],
                    seed=seed,
                    steps=p.steps,
                    cfg=5,
                    sampler_name="uni_pc",
                    scheduler="simple",
                    denoise=1,
                ),
            }
        )
    # Tiled decode limits peak memory, particularly for a video frame batch.
    graph["9"] = node(
        "VAEDecodeTiled",
        samples=["8", 0],
        vae=["3", 0],
        tile_size=256,
        overlap=64,
        temporal_size=16,
        temporal_overlap=4,
    )
    if p.kind == "video":
        graph["18"] = node("CreateVideo", images=["9", 0], fps=24)
        graph["10"] = node(
            "SaveVideo",
            video=["18", 0],
            filename_prefix=f"cityprompt_trials/{job_id}",
            format="mp4",
            **{"format.codec": "h264", "format.codec.encoding": "auto"},
        )
    else:
        graph["10"] = node(
            "SaveImage", images=["9", 0], filename_prefix=f"cityprompt_trials/{job_id}"
        )
    return graph


async def available_presets(settings) -> list[dict]:
    info = {}
    message = "Start ComfyUI on this computer."
    if settings.comfy_trials_enabled and not settings.is_production:
        try:
            async with client(settings) as c:
                response = await c.get("/object_info")
                response.raise_for_status()
                info = response.json()
        except (ComfyFailure, httpx.HTTPError, ValueError):
            pass
    else:
        message = "Local model trials are disabled on this server."
    result = []
    for p in PRESETS.values():
        missing = []
        if info:
            for n in workflow(p, "source.png", p.prompt, 1, 640, 384, "check").values():
                if n["class_type"] not in info:
                    missing.append(n["class_type"] + " node")
            for node, field, name in (
                ("UNETLoader", "unet_name", p.diffusion),
                ("CLIPLoader", "clip_name", p.encoder),
                ("VAELoader", "vae_name", p.vae),
            ):
                choices = (
                    info.get(node, {})
                    .get("input", {})
                    .get("required", {})
                    .get(field, [[]])[0]
                )
                if name not in choices:
                    missing.append(name)
        result.append(
            {
                "id": p.id,
                "label": p.label,
                "kind": p.kind,
                "available": bool(info) and not missing,
                "message": (
                    ("Ready" if not missing else "Missing: " + ", ".join(missing))
                    if info
                    else message
                ),
                "default_prompt": p.prompt,
                "max_edge": p.max_edge,
                "steps": p.steps,
                "duration_seconds": 49 / 24 if p.kind == "video" else None,
            }
        )
    return result


async def submit(settings, preset, image_bytes, prompt, seed, w, h, job_id):
    async with client(settings) as c:
        response = await c.post(
            "/upload/image",
            files={"image": (f"cityprompt_{job_id}.png", image_bytes, "image/png")},
            data={"type": "input", "overwrite": "false"},
        )
        response.raise_for_status()
        uploaded = response.json()
        image_name = "/".join(
            x for x in (uploaded.get("subfolder", ""), uploaded["name"]) if x
        )
        graph = workflow(preset, image_name, prompt, seed, w, h, job_id)
        # Current native ComfyUI accepts a client-assigned UUID. Persist it BEFORE
        # submission, so even a lost HTTP receipt can be recovered without reruns.
        response = await c.post(
            "/prompt",
            json={
                "prompt": graph,
                "prompt_id": job_id,
                "client_id": f"cityprompt-{job_id}",
            },
        )
        if response.status_code == 400:
            raise ComfyFailure(
                "ComfyUI rejected the workflow. Check its models and nodes; no automatic retry."
            )
        response.raise_for_status()
        receipt = response.json()
        if receipt.get("node_errors") or receipt.get("prompt_id") != job_id:
            raise ComfyFailure(
                "ComfyUI did not accept the stored job ID. Update ComfyUI before trying again."
            )


async def poll(settings, job_id: str) -> tuple[str, bytes | None]:
    async with client(settings) as c:
        response = await c.get(f"/history/{job_id}")
        response.raise_for_status()
        entry = response.json().get(job_id)
        if not entry:
            response = await c.get("/queue")
            response.raise_for_status()
            q = response.json()
            if any(row[1] == job_id for row in q.get("queue_running", [])):
                return "running", None
            if any(row[1] == job_id for row in q.get("queue_pending", [])):
                return "queued", None
            return "submission_unknown", None
        state = entry.get("status", {})
        if state.get("status_str") == "error":
            raise ComfyFailure(
                "ComfyUI generation failed. Check its log for memory or model errors. No automatic retry."
            )
        if not state.get("completed"):
            return "running", None
        output = entry.get("outputs", {}).get("10", {})
        assets = (
            output.get("images") or output.get("videos") or output.get("gifs") or []
        )
        if not assets:
            raise ComfyFailure("ComfyUI finished without an image or video output.")
        asset = assets[0]
        if (
            asset.get("type") != "output"
            or ".." in asset.get("filename", "")
            or ".." in asset.get("subfolder", "")
        ):
            raise ComfyFailure("ComfyUI returned an invalid output reference.")
        response = await c.get(
            "/view",
            params={k: asset.get(k, "") for k in ("filename", "subfolder", "type")},
        )
        response.raise_for_status()
        if len(response.content) > 100_000_000:
            raise ComfyFailure("Local output exceeds the 100 MB trial limit.")
        return "saving", response.content
