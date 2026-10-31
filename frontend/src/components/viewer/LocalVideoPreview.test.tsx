import '@testing-library/jest-dom/vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {afterEach,beforeEach,expect,it,vi} from 'vitest';
import {LocalVideoPreview} from './LocalVideoPreview';

const BrowserURL=URL;
const create=vi.fn(), revoke=vi.fn();
beforeEach(()=>{
  create.mockReset().mockReturnValueOnce('blob:first').mockReturnValueOnce('blob:second');revoke.mockReset();
  vi.stubGlobal('URL',class extends BrowserURL {static createObjectURL=create;static revokeObjectURL=revoke;});
});
afterEach(()=>{cleanup();vi.unstubAllGlobals();});

it('plays and downloads the same decoded Blob, releasing replaced and unmounted resources',()=>{
  const view=render(<LocalVideoPreview source="data:video/mp4;base64,Z3VpZGU=" mimeType="video/mp4"/>);
  expect(screen.getByLabelText('Local route preview')).toHaveAttribute('src','blob:first');
  expect(screen.getByRole('link',{name:'Download preview'})).toHaveAttribute('href','blob:first');
  expect(create.mock.calls[0][0]).toMatchObject({type:'video/mp4',size:5});
  view.rerender(<LocalVideoPreview source="data:video/mp4;base64,bmV3" mimeType="video/mp4"/>);
  expect(screen.getByLabelText('Local route preview')).toHaveAttribute('src','blob:second');
  expect(revoke).toHaveBeenCalledWith('blob:first');
  view.unmount();expect(revoke).toHaveBeenCalledWith('blob:second');
});

it('makes playback failure visible and keeps the downloadable file available',()=>{
  render(<LocalVideoPreview source="data:video/mp4;base64,Z3VpZGU=" mimeType="video/mp4"/>);
  fireEvent.error(screen.getByLabelText('Local route preview'));
  expect(screen.getByRole('alert')).toHaveTextContent(/cannot play.*download/i);
  expect(screen.getByRole('link',{name:'Download preview'})).toHaveAttribute('href','blob:first');
});
