# Codex LEGO Archviz v5 pilot

## Result

The mass-timber pilot now uses a versioned AI-assisted material profile instead of changing the baseline library. GPT Image supplies de-lit source imagery for the engineered-timber façade, the sedum roof and an eight-room interior atlas. The Blender compiler turns the surface sources into tileable albedo, OpenGL normal and roughness maps, assigns different room cells behind recessed glazing, adds botanical planter silhouettes, and exports the same modular glTF family used by the globe builder.

The quality reference supplied for this work is a complete photogrammetric city scene, not one conventionally modeled building. Matching that class therefore has two routes:

1. authored replacement buildings: the current LEGO pipeline, improved with construction depth, PBR materials, real glazing/interior layers, roof detail and high-quality lighting;
2. captured existing buildings: photogrammetry or LiDAR, simplified and retextured for delivery.

The first route is appropriate for proposed designs and archetype-driven planning. The second is the closest technical match for existing real-world buildings.

## 2026 quality benchmark

- **Physically based material response.** A high-end surface is a calibrated set of base color, normal/height, roughness, AO and—where relevant—transmission, IOR, clearcoat or anisotropy. Khronos glTF PBR now standardizes the core set plus extensions such as clearcoat, transmission, volume, IOR and anisotropy: <https://www.khronos.org/gltf/pbr/>.
- **Layered construction geometry.** Window reveals, slab edges, copings, gaskets, mullions, rails, flashings, drains and roof plant must cast their own shadows. A flat textured extrusion cannot reach the target.
- **Indirect light and reflections.** Epic's current Lumen documentation describes dynamic diffuse interreflection and indirect specular reflections across detailed environments; this is why final QA uses Cycles rather than judging materials only in the fast viewport: <https://dev.epicgames.com/documentation/en-us/unreal-engine/lumen-global-illumination-and-reflections-in-unreal-engine>.
- **Dense detail with controlled delivery.** Nanite demonstrates the 2026 expectation of pixel-scale source geometry and view-dependent streaming, but this web application still needs explicit LOD and compression: <https://dev.epicgames.com/documentation/en-us/unreal-engine/nanite-in-unreal-engine>.
- **Material variation and lived-in interiors.** Repeating every bay and floor is one of the strongest procedural tells. V5 changes atlas cells by bay, side and assembled level while retaining repeatable modules.
- **Context and ground contact.** The production result depends on persistent clipping of the scanned building, terrain seating, consistent sunlight and surrounding Photorealistic 3D Tiles. The lightweight Blender city is only a QA rig.

## Tool decisions

### Used in this pilot

- **GPT Image:** produces controlled, de-lit source photographs and the room atlas. It is not treated as a normal-map generator. The existing deterministic texture pipeline removes broad lighting, measures and repairs seams, and derives normal/roughness maps locally.
- **Blender 5.1 + Cycles:** authors geometry, validates material response with path-traced review images, bakes modular AO, and exports glTF.
- **glTF PBR + Three.js:** preserves a portable web material contract. The globe runtime increases anisotropy and tunes coated dielectric glass on clone-owned materials.

### Recommended next tools

- **Adobe Substance 3D Sampler/Designer/Painter:** Sampler's April 2026 Image to Material workflow generates normal, height and roughness while removing baked shadows/highlights; it should replace the simple luminance-derived maps for production hero materials: <https://experienceleague.adobe.com/en/docs/substance-3d-sampler/using/filters/tools/image-to-material>.
- **RealityScan or another photogrammetry pipeline:** use for an existing landmark or when the desired output truly is the supplied Google-Earth-like quality. RealityScan supports photo/LiDAR reconstruction and automated simplify/export workflows: <https://dev.epicgames.com/documentation/realityscan/reconstruction-commands>.
- **KTX 2.0 / Basis Universal and mesh compression:** the current high-quality family is larger than the desired web budget. KTX2 reduces download and GPU-memory cost and Three.js has a dedicated KTX2 loader: <https://www.khronos.org/ktx/> and <https://threejs.org/docs/pages/KTX2Loader.html>.
- **V-Ray/Chaos Vantage or Unreal Engine:** valuable for marketing/final-frame review, not as the delivery runtime. V-Ray 7 Update 3's 2026 viewport combines real-time ray tracing with final-quality iteration: <https://www.chaos.com/press/v-ray-7-update-3-real-time-rendering-meets-the-v-ray-viewport>.
- **Geometry Nodes or Houdini:** the next procedural-authoring step for façade rules, believable vegetation, non-rectangular massing and LOD generation.

## Implemented v5 changes

- Versioned overlay library at `tools/archetype_compiler/textures_archviz_v5`; unchanged materials fall back to the baseline library.
- GPT-derived CLT and sedum sources with deterministic albedo/normal/roughness outputs and provenance manifest.
- Eight-cell residential interior atlas with face-level UV selection and per-floor variation in assembled QA exports.
- Alpha-blended low-iron glazing with dielectric/clearcoat runtime tuning.
- Stem-and-leaf balcony planting, slab underside shadow layers, and retained v4 façade/roof construction detail.
- Optional denoised Cycles presentation rendering through `--presentation-engine cycles`.

## Remaining gap

The pilot is now in the authored real-time archviz class, but it is not a photogrammetric scan. The largest remaining gains will come from unique massing and corner rules, scan/artist-authored hero assets for entrances and trees, production HDR environment lighting, and a formal LOD/KTX2 delivery pass. The generated assembled family is intentionally quality-first and currently exceeds the 8 MB target; it should not be promoted to the default catalogue until compression and LODs are added.

## Reproduce

```powershell
py tools/archetype_compiler/generate_family.py `
  --archetype-id contemporary_midrise `
  --variant-id mass_timber_biophilic_tower `
  --output build/lego-archviz-v5/mass-timber `
  --textures tools/archetype_compiler/textures_archviz_v5 `
  --presentation-engine cycles `
  --presentation-samples 32
```
