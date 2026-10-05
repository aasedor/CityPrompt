export interface RenderStyleOption { id: string; label: string }
interface StyleDirection { summary: string; goodFor: string }

/** Reader-facing descriptions of the established treatments. These are not
 * provider prompts, new style definitions or guarantees of design fidelity. */
export const RENDER_STYLE_DIRECTIONS: Readonly<Record<string, StyleDirection>> = {
  photorealistic: {summary:'Natural daylight, readable materials and restrained photographic detail.', goodFor:'Showing what the proposed place could feel like.'},
  photomontage: {summary:'A photographic finish that brings the proposal and its real surroundings into one coherent image.', goodFor:'Discussing a proposal in its neighbourhood context.'},
  development: {summary:'Clean materials, crisp entrances and bright daylight give the existing design a newly finished appearance.', goodFor:'A polished development presentation.'},
  atmospheric: {summary:'Warm late-day light, soft haze and layered shadows give the scene a quieter, cinematic mood.', goodFor:'Explaining the atmosphere of a place.'},
  winter: {summary:'Cold daylight, snow and seasonal planting show the existing place in winter.', goodFor:'Considering how a community feels in a colder season.'},
  night: {summary:'Blue-hour sky and a restrained glow from existing windows and lights.', goodFor:'An evening character study.'},
  watercolour: {summary:'Transparent washes, warm paper, pigment texture and selective brush edges. Material colours become a restrained painted palette.', goodFor:'An inviting concept presentation with a visible hand-painted character.'},
  charcoal: {summary:'Monochrome strokes, rubbed tones and lifted paper highlights reveal form, depth and shadow.', goodFor:'Comparing massing and architectural character without colour.'},
  'marker-render': {summary:'Precise ink outlines with broad, directional marker strokes and clear colour blocks.', goodFor:'A legible architectural presentation with a lively drawn finish.'},
  'pen-and-ink': {summary:'Fine linework, varied line weights and cross-hatching on cream paper.', goodFor:'Explaining edges, openings and the rhythm of a street.'},
  survey: {summary:'Even neutral light, clear detail and an undramatic photographic treatment.', goodFor:'Reviewing visible architectural relationships. This is an image style, not a measured survey.'},
  documentary: {summary:'Calm everyday photography, restrained colours and natural surface variation.', goodFor:'A grounded account of the proposed place.'},
  'site-plan': {summary:'A clean orthographic plan looking straight down, with readable buildings, paths and open space.', goodFor:'Discussing site organisation from above.'},
  'site-plan-photo': {summary:'A photographic overhead view that retains material and landscape texture.', goodFor:'An overhead presentation with a photographic finish.'},
  blueprint: {summary:'White drafted linework on a blue ground, with a strict top-down plan composition.', goodFor:'A graphic plan study. It is not a construction drawing.'},
  'site-plan-watercolor': {summary:'An overhead plan with transparent colour washes and paper texture.', goodFor:'A softer, illustrated account of the site layout.'},
  isometric: {summary:'Parallel architectural projection, matte colour and clear edges show the composition as a three-dimensional diagram.', goodFor:'Explaining how buildings and open spaces fit together.'},
  'clay-maquette': {summary:'A monochrome white scale-model treatment, with soft studio shadows that describe volume.', goodFor:'Discussing massing and spatial relationships.'},
  woodblock: {summary:'Bold carved outlines, flat restrained colours and a visible printed grain.', goodFor:'A strong graphic poster with a tactile print character.'},
  collage: {summary:'Layered paper, cut photographic textures and restrained colour blocks.', goodFor:'A presentation that emphasises material character and a visual narrative.'},
  risograph: {summary:'Two or three spot inks, halftone dots and uneven ink texture on warm paper. Small ink offsets stay within surfaces.', goodFor:'A distinctive limited-colour print or presentation board.'},
  'pixel-art': {summary:'A limited palette, uniform square pixels, selective outlines and patterned dithering.', goodFor:'A playful graphic account of the community.'},
  'human-scale': {summary:'Everyday street photography with calm natural light and human proportions. The people control still governs entourage.', goodFor:'Discussing the experience of the street at eye level.'},
};

export function renderStyleDirection(id: string): StyleDirection | undefined {
  return RENDER_STYLE_DIRECTIONS[id === 'clay-model' ? 'clay-maquette' : id];
}

export const RENDER_STYLE_EXAMPLES = [
  {id:'photomontage',label:'Photomontage',view:'Street view',image:'/render-style-examples/photomontage-output.png',source:'/render-style-examples/photomontage-source.png'},
  {id:'watercolour',label:'Watercolour',view:'Street view',image:'/render-style-examples/watercolour-output.png',source:'/render-style-examples/watercolour-source.png'},
  {id:'charcoal',label:'Charcoal',view:'Closer building view',image:'/render-style-examples/charcoal-output.png',source:'/render-style-examples/charcoal-source.png'},
] as const;

export interface RenderStyleGuideProps {
  styles: readonly RenderStyleOption[]; selectedStyle: string;
  onStyle: (id: string) => void;
  isStyleDisabled?: (id: string) => boolean;
  styleHint?: (id: string) => string | undefined;
}
