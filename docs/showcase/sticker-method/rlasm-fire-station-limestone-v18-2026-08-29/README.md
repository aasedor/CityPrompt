# RLASM v5 — Second Empire fire station limestone correction

Candidate `10-second-empire-fire-station-rlasm-v18` is the independently
reviewed correction requested on 2026-08-29. The user-approved orthographic
crest establishes one warm aged limestone family for the complete exterior
masonry envelope.

## Phone review

- [Source and v18 limestone comparison](phone/fire-station-v18-source-limestone-phone.png)
- [V14 to v18 before/after](phone/fire-station-v14-v18-before-after-phone.png)

## Review decision

Independent review: `PASS_ZERO_P0_KEEPER_READY`.

- The former cool-white secondary stone family is gone.
- Coursed wall fields and dressed quoins, arches, returns, cornices, dormers,
  cupola columns, crest carrier and supports read as one warm aged limestone
  family.
- Slate, oak, copper, iron and glass remain distinct source-locked materials.
- Left, right, rear and rear-side cameras now show the complete grade-to-finial
  envelope and footprint with neutral margin.
- Generic fallback count: `0`.

The exact review records are in [evidence](evidence/). All 11 full-resolution
review renders are in [renders](renders/).

## New reusable method step

RLASM now includes a building-level material-family contract. When several
semantic roles are the same physical substance, they share one recorded family
authority even when their construction finish differs. Coursed, dressed and
carved variants may change joints, relief, roughness and restrained value, but
must retain continuous hue, aging and mineral character across every elevation.

When the earlier dressed-stone sheet remained too cool, a new ornament-free,
shadow-neutral specimen was conditioned from the approved crest. Its exact
input hash, prompt, output hash and byte count are preserved in
[material provenance](materials/fire-crest-warm-aged-limestone-dressed-v1-provenance.json).

## Selected SHA-256

- `fire-station-v18-source-limestone-phone.png` — `d159fcc64ae2ab60b2ce7c6e6a370e4691e404d60f1938601cc4d87cdbdbfe0e`
- `fire-station-v14-v18-before-after-phone.png` — `4bc727e047ae7583a1024c51afe68492fcb2024c818b102d58b1b11d2864ee6c`
- `front.png` — `a1ac90b4e854987ad6100a3d3c95cff6a855d628043dd5c02e65606a3baa3b65`
- `front_corner.png` — `51ed7e4b6aefb586afcd46aac7906ba20b0b5d9d3db7013e053c2be09ff8b56d`
- `aerial.png` — `112adab5cc932ee642cf176f4e0440b129e12f71c2d8755fd581c3f29da556fa`
- `fire-crest-warm-aged-limestone-dressed-v1-albedo.png` — `2ee52b5ed02e91d556aa4a299612f787c4c1a0bf3dc8e7e05149e0edf2781be2`

Earlier candidates remain preserved and were not overwritten.
