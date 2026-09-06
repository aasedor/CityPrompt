# Three-building catalogue publication

The user approved publication with “Publish them to the main catalogue” on 2026-09-06. The approved scope is the post-war bungalow v005, Edwardian Foursquare v004, and sandstone civic hall v007. Each exact GLB passed independent holistic architectural-clay review with zero unresolved P0/P1 findings and was trialed on open land in local City Prompt.

`seed/model-library/rlasm-architectural-clay/library.json` is the durable activation record. It locks the three GLBs, actual native bounds, original catalogue references and independent reviews. Runtime models use Git LFS. Superseded builds and full visual evidence remain in the external candidate directories referenced there. Historical pilot records remain unchanged; this approval supersedes their local-only restriction for these exact deliveries only.

The standard Buildings picker now includes Post-war bungalow, Edwardian Foursquare and Sandstone civic hall. Saved `trial_*` identifiers remain stable for compatibility, but the cards are ready and have no trial label or development flag. Wider home plots repeat complete houses; the civic hall remains one complete native-size landmark. The Foursquare family is included in native detached-home assembly.

## Install the catalogue in a target environment

Hydrate the three GLBs and their locked source images with Git LFS. Run `python tools/seed_model_library.py --rlasm-clay-only --dry-run` first, then the same command without `--dry-run`, supplying the target storage/database options and `--owner-id` for an existing user. The command adds public model-library rows and object files; it leaves existing rows unchanged. A Git merge alone does not seed a deployed database.

The local trial is project `0c5c0816-3c68-4eea-8b74-150b84c59259` at port 5174. Its installation uses the isolated database at port 55432 and storage at port 59002. Prior trial objects stay available so saved scenes retain their original URLs.

Before large-scale classroom use, add reviewed distance LODs for the 10.3 MB Foursquare and 12.3 MB civic hall. Existing ground-pad blending remains a separate improvement. Publication does not imply surveyed accuracy, zoning compliance, arbitrary mesh stretching, textured-keeper approval, or a paid-render consistency test.
