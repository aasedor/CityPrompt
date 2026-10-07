# Catalogue image and model delivery checks

The October 4 audit covers every choice in the local picker: 44 buildings,
30 parks and 31 streets, including the ten sealed temporary building trials.
All 354 distinct image/model dependencies passed the HTTP/content/hash audit,
including alternate saved park layouts and legacy capture image bindings.
All 137 packet images were fully decoded with Pillow. The 19 advertised expansion
buildings passed exact readback from the isolated Model Library bucket.
This checks missing or corrupt assets and bindings; it does not certify every
variant's walking, terrain, editing or visual quality.

The deeper audit restored two street hero images and thirteen flexible-park
components that remained Git LFS pointers. The earlier image audit used raw
IDs and missed those two transformed picker mappings. The new audit loads the
actual `CLASSROOM_CHOICES` and `pickerHeroImage` modules, follows native park
and street dependencies, and includes the shared kits used by flexible parks.
An additional 33 declared compatibility files were restored from verified
local evidence: four park GLBs, fifteen park capture thumbnails and fourteen
street references. These intentional runtime dependencies are now in Git LFS.

## Preventing silent regressions

- `npm run dev` runs the complete local catalogue delivery check first. Missing
  files, Git LFS pointers, HTML application fallbacks, invalid images, corrupt
  GLBs, unbound model dependencies and wrong exact model hashes fail the check.
- Vite dev and preview return 404 for missing catalogue assets and 503 for
  unhydrated assets. They cannot silently return the application's HTML page.
  Restored public files are served immediately, even when Vite's original
  public-file inventory predates the recovery.
- An optional local packet is checked against its catalogue source hashes and
  every asset hash before startup. Changed asset bytes are rejected again at
  request time. A stale source branch cannot reuse the packet silently.
- The local stack launcher requires the expected 19 public expansion variants
  and their exact stored bytes. An empty database cannot pass. This check never
  seeds, deletes or alters records.
- CI checks the catalogue's representation/hash bindings and the failure
  regressions. CI metadata checks do not establish runtime hydration.
- The 15 original fixed validation buildings retain their stable saved IDs and
  now bind directly to their already-declared exact local GLB URLs. They do not
  depend on a developer having unrelated Model Library rows installed.

## Reusable local packet

The complete checked packet is outside Git:
`C:/dev-artifacts/CityPrompt/catalogue-delivery-2026-10-04-v002`.
It contains 335 web assets with an exact manifest. It does not inject trial
choices, grant approval, activate entries or publish anything.

For the ordinary source app, set `CITYPROMPT_CATALOGUE_PACKET` to that directory,
then run `npm run dev` from `frontend`. Preserve the existing backend/proxy and
map-key environment. The packet restores the stable 95 source choices; the
separate sealed trial launcher still owns the additional ten temporary choices.
A fresh ordinary source preview passed startup with 95 choices and 324
dependencies. The browser decoded all 44 building and 30 park card previews;
the complete street dependency audit passed. The disposable project displayed
the restored tower and station rather than blank massing. Browser evidence is
under the external `main-app-runtime` artifact directory.

Read-only live audit:

```
python scripts/check_model_library_storage.py --require-catalogue --report <storage.json>
cd frontend
npm run check:catalogue-delivery -- --base-url=<app-url> --model-library-report=<storage.json> --report=<audit.json>
```

Run the storage check in the backend's actual database/S3 environment. The
receipt must be fresh. Add `--fixtures=<sealed-ten-fixtures.json>` to include
the local ten-building trial and `--packet-dir=<new-external-directory>` to
create a checked packet. Existing differing packet bytes are never overwritten.
The generated packet and audit receipts stay outside the source tree.

The 20-building generation automation remains paused. No paid generation calls
were made. The user's original projects were preserved. The later explicit
request for render credits granted the isolated trial account 1,000 City Prompt
tokens and enabled its existing OpenAI provider configuration. Read-only model
discovery and browser controls verified access; no image was generated to test it.

## Limits

These checks prevent the observed missing-file, pointer, wrong-hash, unbound
model and HTML-fallback failures from passing as healthy. Runtime availability
does not certify walking, terrain, architectural quality or every saved project.
The larger historical asset manifest remains a metadata inventory here; its
4,004 unhydrated historical dependencies require the separate hydrated release
workflow. The current picker packet and Model Library received actual byte checks.
