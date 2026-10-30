# Lifelike picker hero checkpoint

All **202 development choices** have decoded, visually inspected photographic heroes: 104 buildings, 42 parks and 56 streets. The actual picker resolver was audited; inspecting only canonical fallback images initially overstated missing images because many cards already had curated photographs.

Changes: five new parkade photographs replace technical elevation boards; six public-realm cards use existing locked photographic references instead of model previews/missing archive art; seven newer buildings gain explicit exact-placement hero entries. Five missing historical-building reference URLs were hydrated from verified existing LFS cache, without changing their tracked bytes. Original model thumbnails, GLBs, source references, catalogue content and activation gates are unchanged.

The hero test covers development trials explicitly while preserving production exclusion. All five new full-resolution WebPs use LFS. Original PNGs, generation IDs, reference-board identities, decoded URL hashes and contact sheets are retained in the external review directory. Independent review found no material archetype-identity mismatch in the five parkade photographs.

Verification: 58 frontend tests across six files, another 20 hero tests in development mode, TypeScript, nine validation-bundle tests and the current 5,441-record runtime inventory metadata check pass. Browser search verified the changed card images; screenshots show the parkades plus selected park, street and historical cards. The only observed console errors came from a browser extension. These checks do not certify every model or the entire release package's hydration.

The inventory was regenerated from the canonical checkout after restoring 376 pre-existing ignored runtime dependencies from the existing local preview. That restoration does not add new asset contents to this commit. Previously unrecorded source dependencies/dynamic asset counts are now reflected in the generated inventory; actual release hydration remains a separate check.

Private review folder: https://drive.google.com/drive/folders/1-B97Xt1sq8iREDu-qCABsW2lWqBgjLIc

External originals and delivery receipts: `C:/dev-artifacts/CityPrompt/claude-crossings-practical-20261029/hero-audit/`. No push or deployment.
