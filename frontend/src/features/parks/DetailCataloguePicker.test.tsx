import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import { DetailCataloguePicker } from './DetailCataloguePicker';

it('cannot add unvalidated curb bulbs through the arrangement editor',()=>{
  const add=vi.fn();
  render(<DetailCataloguePicker disabled={false} canAdd={()=>true} onAdd={add}/>);
  fireEvent.change(screen.getByLabelText('Detail category'),{target:{value:'Curb bulbs'}});
  const button=screen.getByRole('button');
  expect((button as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(button);
  expect(add).not.toHaveBeenCalled();
});
