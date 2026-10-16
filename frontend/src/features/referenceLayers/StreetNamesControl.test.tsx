import '@testing-library/jest-dom/vitest';
import { act, render, renderHook, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { beforeEach, expect, it, vi } from 'vitest';
import type { ReactNode } from 'react';
import { StreetNamesControl } from './StreetNamesControl';
import { useStreetNames } from './useStreetNames';
import { fetchStreetNames } from './streetNames';

vi.mock('./streetNames',async original=>({ ...await original<typeof import('./streetNames')>(),fetchStreetNames:vi.fn() }));
const area=[[-114.07,51.045],[-114.069,51.045],[-114.069,51.046]];
function wrapper({children}:{children:ReactNode}) {
  return <QueryClientProvider client={new QueryClient({defaultOptions:{queries:{retry:false}}})}>{children}</QueryClientProvider>;
}
beforeEach(()=>{ localStorage.clear(); vi.mocked(fetchStreetNames).mockReset().mockResolvedValue([{id:'1',label:'10 ST NW',anchor:[-114.07,51.045]}]); });
it('defaults off without fetching, persists per project and uses cached names', async()=>{
  const {result,rerender,unmount}=renderHook(({id})=>useStreetNames(id,[],area),{wrapper,initialProps:{id:'one'}});
  expect(result.current.enabled).toBe(false);
  expect(fetchStreetNames).not.toHaveBeenCalled();
  act(()=>result.current.setEnabled(true));
  await waitFor(()=>expect(result.current.data).toHaveLength(1));
  expect(localStorage.getItem('cityprompt:street-names:one')).toBe('true');
  act(()=>result.current.setEnabled(false));
  act(()=>result.current.setEnabled(true));
  expect(fetchStreetNames).toHaveBeenCalledTimes(1);
  rerender({id:'two'});
  expect(result.current.enabled).toBe(false);
  expect(result.current.data).toBeUndefined();
  unmount();
  const restored=renderHook(()=>useStreetNames('one',[],area),{wrapper});
  expect(restored.result.current.enabled).toBe(true);
});
it('can be operated with the keyboard and exposes loading/failure recovery', async()=>{
  const user=userEvent.setup(),setEnabled=vi.fn(),retry=vi.fn();
  const state={enabled:false,setEnabled,problem:null,loading:false,error:null,data:undefined,retry};
  const {rerender}=render(<StreetNamesControl state={state}/>);
  const toggle=screen.getByRole('switch',{name:'Street names'});
  await user.tab(); expect(toggle).toHaveFocus();
  await user.keyboard(' '); expect(setEnabled).toHaveBeenCalledWith(true);
  rerender(<StreetNamesControl state={{...state,enabled:true,loading:true}}/>);
  expect(screen.getByRole('status')).toHaveTextContent('Loading street names');
  rerender(<StreetNamesControl state={{...state,enabled:true,error:new Error('offline')}}/>);
  await user.click(screen.getByRole('button',{name:'Try again'}));
  expect(retry).toHaveBeenCalledOnce();
});
