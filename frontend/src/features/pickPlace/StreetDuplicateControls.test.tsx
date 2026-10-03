import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { it, expect, vi } from 'vitest';
import { StreetDuplicateControls } from './StreetDuplicateControls';

it('cancels without writing and keeps a rejected copy editable',async()=>{
  const copy=vi.fn().mockRejectedValue(new Error('Keep the copy inside the site.'));
  render(<StreetDuplicateControls disabled={false} width={18} onDuplicate={copy}/>);
  fireEvent.click(screen.getByRole('button',{name:'Duplicate street'}));
  fireEvent.click(screen.getByRole('button',{name:'Cancel copy'}));
  expect(copy).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Duplicate street'}));
  fireEvent.change(screen.getByLabelText('East offset (m)'),{target:{value:'60'}});
  fireEvent.click(screen.getByRole('button',{name:'Create copy'}));
  await waitFor(()=>expect(screen.getByRole('alert').textContent).toContain('Keep the copy inside the site.'));
  expect(copy).toHaveBeenCalledExactlyOnceWith(60,0);
  expect((screen.getByLabelText('East offset (m)') as HTMLInputElement).value).toBe('60');
  expect((screen.getByRole('button',{name:'Create copy'}) as HTMLButtonElement).disabled).toBe(false);
});
