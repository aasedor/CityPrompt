# Vancouver Laneway House — RLASM v12

Status: `PASS_FINAL_ARCHETYPE_VISUAL_QA`

These are actual Blender renders of the Vancouver laneway-house 3D model, not
AI-generated building previews. AI image editing was used only for the atomic
hardware-free cedar door cards and the isolated sconce reference card.

This revision closes the final-render entry review:

- two distinct entrances are explicitly inventoried;
- the primary door beneath the balcony and the side recessed door are both
  modeled;
- both leaf cards are hardware-free;
- each door has exactly one attached physical latch assembly;
- the side leaf is 0.28 m behind the facade plane;
- both entrance steps meet grade with zero gap;
- the side sconce has a dedicated reference card and fixture-local 18 W light;
- no floating item or full black reveal was detected; and
- the GLB imported cleanly during independent QA.

The independent reviewer approved v12. Minor non-blocking observations are a
bright sconce face and somewhat chunky concrete entrance blocks; those are
acceptable at City Prompt scale and can be softened during downstream image or
video refinement.

The method documents in the parent `sticker-method` directory are updated to
RLASM 1.6.0 with the reusable entry-role, hardware-exclusivity, recess,
ground-contact, and final independent-review gates learned here.
