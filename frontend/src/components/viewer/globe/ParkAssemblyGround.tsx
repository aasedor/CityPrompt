import { createContext, useCallback, useContext, useLayoutEffect, useMemo, useState, type ReactNode } from 'react';
import type { SiteZone } from '@/types';

type Owner = Pick<SiteZone, 'id' | 'updated_at' | 'coordinates'>;
type Register = (owner: Owner) => () => void;
const RegisterContext = createContext<Register>(() => () => {});
const OwnersContext = createContext<readonly Owner[]>([]);

/** Only a mounted, loaded assembly may replace the generic ground. Suspension,
 * an asset failure, LOD removal or a stale revision restores the fallback. */
export function ParkAssemblyGroundProvider({ children }: { children: ReactNode }) {
  const [owners, setOwners] = useState<readonly Owner[]>([]);
  const register = useCallback<Register>((owner) => {
    const entry = { ...owner };
    setOwners(previous => [...previous.filter(item => item.id !== entry.id), entry]);
    return () => setOwners(previous => previous.filter(item => item !== entry));
  }, []);
  return <RegisterContext.Provider value={register}>
    <OwnersContext.Provider value={owners}>{children}</OwnersContext.Provider>
  </RegisterContext.Provider>;
}

export function useOwnParkAssemblyGround(zone: Owner) {
  const register = useContext(RegisterContext);
  const { id, updated_at, coordinates } = zone;
  useLayoutEffect(() => register({ id, updated_at, coordinates }), [register, id, updated_at, coordinates]);
}

export function useParkAssemblyGroundOwners(zones: SiteZone[]) {
  const owners = useContext(OwnersContext);
  return useMemo(() => zones.filter(zone => owners.some(owner =>
    owner.id === zone.id && owner.updated_at === zone.updated_at
    && JSON.stringify(owner.coordinates) === JSON.stringify(zone.coordinates))), [owners, zones]);
}
