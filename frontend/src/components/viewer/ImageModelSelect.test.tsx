import '@testing-library/jest-dom/vitest';
import {render,screen,fireEvent} from '@testing-library/react';
import {expect,it,vi} from 'vitest';
import {ImageModelSelect} from './ImageModelSelect';

it('offers only supported cloud engines, keeping retired local engines out of new renders',()=>{
  render(<ImageModelSelect value="gpt-image-2" onChange={vi.fn()} availability={null}/>);
  expect(screen.queryAllByRole('option',{name:/FLUX|Qwen|Wan|Local/})).toHaveLength(0);
  expect(screen.getByRole('option',{name:/^Sunburst/})).toBeInTheDocument();
});

it('offers Nano Banana independently of OpenAI and emits its exact model ID',()=>{
  const change=vi.fn();
  render(<ImageModelSelect value="gpt-image-2" onChange={change}
    availability={{default_model:'gpt-image-2',models:[{id:'gpt-image-2',available:false},{id:'gemini-nano-banana-2.1',available:true}]}}/>);
  expect(screen.getByRole('option',{name:/Nano Banana 2.1/})).toBeEnabled();
  fireEvent.change(screen.getByRole('combobox'),{target:{value:'gemini-nano-banana-2.1'}});
  expect(change).toHaveBeenCalledWith('gemini-nano-banana-2.1');
});
it('keeps Google unavailable until the backend advertises its configuration',()=>{
  render(<ImageModelSelect value="gpt-image-2" onChange={vi.fn()} availability={null}/>);
  expect(screen.getByRole('option',{name:/Nano Banana 2.1/})).toBeDisabled();
});
