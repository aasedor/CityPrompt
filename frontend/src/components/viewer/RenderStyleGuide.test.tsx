import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { RenderStyleGuide } from './RenderStyleGuide';
import { RenderStyleGuideButton } from './RenderStyleGuideButton';
import { RENDER_STYLE_DIRECTIONS, renderStyleDirection } from './renderStyleGuideData';
import { STYLES } from './globe/imageStyles';

const props = {styles:STYLES,selectedStyle:'photorealistic',onStyle:vi.fn(),onClose:vi.fn()};
afterEach(() => { cleanup(); vi.clearAllMocks(); });

it('describes all established styles and preserves street aliases without implying survey certification', () => {
  for (const style of STYLES) expect(renderStyleDirection(style.id)?.summary.length).toBeGreaterThan(20);
  expect(renderStyleDirection('clay-model')).toBe(RENDER_STYLE_DIRECTIONS['clay-maquette']);
  expect(renderStyleDirection('human-scale')?.summary).toContain('people control');
  expect(renderStyleDirection('survey')?.goodFor).toContain('not a measured survey');
  expect(renderStyleDirection('missing-style')).toBeUndefined();
});

it('opens existing samples on demand without changing the current style', async () => {
  const {container}=render(<RenderStyleGuideButton {...props} />);
  expect(container.querySelectorAll('img')).toHaveLength(0);
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:'Compare styles & examples'}));
  await screen.findByRole('dialog',{name:'Render style guide'});
  expect(screen.getByText('Current render style: Photo Realistic')).toBeInTheDocument();
  expect(screen.getByRole('combobox',{name:'Explore a style'})).toHaveValue('photomontage');
  expect(screen.getByAltText('Photomontage saved image example')).toHaveAttribute('loading','lazy');
  expect(screen.getAllByRole('img')).toHaveLength(1);
  expect(props.onStyle).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Close render style guide'}));
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});

it('applies an exact style only after explicit selection and closes the guide', () => {
  render(<RenderStyleGuide {...props} />);
  fireEvent.click(screen.getByRole('button',{name:'View Watercolour'}));
  expect(props.onStyle).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Use this style · Watercolour'}));
  expect(props.onStyle).toHaveBeenCalledExactlyOnceWith('watercolour');
  expect(props.onClose).toHaveBeenCalledOnce();
});

it('retains caller availability gates and explains them while allowing preview', () => {
  render(<RenderStyleGuide {...props} isStyleDisabled={id=>id==='development'} styleHint={id=>id==='development'?'Place 3D buildings first.':undefined} />);
  fireEvent.change(screen.getByRole('combobox',{name:'Explore a style'}),{target:{value:'development'}});
  expect(screen.getByRole('button',{name:'Use this style · Development'})).toBeDisabled();
  fireEvent.click(screen.getByRole('button',{name:'Use this style · Development'}));
  expect(props.onStyle).not.toHaveBeenCalled();
  expect(screen.getByRole('status')).toHaveTextContent('Place 3D buildings first.');
});

it('loads the correct original source only on request and resets comparison on style change', () => {
  render(<RenderStyleGuide {...props} selectedStyle="watercolour" />);
  expect(screen.getAllByRole('img')).toHaveLength(1);
  fireEvent.click(screen.getByRole('button',{name:'Show original 3D view'}));
  expect(screen.getByAltText('Watercolour example: original 3D source')).toHaveAttribute('src','/render-style-examples/watercolour-source.png');
  fireEvent.click(screen.getByRole('button',{name:'View Charcoal'}));
  expect(screen.queryByAltText('Watercolour example: original 3D source')).not.toBeInTheDocument();
  expect(screen.getAllByRole('img')).toHaveLength(1);
  expect(screen.getByText(/Closer building view/)).toBeInTheDocument();
});

it('compares street examples without relabelling charcoal or applying a style', () => {
  render(<RenderStyleGuide {...props} selectedStyle="charcoal" />);
  fireEvent.click(screen.getByRole('button',{name:'Compare street examples'}));
  expect(screen.getByAltText('Photomontage street comparison example')).toBeInTheDocument();
  expect(screen.getByAltText('Watercolour street comparison example')).toBeInTheDocument();
  expect(screen.queryByAltText('Charcoal saved image example')).not.toBeInTheDocument();
  expect(screen.getByText(/source captures differ slightly/)).toBeInTheDocument();
  expect(props.onStyle).not.toHaveBeenCalled();
});

it('distinguishes projection changes, including the existing street clay alias', () => {
  render(<RenderStyleGuide {...props} styles={[...STYLES,{id:'clay-model',label:'Street clay'}]} />);
  fireEvent.change(screen.getByRole('combobox',{name:'Explore a style'}),{target:{value:'clay-model'}});
  expect(screen.getByText(/Changes the camera projection/)).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:'View Watercolour'}));
  expect(screen.queryByText(/Changes the camera projection/)).not.toBeInTheDocument();
});

it('keeps selection available after a missing image and permits Escape dismissal', () => {
  render(<RenderStyleGuide {...props} selectedStyle="charcoal" />);
  fireEvent.error(screen.getByAltText('Charcoal saved image example'));
  expect(screen.getByRole('status')).toHaveTextContent('could not load');
  expect(screen.getByRole('button',{name:'Use this style · Charcoal'})).toBeEnabled();
  fireEvent.keyDown(document,{key:'Escape'});
  expect(props.onClose).toHaveBeenCalledOnce();
  expect(props.onStyle).not.toHaveBeenCalled();
});
