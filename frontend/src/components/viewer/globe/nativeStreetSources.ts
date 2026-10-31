import streets from '@/data/nativeStreetPilots.json';
import { nativeBridgeSources } from './nativeBridgeSources';
import type { NativeStreetProgram } from './nativeStreetProgram';

type NativeModule = { sha256: string; bytes: number; url: string };
type NativeStreetSource = Omit<typeof streets[number], 'modules' | 'program'> & {
  modules: Record<string, NativeModule>;
  program?: NativeStreetProgram;
};

/** The bridge receipt supplies reviewed production profiles. Held bridge data
 * and modules remain outside production discovery and bundle payload. */
export const nativeStreetSources: NativeStreetSource[] = [...streets, ...nativeBridgeSources]
  .map(row => ({ ...row, program:row.program as NativeStreetProgram, modules: Object.fromEntries(Object.entries(row.modules)
    .filter((entry): entry is [string, NativeModule] => entry[1] !== undefined)) }));
