# Public Realm LEGO V1

Date: 2026-07-21
Branch: `codex/public-realm-lego-v1`

## Outcome

AI Master Planner communities now use a finite, executable Public Realm LEGO
catalog for parks and streets. A generated public-realm zone is not considered
compiled merely because it has a recognizable catalog name: its exact source
identity, visual variant, measured geometry, renderer profile, components and
capability revision must resolve to one canonical recipe.

The existing Classic colored-polygon planner and render pipeline remain on
their established broad visual catalog. Strict Public Realm LEGO selection is
enabled only when the runtime LEGO planning catalog is supplied.

## First executable cohort

### Parks

- Pocket park / courtyard
- Neighborhood / community park
- Civic plaza
- Linear greenway
- Stormwater / water ecology

The browser has an explicit resolver for every server-advertised family. The
pocket and neighborhood families add fixed metric playground, shade, pavilion,
furniture and planting assemblies where their whole safety envelopes fit. The
civic, greenway and water families retain their reviewed deterministic ground
programs and family-specific landscape rules rather than falling through to a
generic park.

### Streets

- Local public realm
- Native 22 m complete main street
- Accessible four-way intersection
- Four-arm compact roundabout

Local source profiles retain their reviewed native right-of-way dimensions.
The 22 m main street has explicit sidewalks, furnishing bands, protected cycle
tracks, buffers, parking/loading and two movement lanes. Accessible
intersection geometry is graph-owned and is mounted only when all contributing
streets carry supported compiled V1 contracts; Classic streets are unaffected.

## Planner-to-render contract

1. The AI tool schema exposes only archetypes and variants present in the
   executable server catalog.
2. Validation repairs unavailable choices before geometry generation.
3. Generated parks and streets persist their exact archetype and selected
   variant.
4. Metric geometry is checked against the selected family's envelope.
5. Community 3D atomically compiles and persists the canonical recipe at
   `properties.public_realm_lego` before mutating any scene content.
6. Representation fingerprints bind the source geometry and exact recipe.
7. Direct 3D reconstructs the recipe from the locked live geometry and rejects
   any stale, altered or geometry-mismatched claim before reserving credits.
8. The browser accepts Direct claims only for public-realm family contracts it
   can actually reproduce.

## Geometry hardening

- Courtyards are repaired and precision-snapped in the local metric CRS before
  WGS84 serialization. Projection seams can no longer become zero-area park
  zones.
- Compact linear central greens route to the greenway family only when they
  meet a 3:1 morphology gate; square pond-edge lobes route to pocket gardens.
- Large clipped internal courtyards use the no-playground courtyard program
  without pretending to be neighborhood parks.
- Native AI street widths are established before the graph is generated. The
  first cohort uses a 22 m main street, 16 m Calgary local, 14 m narrow local,
  and 10 m yield/woonerf sections.
- Locked public-realm geometry retains a compatible exact identity instead of
  combining an inferred archetype with an unrelated visual variant.
- Fixed park elements use the same terrain-surface datum as their ground
  program. Decorative detail is deterministically budgeted and repeated street
  fixtures are instanced to protect the Google Tiles WebGL budget.

## Residual landscape

The site boundary remains the ownership mask for un-authored parcel land. On
Community 3D generation, the residual recipe subtracts buildings, authored
parks, streets and other exclusions from the boundary, decomposes the remaining
ground, and applies deterministic context-aware landscaping. This closes the
visible gaps between independently authored polygons without altering those
polygons or allowing landscape to cross the parcel boundary.

## Live visual QA

The live checks used one Google Tiles tab at a time. That constraint matters:
two simultaneous globe tabs previously exhausted the browser's WebGL context,
which can make a sound scene look as though its detailed buildings vanished.

### Clean common-site pilot

The fresh Environmental pilot is the representative everyday case: 5
buildings, 2 parks and 7 streets. Its atomic Community 3D build assembled all 5
buildings with no family or skipped-building fallback, compiled all 9 authored
public-realm systems, and landscaped 6,227 m2 of otherwise un-authored site
boundary with 5 deterministic trees. The 30-degree oblique review showed a
coherent LEGO community without Meshy or planned-massing substitution.

The free 1280 x 720 Direct capture classified 10.9% of the image as proposal:
2.0% ground, 0.1% landscape, 2.8% street, 2.4% park and 3.6% building. Those
figures provide a repeatable source-capture baseline for the paid fidelity
check; they are not a subjective image-quality score.

### Compact compatibility pilot

The mixed manual-plus-AI project contains 7 buildings, 3 parks and 12 streets.
The build added 3 detailed buildings alongside 4 existing ones, mounted 13
renderable park/street layers, and landscaped 710 m2 of residual parcel. It was
reviewed at 30-degree oblique, 73-degree steep and 90-degree overhead. Detailed
models remained mounted through the camera changes and the model off/on cycle;
turning models off exposed colored massing immediately, and turning them on
restored the LEGO layers.

This project deliberately retains overlapping manual and AI-authored park
surfaces. Their grey/green visual overlap is a mixed-content authoring artifact,
not the clean reference for family quality; the common-site pilot above is the
preferred visual baseline.

### 65-zone stress pilot

The bounded scale-up scene contains 65 authored physical zones: 46 buildings,
6 parks and 13 streets. All 46 building representations remained visible at
30-degree oblique, 74-degree steep and 90-degree overhead, including after a
model off/on cycle. No WebGL loss was observed in the single-tab run. At this
scale the intentionally bounded street detail and park planting LOD become
sparser, which kept interaction stable while exposing the next visual-quality
target: stronger district-scale street material and canopy continuity.

This stress scene began under an older public-realm recipe revision, so it was
also redrawn under the final contract. The redraw produced 50 physical plan
zones plus 4 framework overlays: 30 buildings, 5 parks and 15 streets/paths.
The atomic rebuild placed all 30 detailed buildings with no family-pending
masses, compiled all 20 public-realm systems and landscaped 7,432 m2 of residual
site. A free 1280 x 720 Direct capture was then enabled and classified 3.8%
proposal coverage: 0.4% ground, 1.6% street, 0.6% park and 1.2% building.

That redraw exposed two useful hardening cases. A parcel-edge trail claimed a
4 m width but measured 2 m after half its corridor was clipped; several access
connectors had the same latent defect. Connector routing is now
corridor-width-aware, requires at least 90% in-parcel coverage and chooses a
longer truthful route or leaves the anchor unserved. A later camera gesture also
proved that exact boundary undo must restore, rather than repeatedly invalidate,
the matching plan cohort. Canonical boundary fingerprints now distinguish an
exact undo from a genuinely changed or expanded boundary.

## Direct 3D fidelity checkpoint

The first paid `gpt-image-2` common-site attempt generated a visually polished
image, but it was correctly rejected before acceptance. Raw context
registration scored 0.556, and the provider had redesigned the authored public
realm into a formal canal/plaza composition while also changing building
appearance. The rejected image was retained only as a diagnostic artifact; it
was not promoted as a project render. The attempt consumed 46 internal render
tokens.

The context-lock hardening adds a style-invariant, bidirectional structural-edge
registration path for cases where photoreal restyling defeats raw luminance
correlation. It does not weaken the translation, rotation, interior-geometry or
class checks. Once a candidate is structurally registered, source-geometry
fusion discards provider-authored geometry and the exact exterior hard
composite preserves every mask-zero context pixel byte-for-byte.

A second paid common-site call passed the hardened path and was saved as project
render `632fe7bc-639c-4207-8964-bf13fd90f854`. It registered at 78.8%, required
only 3.4/2.4 px translation and -0.10-degree rotation, and finished with zero
exterior channel delta. Building-edge fidelity was 98.1% and semantic-edge
fidelity was 99.0%. The result is therefore a source-anchored material,
vegetation and lighting finish of the LEGO scene, not a provider redesign.

## Recommended next family sequence

| Priority | Family package | First executable scope | Acceptance gate |
| ---: | --- | --- | --- |
| 1 | Protected-cycle collector and arterial | Native collector/avenue sections, protected junction transitions, common three-arm junction and raised crossing nodes | Continuous safe cycle/foot routes, metric lane envelopes and no graph-owned overlap at every supported junction |
| 2 | Stormwater, wetland and bioswale depth | Inlet, outlet, weir, wet shelf, forebay, boardwalk and maintenance-edge modules | Water levels and access clearances fit wholly inside the authored polygon; no decorative water substituted for drainage logic |
| 3 | Sports and active recreation | Multi-use field, basketball/tennis/pickleball courts, fencing, goals, lighting and accessible spectator edges | Whole regulation element plus runoff/safety envelope must fit or fail closed; no clipped court markings or equipment |
| 4 | Urban plaza and courtyard expansion | Market plaza, campus quad, civic forecourt and intimate courtyard variants | Tested event, loading, fire-access and accessible-route clear zones with deterministic furniture packing |
| 5 | Greenway, creek and trail expansion | Daylighted creek, riparian greenway, rail trail, trailhead and bridge/underpass nodes | One continuous end-to-end accessible route and hydraulically/structurally valid crossings |
| 6 | Canopy-dependent landscapes | Urban forest, botanical garden and habitat-restoration families | Biome, age, season and crown-LOD libraries must pass the same single-tab Google Tiles stress gate |

The sequence keeps the previously recommended order: common network and
safety-critical systems first, then high-demand recreation and civic space,
then the visually distinctive families that need deeper ecological or canopy
libraries.

## Meshy versus LEGO

| Decision | Meshy asset generation | Archetyped LEGO compiler |
| --- | --- | --- |
| Best role | A unique landmark or approved hero object | The planning source of truth for an ordinary community |
| Repeatability | Generation can change topology, dimensions and appearance between attempts | Same source identity, geometry and catalog revision produce the same canonical recipe |
| Site fit | A finished mesh is difficult to resize without distortion or material/UV damage | Native metric modules are selected, rotated and bounded-fit against the actual polygon |
| Editing | Mostly object-level transform or regeneration | Family, variant, storeys, section, fixtures and landscape modules remain structured and replaceable |
| Parks and streets | No shared network, clearance, drainage or planting grammar | Explicit section, node, safety-envelope, component and LOD contracts |
| Community scale | Per-asset generation/import latency and cost accumulate | A reviewed family can be compiled across many zones without another asset-generation call |
| Failure behavior | A plausible mesh can hide a wrong fit or stale source | Fingerprints and metric gates fail closed before strict Community 3D mutates the scene |
| Visual ceiling | Strong one-off sculptural detail | Strong geometric fidelity and consistency; Direct 3D supplies the final material, foliage, light and atmosphere pass |

Recommended production split: LEGO for every ordinary community building,
park and street; Direct 3D for photoreal finish; Meshy only for approved unique
landmarks that cannot be expressed by an existing family. Meshy is therefore a
specialist asset source, not an alternate community-planning pipeline.

## Verification contract

- Full generator-to-strict-recipe probes at compact and district scale for all
  three AI scenarios.
- Community 3D transaction tests, representation freshness and Direct preflight
  tamper tests.
- Focused park, street, geometry, LOD and Classic-isolation frontend suites.
- TypeScript type-check and production build.
- One-tab live Google Tiles review at approximately 30 degree oblique, 60-75
  degree steep and 90 degree overhead.
- Compact, 46-building legacy-scale and 30-building current-contract stress
  projects, including reload, camera changes, model off/on, plan overlay,
  exact boundary undo and Direct-capture readiness.

Final verification on the branch completed with 278 combined backend tests,
557 frontend tests across 62 files, TypeScript type-check, production build,
Ruff on all touched backend modules and `git diff --check`. The remaining test
and build notices are pre-existing dependency, React test and bundle-size
warnings rather than failures in this initiative.
