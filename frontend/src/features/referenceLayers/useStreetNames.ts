import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import type { SiteZone } from '@/types';
import { getActiveSiteBoundary } from '@/utils/siteBoundary';
import { readBrowserPreference, writeBrowserPreference } from '@/utils/browserPreferences';
import { fetchStreetNames, streetNameBounds } from './streetNames';

export function useStreetNames(projectId: string | undefined, zones: SiteZone[], exploration: number[][] = []) {
  const key=`cityprompt:street-names:${projectId}`;
  const [choices,setChoices]=useState<Record<string,boolean>>({});
  const saved=useMemo(()=>readBrowserPreference(key)==='true',[key]);
  const enabled=choices[key] ?? saved;
  const bounds=streetNameBounds(getActiveSiteBoundary(zones)?.coordinates ?? exploration);
  const problem=!bounds ? 'Available for Calgary neighbourhoods. Move closer or choose a smaller site.' : null;
  const query=useQuery({
    queryKey:['street-names-v1',projectId,bounds],
    queryFn:({signal})=>fetchStreetNames(bounds!,AbortSignal.any([signal,AbortSignal.timeout(30_000)])),
    enabled:Boolean(projectId && enabled && bounds), staleTime:15*60_000,gcTime:30*60_000,retry:1,retryDelay:1000,
  });
  return { enabled, setEnabled:(next:boolean)=>{
    writeBrowserPreference(key,String(next));
    setChoices(current=>({...current,[key]:next}));
  }, data:bounds ? query.data : undefined, problem, loading:query.isFetching,error:query.error,
  retry:()=>{ if (enabled && bounds) void query.refetch(); } };
}
export type StreetNamesState=ReturnType<typeof useStreetNames>;
