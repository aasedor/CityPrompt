# Chat History Analysis - Key Learnings from SiteForge Development

Extracted from ~16,500 lines of Claude Code session transcripts covering weeks of development.

---

## User Profile & Preferences

### Working Style
- Prefers to give detailed multi-point specifications (e.g., "Master Refactor: 5-point plan") and have Claude implement while away ("I am going to head out for a bit to walk my dog. And when I come back, hopefully it is done.")
- Often works in evening sessions, heading to bed with instructions to keep coding overnight
- Has a dog they walk during long coding sessions; also spends time with son and wife
- Goes out with friends and expects autonomous progress while away
- Frequently shares Gemini analysis/suggestions as input for Claude to implement

### Communication Patterns
- Shares screenshots constantly to show issues and results
- Sends Gemini's analysis as reference material (often copy-pasted chat transcripts)
- Gives thumbs-up quickly when something works: "These look great!", "YES! These are perfect and beautiful"
- Quick to request reverts when something doesn't work: "revert that. It doesn't work"
- Prefers to see working examples before committing to batch operations: "can you create a few examples before we proceed with them all?"

### Technical Comfort
- Relatively new to local development workflows (asked "how do I restart it?", "I am not sure where the terminal is", had trouble with venv activation, PowerShell syntax)
- Uses PowerShell on Windows (requires semicolons not &&, different path syntax)
- Runs into OneDrive git lock file conflicts constantly (OneDrive syncs .git folder, creating index.lock)
- Has a friend/collaborator (beemanbesh) who works on the same codebase, pushes to a separate remote

### Frustrations
- Context resets when Claude sessions run out of tokens (happened multiple times)
- OneDrive git lock files blocking commits/pushes
- When renders don't match expectations after multiple iterations
- When code changes inadvertently break something that was working

### Teaching Context
- University professor/instructor who teaches with this tool
- Students create site plans and render them
- Students were hitting crashes (variant_0 bug), render quality issues, and token limits
- Student feedback drives feature priorities (people in street view, occlusion culling)
- Wants to create a business out of this ("let's make this great. I am going to try and create a business out of this")

---

## Technical Decisions & Architecture

### Render Pipeline Evolution
1. **Started with fal.ai** - original render provider, migrated away
2. **Moved to Vertex AI Imagen 3** (`imagen-3.0-capability-001`) - inpainting with binary masks
   - Used REFERENCE_TYPE_RAW + REFERENCE_TYPE_MASK
   - EDIT_MODE_INPAINT_INSERTION
   - Had persistent quality issues: buildings not rendering, zones bleeding into each other
3. **Switched to Gemini API** (`gemini-2.5-flash-image`) - dramatically simpler and better results
   - Direct API via generativelanguage.googleapis.com (not Vertex AI endpoint)
   - Requires GEMINI_API_KEY in backend/.env
   - Uses responseModalities: ["TEXT", "IMAGE"] on v1beta endpoint
   - Simple natural language prompts instead of complex 3-block structured prompts
4. **Flash 3.1 for street view** - supports thinking mode for better spatial reasoning
5. **SCHEMA prompt format** - compressed zone labels, structured prompt builder for aerial renders

### Key Architecture Decisions
- **Per-zone sequential rendering** is the highest quality approach (each zone gets its own API call with isolated mask/screenshot)
- **Per-zone mode defaults to ON** when multiple zones exist
- **Two-pass rendering**: Pass 1 = ground zones (parks, roads), Pass 2 = buildings individually
- **Clay render (Three.js)** provides spatial reference for street view renders
- **View cone with occlusion culling** for street view - buildings block zones behind them
- **Style 6 photorealistic people** chosen for card images (over watercolor, silhouettes, etc.)
- **10 render styles** in a 2x5 grid: Photo Realistic, Drone Photo, Massing Study, Site Plan, Ink Wash, Charcoal, Marker Render, Isometric, Wood Block, Water Colour
- **District Kits** system: 16 city-based archetype collections (5 Canadian + international cities)
- **City Kit as a first-class dropdown option** in all zone pickers (Buildings, Streets, Parks, Plazas)

### Data Model
- Archetype JSONs: `buildingArchetypes.json`, `streetPathArchetypes.json`, `openSpaceArchetypes.json`
- Each archetype has 4 design variants with unique shadeId, renderPrompt, facadeDetail, roofDetail, palette
- Variant images: `variant_0.png` through `variant_3.png` per archetype, variant_0 doubles as hero
- Card images at 1024x768, photorealistic Style 6, generated via `scripts/generate_card_images.py`
- Zone properties store: `{prefix}_archetype_id`, `{prefix}_archetype_label`, `{prefix}_subcategory`, `{prefix}_selected_variant_id`

### Prompt Engineering Insights
- **Simple natural prompts work best with Gemini** - the verbose 3-block structured format was abandoned
- **Containment instructions matter**: "ONLY render within the [color] polygon", "do NOT extend into other colored zones"
- **Negative prompts**: "building extending beyond footprint, people, pedestrians, human figures"
- **Camera physics** improve people quality: "shot on 35mm SLR, f/5.6, Kodak Portra 400"
- **Numerical inventory clause**: "This scene contains EXACTLY N buildings" prevents hallucinations
- **Void definition**: "Space between zones is flat, unbroken ground" prevents ghost buildings
- **Temperature 0.0** for aerial renders (precision over creativity); temperature 0.35 was tried and reverted
- **thinkingBudget** scaled by zone count: 16K (1-15 zones), 24K (16-29), 32K (30+)
- **View cone distance 150m** is the sweet spot for street view (was 200m, tried 120m)

---

## What Worked / What Failed

### What Worked
- Switching from Imagen 3 to Gemini API - massive quality improvement
- Per-zone rendering with isolated screenshots per zone
- Unique polygon colors per archetype variant - helps AI distinguish zones
- White site boundary fill as clean canvas for AI
- Clay render (Three.js) as spatial reference for street view
- Style 6 photorealistic people with camera physics prompts
- SCHEMA compressed prompt format for aerial renders
- View cone occlusion culling - buildings correctly block zones behind them
- Distance markers on clay render (orange rings at 25m, 50m, 75m, 100m)
- Edge feathering (4px blur on zone masks, 20px fade on overlay rectangle)

### What Failed / Was Abandoned
- **Imagen 3 inpainting** - too complex, poor quality, constant boundary bleeding
- **Complex 3-block structured prompts** - AI couldn't follow the verbose instructions
- **Zooming into zones for per-zone rendering** - coordinate mapping broke when viewport changed
- **Building headroom expansion** (extending clip polygon upward) - made things worse, reverted
- **Clean base screenshot approach** (hiding all zones before capture) - didn't work, reverted
- **Temperature 0.35** for aerial renders - reduced architectural precision, reverted to 0.0
- **Semantic color map for oblique aerial views** - works for top-down only, breaks at steep angles
- **responseModalities on v1 endpoint** - only works on v1beta
- **gemini-2.0-flash-exp** model - deprecated/unavailable, had to find gemini-2.5-flash-image
- **Watercolor/pencil sketch/collage render styles** initially considered for removal but user wanted to keep artistic styles
- **Flat pastel silhouettes** for people (Style 1) - replaced by Style 6 photorealistic

---

## Known Issues & Workarounds

### OneDrive Git Conflicts
- **Problem**: OneDrive syncs the `.git` folder, creating `index.lock` files that block git operations
- **Workaround**: Pause OneDrive sync, delete `.git/index.lock`, perform git operation, resume sync
- **Better fix**: Exclude `.git` folder from OneDrive sync entirely

### Variant 0 Crash Bug (FIXED)
- **Problem**: Selecting variant_0 for any archetype crashed the app
- **Root cause**: `parseInt("0") - 1 = -1`, accessing `VARIANT_SHIFTS[-1]` = undefined, destructuring crashes
- **Fix**: `Math.max(0, ...)` clamp in `resolveZoneColor` in `SitePlannerMap.tsx`

### Zone Outlines Baking into Renders
- **Problem**: Red/orange polygon borders visible in final renders
- **Fix**: Capture `originalBase64` AFTER hiding zone layers, not before

### Mask Size Mismatch (1px off)
- **Problem**: DPR rounding causes +-1px difference between mask and screenshot
- **Fix**: Generate mask FIRST (synchronous) before async screenshot capture; backend also resizes mask to match

### Site Boundary Clipping Building Tops
- **Problem**: Buildings in perspective extend above site boundary polygon, get clipped
- **Status**: Partially addressed. Expanding clip upward was reverted. Current approach: buildings render without polygon clip in per-zone mode

### Card Image Path Mismatches
- **Problem**: Generator saves to kebab-case folders but JSON uses snake_case IDs
- **Fix**: Script to update thumbnailUrl paths in all JSON files to match actual folder names

### Backend .env Location
- **Problem**: Google OAuth credentials were in root `.env` but backend reads `backend/.env`
- **Fix**: Copy credentials to `backend/.env`

### PowerShell Syntax
- `cd X && command` doesn't work in PowerShell (use semicolons or run separately)
- `uvicorn app.main:app --reload --port 8000` may need `--port=8000` syntax

### Docker Required for Full Stack
- PostgreSQL and Redis run via Docker Compose
- `docker compose up db redis` for minimal local development
- Backend needs the database running for authentication

---

## Future Roadmap Items

### Immediate / In Progress
- Complete card image generation for all archetypes (was ~2,049/~2,500+ images when last checked)
- SCHEMA + Street View metadata audit for all 121 kit archetypes
- Push district kits and card images to remote (currently local only)
- Fix remaining card generation gaps (some Canadian parks still missing)

### Short-term
- **Character reference library** - 10 fictional "City Prompt personas" created, can be used with Flash 3.1's Subject Consistency engine for close-up renders
- **Render result caching** - store successful renders so users can revisit
- **Progress streaming** - replace spinner with SSE/polling for actual progress
- **Batch zone rendering** - render individual zones at higher zoom for better detail
- **Save renders button** - missing from render modal in some views
- **Fix subcategory filtering** - some archetypes appearing in wrong development types
- **Park image cards showing identical images** - some parks have the same thumbnail

### Longer-term
- **Landing page** - Direction C "Living Map" concept built at `docs/landing.html`
- **Business launch** - user wants to create a business ("Let's make Google jealous")
- **People in site renders** - currently excluded, plan to add once core quality is solid
- **Iterative refinement** - render, upscale, re-inpaint to sharpen details
- **Suggested building footprint areas** - already has suggestedAreaSqm for 15 parks
- **Min/max floor enforcement** - soft warnings when floors outside range

---

## Key Memories to Save

### Critical Configuration
- **GCP Project**: `blissful-jet-489205-b8`
- **Gemini model for image generation**: `gemini-2.5-flash-image` (on v1beta endpoint)
- **Gemini model for street view**: Flash 3.1 with thinking mode, or Flash 2.5 without
- **Backend port**: 8000, Frontend port: 5174
- **Git remotes**: origin = `aasedor/2D-Maps`, beeman = `beemanbesh/2D-Maps2`
- **Docker needed**: PostgreSQL (port 5432) + Redis for full auth stack
- **Weekly token allowance**: bumped to 99,999 locally for development

### File Locations (Updated)
- `frontend/src/components/viewer/useAIRender.ts` - Core aerial render pipeline (~2500+ lines)
- `frontend/src/components/viewer/useStreetViewRender.ts` - Street view render with clay render, occlusion
- `frontend/src/components/viewer/StreetViewPanel.tsx` - Street view UI (7 styles, model selector)
- `frontend/src/components/viewer/SitePlannerMap.tsx` - Map rendering, zone colors, labels, interactions
- `frontend/src/components/viewer/ZonePropertiesPanel.tsx` - Zone editing, archetype selection, variant thumbnails
- `frontend/src/components/viewer/aestheticCatalog.ts` - ArchetypeVariant type, aesthetic options
- `frontend/src/data/archetypeShadeMap.ts` - 73 unique shade assignments
- `frontend/src/components/viewer/overlayArchitecturalFigures.ts` - SVG figure overlay (kept for future use)
- `frontend/public/entourage/` - 10 character persona reference images
- `scripts/generate_card_images.py` - Card image generation via Gemini API
- `scripts/create_district_kits.py` - District kit creation script
- `docs/landing.html` - Direction C landing page prototype
- `docs/QUICK_START.html` - Dark theme quick-start guide

### App Name Evolution
- Started as "SiteForge" in early sessions
- Later referred to as "City Prompt" in later sessions (possibly rebranded)

### User's Decision Patterns
- Prefers photorealistic over artistic for default renders
- Chose Style 6 photorealistic people over watercolor/silhouettes after wife consultation
- Wants professional, credible output ("Watercolour, Pencil Sketch, Collage undermine professional credibility" but then decided to keep them)
- Values spatial accuracy in street view over artistic liberty
- Prefers conservative approach: test locally, verify, then push to remote
- Pushes to both origin and beeman remotes for collaborator access
