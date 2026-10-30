import streets from '@/data/nativeStreetPilots.json';
import bridges from '@/data/nativeBridgePilots.json';
import type { NativeStreetProgram } from './nativeStreetProgram';

type NativeModule = { sha256: string; bytes: number; url: string };
type NativeStreetSource = Omit<typeof streets[number], 'modules' | 'program'> & {
  modules: Record<string, NativeModule>;
  program?: NativeStreetProgram;
};

/** New bridge adapters remain local pilots until their exact runtime review.
 * Keep their data and modules out of production discovery and bundle payload. */
export const nativeStreetSources: NativeStreetSource[] = [...streets, ...(import.meta.env.DEV && import.meta.env.MODE === 'development' ? bridges : [])]
  .map(row => ({ ...row, modules: Object.fromEntries(Object.entries(row.modules)
    .filter((entry): entry is [string, NativeModule] => entry[1] !== undefined)) }));
