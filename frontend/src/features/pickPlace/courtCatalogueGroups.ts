import { SAVED_OPENSPACE_AESTHETIC_OPTIONS } from '@/components/viewer/aestheticCatalog';
import type { CanonicalChoice } from './canonicalCatalogue';

const SPORTS = [
  { parent: 'basketball_court', label: 'Basketball court', aliases: ['basketball_court', 'court_only_basketball'] },
  { parent: 'tennis_court_cluster', label: 'Tennis court', aliases: ['tennis_court_cluster', 'student_tennis_garden', 'court_only_tennis'] },
  { parent: 'pickleball_courts', label: 'Pickleball court', aliases: ['pickleball_courts', 'student_pickleball_garden', 'court_only_pickleball'] },
  { parent: 'beach_volleyball_courts', label: 'Beach volleyball court', aliases: ['beach_volleyball_courts', 'court_only_beach_volleyball'] },
];

/** Discovery groups exact choices; native saved identities and model bindings
 * remain the registry objects. Only available variants enter the grouped card. */
export function groupCourtCatalogueChoices(choices: CanonicalChoice[]): CanonicalChoice[] {
  const output = [...choices];
  for (const sport of SPORTS) {
    const members = output.filter(choice => choice.domain === 'park_plaza' && sport.aliases.includes(choice.option.id));
    if (!members.length) continue;
    const placements = [...new Map(members.flatMap(choice => choice.placements).map(asset => [asset.id, asset])).values()];
    const variants = [...new Map(members.flatMap(choice => choice.option.variants ?? []).map(variant => [variant.id, variant])).values()];
    const first = members.find(choice => !choice.option.id.startsWith('court_only_')) ?? members[0];
    const source = SAVED_OPENSPACE_AESTHETIC_OPTIONS.find(option => option.id === sport.parent);
    const grouped: CanonicalChoice = { ...first, id: `park_plaza:${sport.parent}`, groupedVariants: true, placements,
      option: { ...source, ...first.option, id: sport.parent, label: sport.label, variants } };
    const index = output.indexOf(members[0]);
    output.splice(index, 0, grouped);
    for (const member of members) output.splice(output.indexOf(member), 1);
  }
  return output;
}
