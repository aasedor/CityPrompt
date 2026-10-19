# Independent holistic review: clay-georgian-terrace-house v005 (RLASM v6.1)

Reviewer: independent, no relationship with the builder. I judged rendered pixels only, against the three locked sources (`sources/front.png`, `sources/oblique.jpg`, `sources/top.jpg`). I opened all 18 renders and the 4 phone boards at full resolution. I made zoomed crops into a new folder, `/tmp/claude-0/-home-user-CityPrompt/18c9e177-8a96-5987-8fce-7444c75d018c/scratchpad/georg-v005-review-crops-2767316992/`, and sampled pixel values there. I did not read or rely on metadata, counts, hashes or builder notes.

## 1. Verdict

**VISUAL_REWORK_REQUIRED**: the v004 lantern finding is now fixed in the pixels. A new contact defect remains: an open, pure-black slot where the east rear extension meets the north-east corner of the main house. It shows in five views and blocks production approval.

Counts: P0 = 0, P1 = 1, P2 = 9

## 2. Findings table

| # | severity | view(s) | symptom (what the pixels show) | likely cause | finite fix |
|---|---|---|---|---|---|
| 1 | P1 | east_side (clearest, x≈1268–1282, y≈915–1080), right_side (x≈824–827, y≈660–720), front_corner (x≈1012–1020, y≈640–780), aerial (x≈975–985, y≈600–690), rear_side (extension SE corner) | A straight vertical slot of pure black (sampled RGB 0–1, no shading gradient) runs from the extension's coping down to the ground. It sits where the east rear extension meets the main house's east wall. It is about 0.15 m wide and full extension height. Above the extension coping, the main house's east wall continues out to the corner. Below the coping, that strip of wall is missing, so the slot exposes unlit void. It is not the downpipe: the real downpipe samples about RGB 44,46,50, is shaded and has a different profile. In the whole-envelope views it reads as a crack between two walls. | The main house east wall is trimmed back at its NE corner below extension-coping height, or the extension wall stops short of the main wall. Either way the junction is not closed, and the camera looks into the gap or unlit interior. | Close the junction. Run the brick of the main house's east wall full-width to the NE corner down to the plinth, or extend the extension's east wall and its south return to butt the main wall with a shared coping return. Then re-render east_side, right_side, front_corner, aerial and rear_side and confirm no near-black pixels at the junction. If the intent was a downpipe, model a round pipe in the downpipe material, standing off the wall, with a hopper and shoe. |
| 2 | P2 | chimney_stacks (x≈870–905, y≈440–455), roof_lead (x≈900–920, y≈240–250; x≈130, y≈575), architecture_close (x≈965, y≈180), left_side (x≈720, y≈270) | Hairline black lines cut across the parapet coping at the NE rear corner, with a small black tick on the west parapet. | The coping pieces butt with a tiny gap that shows void. | Mitre or overlap the coping segments at the corners. |
| 3 | P2 | front | One east chimney pot touches the top edge of the frame (pot-coloured pixels at y = 0), so its top is clipped by a few pixels. The building is otherwise fully legible. | Tight framing with very low camera height. | Add about 5% headroom, or lower the target slightly in the frame. |
| 4 | P2 | doorcase_balconette, front_corner, facade_close | The balconette is a single flat front panel with two thin diagonal stays splayed out at its ends. In the oblique source the balconette is a shallow box with short side returns back to the wall. | Simplified railing assembly. | Add short side-return railing panels from the front rail back to the wall. Drop or hide the splayed stays. |
| 5 | P2 | rear_north, rear, rear_side, right_side | The lantern's north slope glass is mid blue-grey (about RGB 99,114,127) and the glazing bars read light silver. The source lantern glass is darker (about RGB 55,70,85). In top, the south slope is correctly dark (about 49,53,55). | The glass material is a little too light in diffuse light. | Optionally darken the glass about 20–30% and take the bars toward lead grey. |
| 6 | P2 | rear, rear_side, left_side | The neighbour context block has completely blank rear and east-gable faces and a hipped roof at both ends, so it reads as a box rather than a continuing stuccoed terrace. | Low-detail context massing. | Add rear sash openings and run the terrace roof on to the west, or crop the context out of the rear views. |
| 7 | P2 | front_corner, right_side, aerial | The east boundary wall of the side passage is plain. The oblique and front sources show a timber gate at the passage end and boundary. The west garden gate between house and neighbour is present. | Gate omitted on the east boundary. | Add a simple dark timber gate panel in the east passage wall or across the passage's rear end. |
| 8 | P2 | roof_lead, top, left_side | The lead flat has no small vents or upstands (the source top shows several). The two west stacks carry 3 pots each, against about 3–4 in the source. | Roof furniture simplified. | Add 2–3 small vent upstands and one more pot on the middle west stack. |
| 9 | P2 | front, aerial, mansard_dormers | The mansard slate is light blue-grey against the source's dark slate. Dormer caps are flat slabs with a white edge, against the small hipped lead caps in the oblique. | Palette lifted for clay, and a simplified dormer cap. | Darken the slate tone a step and give the dormer caps a slight hip. |

There are no P0 findings.

## 3. Source conformance checklist

| item | status | view(s) used | note |
|---|---|---|---|
| Silhouette | conforms | front, front_corner, aerial vs front/oblique | Three-storey block, mansard behind the parapet, east party parapet stepping up the mansard profile with the stack on it, lower neighbour to the west. |
| Storey count and bay rhythm | conforms | front, facade_close | Three brick storeys plus a mansard. Five even bays, with the door and French window on the centre axis. |
| Brick and joints | conforms (clay) | glass_close, facade_close | Warm yellow-tan brick with faint coursing lines. Untextured, as clay allows. |
| Sashes (sizes per floor, bars, sills, flat arches) | conforms | facade_close, glass_close, architecture_close, interior | Six-over-six white sashes. First floor tallest, second floor shortest. Projecting stone sills. Splayed flat arches above each opening. Reveals read in the oblique views and in interior. |
| Doorcase (pilasters, frieze, fanlight, door) | conforms | doorcase_balconette, front_corner | Stone pilasters with caps, frieze or entablature, a three-light rectangular fanlight, a black four-panel door in a reveal, and a stone step. |
| French window and balconette | conforms (P2 #4) | facade_close, doorcase_balconette, interior | Floor-length centre French window. Black iron balconette standing on the doorcase cornice. It has no side returns. |
| String course and plinth | conforms | front, facade_close, front_corner, east_side | Stone string course at first-floor level, returning down the east wall. Projecting brick plinth. |
| Parapet and coping | conforms (P2 #2) | facade_close, mansard_dormers, roof_lead | Short brick parapet with white stone coping. Hairline coping gaps at the corners. |
| Mansard (pitch, slate, dormers) | conforms (P2 #9) | mansard_dormers, aerial, front | Steep lower slope with a shallower upper slope. Five evenly spaced dormers with slate cheeks. The tone is lighter than the source. |
| Lead flat and skylight | conforms (P2 #8) | roof_lead, top | Flat lead behind the mansard with a roll, and a skylight kerb at the west rear, matching the source top. |
| Side parapets and chimney stacks with pots | conforms | chimney_stacks, roof_lead, top, left_side | Coped side parapets. Two west stacks and one east stack, matching the plan positions in the top view. Rows of terracotta pots, five on the east stack. |
| Side wall windows | conforms | right_side, east_side, front_corner | One axis of sashes on the east wall at all three floors, with flat arches and sills, as in the source front and oblique. |
| Passage | conforms | top, front_corner, aerial | A paved side passage on the east between the house and the boundary wall, with a pier at the street. |
| Garden walls and gate | conforms on the west, deviates on the east (P2 #7) | facade_close, front, rear | West garden wall with pier and gate panel between house and neighbour. East timber gate missing. |
| Lamp | conforms | front, front_corner, aerial, top | Black lamp standard on the pavement by the east corner. |
| Tree | conforms | front, front_corner, aerial, top | Plane tree on the pavement in front of the west neighbour, at a similar height. |
| Neighbour terrace | conforms at the front, simplified at the rear (P2 #6) | front, aerial, rear | Lower terrace with white stucco ground floor, sashes above and a slate roof with dormers. Blank rear and gable faces. |
| Rear hipped wing and east lantern extension | conforms | top, rear, rear_side, rear_north, left_side, right_side | West wing with a pyramid hipped roof inside its stone rim. The east extension carries a long, closed, hipped glazed lantern with hip lines that fills the rim, matching the source top. The junction with the house has the slot in P1 #1. |
| Materials hierarchy | conforms | all | Brick (warm tan), stone dressings (white), slate and lead (blue-grey), sashes (white), door, railings and lamp (black), pots (terracotta). |

## 4. Camera validity

- **front:** valid. One chimney pot top is clipped by about 2 px at the top edge (P2 #3). The perspective is very low and close, with strong vertical convergence, but the whole façade is legible.
- **front_corner, aerial:** valid. The whole envelope is in frame. The context neighbour's pots touch the top of aerial, which is context only.
- **top:** valid. True plan view, with everything in frame.
- **left_side:** valid but compromised. The neighbour's roof fills about 40% of the lower foreground and hides the lower walls of the west face and wing. The target stays legible above it (west and rear faces, stacks, wing, lantern end).
- **right_side, rear, rear_side:** valid. The subject is small in frame but fully legible.
- **Detail views** (facade_close, architecture_close, glass_close, doorcase_balconette, mansard_dormers, chimney_stacks, east_side, roof_lead, interior, rear_north): valid. Their crops are intentional, and each frames its named target clearly.
- None of the views is invalid. No target is occluded, clipped or illegible to a degree that changes the verdict.

## 5. Previous-version finding (v004 P1: east rear extension glazed lantern)

**Resolved in the pixels.** I checked each view the brief names:

- **top:** One closed, long, hipped solid fills about 90% of the area inside the stone rim. The ridge runs east-west, with four clear hip lines running to the corners. The south slope glazing is dark (about RGB 49,53,55) and the north slope is blue-grey. Slim bars lie on the planes, including jack bars into the hips. It is no longer an undersized grid box. It matches the source top's dark, long, hipped glazed roof with hip lines.
- **rear and rear_north:** A low hipped glazed roof with sloping hip ends at both sides and a horizontal ridge. It sits on a low kerb inside the coping. The bars lie on the glass. There are no vertical end frames, fins or crate reading.
- **rear_side:** It reads clearly as a closed hipped glass roof with hips, ridge, bars and kerb, filling the rim.
- **left_side:** The west hip end shows a sloping glazed plane with bars. Nothing stands clear of the glass.
- **right_side:** The east hip triangle and long slope read as glass with bars on the planes.

Also from v004: the wing parapet and the grey roof inside the rim are still correct (top, rear_side, left_side).

The finding that keeps v005 from passing is new: P1 #1, the open slot at the junction of the east extension and the main house. It is a finite fix. The candidate cannot be signed off as PASS_ZERO_P0_P1 until that junction is closed and re-rendered.
