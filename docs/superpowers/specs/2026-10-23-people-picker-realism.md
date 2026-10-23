# Realistic People picker images

User approved Maya's photoreal full-body studio portrait on 2026-10-23 and asked
to apply that style to all 23 picker characters. Only the picker changes. The
stylized GLBs, IDs, transforms, rigs, saved actions and render pipeline remain
unchanged. Preserve original model thumbnails and byte manifests.

Generate one identity-specific image per character from their actual thumbnail,
matching hair and complexion. Following the user's correction, use distinct
clothes and styles rather than repeating the source models' overshirts. The
finite wardrobe list is `tools/people_pilot/appearance_styles.json`: dresses,
athletic outfits, knits, hoodies, office tailoring, casual and outdoor clothing.
Reuse the approved Maya pilot and reviewed Clara coat portrait as two choices
within that varied set. Keep full bodies and shoes visible on a neutral studio background.
These are imagined AI appearance/style previews, not guaranteed identities or
wardrobes in output. Only card names/style captions change; runtime labels and
render prompts keep their existing behavior.

Keep raw outputs, prompts and hashes outside the tree. Promote reviewed compact
WebP derivatives to the established external local public directory. A separate
23-entry manifest links the previews to stable actor IDs. Browser cards should
label AI previews and explain that placed people use simplified 3D models.

Alternatives: replacing GLBs was explicitly declined; altering original model
thumbnails would obscure source QA. Separate appearance previews preserve both.

Verify all 23 source model hashes, unique preview mappings and HTTP bytes;
test thumbnail precedence without GLB loading, picker labels and existing detail
controls; run type-check, scoped lint and local browser checks. No paid API calls,
push or deployment. Hosted publication remains a separate release gate.
