# City Prompt Landing Page — Design Research Report

## The 5 Sites Most Worth Studying

### 1. Don't Board Me (dontboard.me) — Awwwards Users' Choice 2024
A pet-sitting service that won design awards AND is genuinely usable. Warm illustrations, clear copy, subtle animations that build trust without slowing anyone down. The jury called it "a surprising blend of great art direction, engaging copywriting, and a very practical website."
**Borrow:** Warm illustration style + clear copy + subtle motion = approachable for all ages.

### 2. Felt (felt.com) — "FigJam for Maps"
The product IS the hero. No screenshot — the interactive map is embedded directly on the landing page. Minimal chrome, white background, colorful data layers provide all the visual interest.
**Borrow:** Make the map the hero. Don't show a screenshot of the product — show the product.

### 3. Stripe (stripe.com) — The SaaS Design Benchmark
Complex financial products explained through animated demos that play on scroll. Famous gradient backgrounds. Clean information architecture handles dozens of products without overwhelm.
**Borrow:** Use animation to EXPLAIN complex concepts (zoning, density, AI rendering), not just to decorate.

### 4. Contra Project Calculator — A TOOL That Won Design Awards (CSSDA 2024)
A freelancer cost estimator that turns data into an engaging interactive experience. Proof that functional utility tools CAN win top design awards.
**Borrow:** Make data interactive and visual, not just tabular. Interactive calculations > static numbers.

### 5. GOV.UK Design System — The Accessibility Gold Standard
Pages load 2x faster. During COVID, 52 services built in weeks. 19px body text minimum. Focus states with thick yellow outlines. Principle: "This is for everyone."
**Borrow:** Focus states, progressive disclosure, content-first design, 19px+ body text.

---

## The 3 Best Hero Section Approaches for City Prompt

### Option A: Scrollytelling Map (Most Recommended)
Each scroll section reveals a planning capability, with the map updating in sync. Based on Mapbox Storytelling template + NBC News Segregation Map (Webby winner).
- Section 1: Empty satellite map → "Start with your site"
- Section 2: Zone polygons appear → "Draw your vision"
- Section 3: Archetypes apply → "Choose a character"
- Section 4: AI render overlays → "See it come to life"
The map never leaves view — it's the constant while text scrolls past.

### Option B: Interactive Mini Demo (Felt-Style)
Embed a simplified version of the actual product. Visitor can draw a zone, pick an archetype, and see a pre-generated render. Zero signup required. Product sells itself.

### Option C: Cinematic Before/After
Full-viewport before/after with a draggable slider. Left: satellite with colored zones. Right: photorealistic render. One image, instant understanding.

---

## Color Direction (Refined)

Based on research, the strongest direction for City Prompt's audience (students → seniors):

| Element | Color | Hex |
|---------|-------|-----|
| Background | Warm off-white | `#FAFAF8` |
| Cards/surfaces | White | `#FFFFFF` |
| Primary text | Near-black | `#1E293B` |
| Secondary text | Warm gray | `#64748B` |
| Primary accent | Emerald green | `#059669` |
| Secondary accent | Deep navy | `#1E293B` |
| CTA buttons | Emerald or navy | `#059669` / `#1E293B` |
| Focus states | Yellow ring (GOV.UK) | `#FFDD00` |
| Map: water | Soft blue | `#AADAFF` |
| Map: terrain | Pastel green | `#C3ECB2` |
| Warning/error | Clear red | `#DC2626` |

**Why not dark mode?** Research shows cognitive performance drops for older adults in dark mode. Community open houses use projectors in well-lit rooms — dark themes wash out. Default light, offer dark as a toggle.

---

## Typography

- **Body:** 18-20px Inter (minimum). GOV.UK uses 19px as their baseline.
- **Headings:** 700-800 weight, -0.02em letter-spacing
- **Line height:** 1.5-1.6x
- **Max line length:** 50-75 characters
- **Weights:** 400 (body), 600 (emphasis), 700-800 (headings). Never below 400.

---

## Animations That Are Safe + Premium

### Use Freely (accessible, tested)
- Intersection Observer fade-ins with staggered delays (150ms between items)
- Card hover: `translateY(-5px)` + increased shadow
- Blur-up progressive image loading (`filter: blur(20px)` → `blur(0)`)
- Color/opacity transitions on hover (120-220ms)
- Skeleton loading with shimmer for map states

### Use Carefully (test with older users)
- Before/after slider (use native `<input type="range">` for keyboard access)
- Word-by-word text reveals (keep speed comfortable)
- Glassmorphism nav bar (verify contrast against blurred background)
- `scroll-snap-type: y proximity` (never `mandatory`)

### Never Use
- Parallax scrolling (triggers vestibular disorders in 35% of adults over 40)
- Scrolljacking (hijacking native scroll)
- Auto-playing video/animation
- Letter-by-letter text splitting (breaks screen readers)
- Custom cursors that hide system cursor
- `mandatory` scroll-snap (traps users with motor impairments)
- Infinite scroll

### Required for All Animations
```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```
Plus an on-page motion toggle (many users don't know about the OS setting).

---

## Layout Techniques Worth Using

### Bento Grid
Asymmetric CSS Grid cards — sites using them report 47% higher dwell time. Great for showing different features (aerial render, street view, style gallery) at different visual weights.

### Before/After Slider
Use the `img-comparison-slider` web component (~3KB, zero deps) or native `<input type="range">` linked to a CSS variable controlling `clip-path`. Built-in keyboard support.

### Grain/Noise Texture
SVG `feTurbulence` filter at 5-20% opacity over gradients. Breaks up gradient banding, adds subtle tactile quality without hurting readability.

### Glassmorphic Nav
`backdrop-filter: blur(12px)` with solid fallback. The nav becomes semi-transparent over the map/hero, keeping the content visible while maintaining navigation access.

---

## Content Strategy

### From Award-Winning Civic Sites
- **Chesterfield.gov** reduced 4,000 pages to 400. Ruthless simplification wins.
- **Asheville SimpliCity** uses a single search bar as the primary interface.
- **SacRT** uses infographics for complex data, simple language throughout.

### For City Prompt's Landing Page
- Write at 6th-8th grade reading level
- Organize by user intent ("I want to..."), not by features
- One CTA above the fold — not two
- No jargon: "neighbourhood styles" not "architectural archetypes"
- Show the product, don't describe it
- Every section should answer: "Why should I care?"

---

## Accessibility Non-Negotiables

From GOV.UK + Helsinki + Singapore design award winners:

1. 4.5:1 contrast ratio minimum (aim for 7:1 per WCAG AAA)
2. Visible focus states (GOV.UK yellow ring: `outline: 3px solid #FFDD00`)
3. `prefers-reduced-motion` respected globally
4. Keyboard-navigable throughout
5. No information conveyed by color alone
6. Touch targets: 44x44px minimum (not the WCAG minimum of 24x24)
7. Progressive disclosure — don't overwhelm on first load
8. On-page motion toggle in addition to OS preference
9. `aria-label` on all interactive elements
10. Test with NVDA, VoiceOver, keyboard-only, and high-contrast mode

---

## Key Insight

The sites that win awards AND serve broad audiences (Don't Board Me, Stripe, Notion, GOV.UK, Chesterfield.gov) share one principle:

**Animate to communicate, not to impress.**

Every transition confirms an action, guides attention, or reveals information. Nothing moves just because it can. This is the 2026 design standard — meaningful motion over decorative motion.

For City Prompt: the map transforming from zones to a photorealistic render IS the animation. That's the magic moment. Everything else on the landing page exists to get visitors to that moment as fast as possible.
