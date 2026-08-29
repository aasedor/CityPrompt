# RLASM v5 — Second Empire fire-station dormer contact correction

Candidate `10-second-empire-fire-station-rlasm-v20` is the independently
reviewed correction for the floating side dormer windows identified on
2026-08-29. It preserves the approved v18 limestone/material pass while making
each side window part of a complete occupied dormer wall-and-roof assembly.

## Phone review

- [V18 to v20 before/after](phone/fire-station-v18-v20-dormer-contact-phone.png)
- [V20 contact close and whole-envelope proof](phone/fire-station-v20-dormer-contact-close-phone.png)

## Review decision

Independent review: `PASS_ZERO_P0_KEEPER_READY`.

- Side dormer cheeks cross the constructed mansard plane rather than floating
  outside it.
- Each full-depth wall cut exposes limestone jamb, head, and sill returns.
- Oak sash, neutral glass, and occupied depth sit at distinct inward datums.
- Closed limestone gables carry bounded, seated slate roof caps.
- The roof intersection is sealed by a bounded slate apron/shadow joint; no
  open black gap or unsupported cap remains.
- Front geometry, crest alignment, warm limestone family, slate, oak, copper,
  iron, glazing, and complete-envelope cameras show no regression.
- Generic fallback count: `0`.

The exact review records are in [evidence](evidence/). All 12 full-resolution
review renders, including the dedicated contact close, are in
[renders](renders/). V18 and the failed-cut v19 remain preserved.

## New reusable method step

RLASM now requires a roof-mounted opening contact section. The opening datum is
solved from the actual sloped roof plane; the lower cheeks cross that plane;
the cutter spans every opaque body layer; and the reveal, sash, glass, and
occupied room layer are visibly ordered from exterior to interior. A closed
gable, seated bounded cap, and flashing/apron own the weather joint. Both side
elevations, aerial, and an oblique contact close are mandatory proof.

## Selected SHA-256

- `fire-station-v18-v20-dormer-contact-phone.png` — `e1b5a963932046cca7d30f3ddf5313561058248330d83147c2b774df806bb9aa`
- `fire-station-v20-dormer-contact-close-phone.png` — `64b1470c59f543edda3012d553e999acef108e56cc00d45e1e61c496b3f5af62`
- `front.png` — `e063228b6ba40b7b7ba1558a34c39f480ae82cb21c6a0dab99c5e6f214432554`
- `aerial.png` — `89acdf764fb9b9b452d7cffade24fa8a24fc18ca79f3c9ea86e58971233b0dd7`
- `dormer_contact_close.png` — `ca9cb7b6ab44de6b83ed7f890cc68a23a87279e7cc4c3f8456b6d3da028f83fe`
- `independent-review.json` — `800d13807f1642c60aef51ead7e640a347bf4574cd0c7881680627d8b6304c10`

Earlier candidates and unrelated untracked showcase packages were not
overwritten, staged, or removed.
