import { buildLegoMassingCourtyardKitData, type LegoMassingCourtyardStyle } from './legoMassingCourtyardKit';
import { buildLegoMassingKitData, type LegoMassingKitData, type LegoMassingKitStyle } from './legoMassingGeometry';

/** One archetype's facade kit. `type` names the vocabulary it is drawn with. */
export type LegoMassingKit =
  | ({ type: 'apartment_bar' } & LegoMassingKitStyle)
  | ({ type: 'courtyard_block' } & LegoMassingCourtyardStyle);

/** Build the complete shell for an outline with the kit's own vocabulary. */
export function buildLegoMassingKit(ring: readonly number[][], centroidLng: number, centroidLat: number,
  kit: LegoMassingKit): LegoMassingKitData | null {
  return kit.type === 'courtyard_block'
    ? buildLegoMassingCourtyardKitData(ring, centroidLng, centroidLat, kit)
    : buildLegoMassingKitData(ring, centroidLng, centroidLat, kit);
}
