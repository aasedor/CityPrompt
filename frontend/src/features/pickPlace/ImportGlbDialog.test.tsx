import '@testing-library/jest-dom/vitest';
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';
import { ImportGlbDialog } from './ImportGlbDialog';
import { PlacementPalette } from './PlacementPalette';

const { upload } = vi.hoisted(() => ({ upload: vi.fn() }));
vi.mock('@/services/api', async importOriginal => ({ ...await importOriginal<typeof import('@/services/api')>(),
  modelLibraryApi: { importGlb: upload } }));
const model = { id:'imported', project_id:'project', name:'My building', preview_url:null, model_url:'/api/v1/files/projects/project/models/a.glb',
  width_m:12, depth_m:20, height_meters:9, floor_count:null, size_estimated:false, source_kind:'imported_glb' as const };
afterEach(() => { cleanup(); vi.clearAllMocks(); });

it('puts a prominent import action directly above Walk and opens the import dialog', () => {
  render(<PlacementPalette projectId="project" selected={null} onPick={vi.fn()} onPickCanonical={vi.fn()} onPickGenerated={vi.fn()}
    onCancel={vi.fn()} onRetry={vi.fn()} status="ready" message="" primaryAction={<button>Walk</button>} />);
  const button=screen.getByRole('button',{name:'Import GLB'});
  expect(button.compareDocumentPosition(screen.getByRole('button',{name:'Walk'})) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  fireEvent.click(button);
  expect(screen.getByRole('dialog')).toBeInTheDocument();
  expect(screen.getByLabelText('GLB building file')).toHaveAttribute('accept','.glb');
});

it('uploads chosen units then hands the measured private model to click placement', async () => {
  upload.mockResolvedValue(model);const pick=vi.fn();
  render(<ImportGlbDialog projectId="project" onImported={pick} onClose={vi.fn()}/>);
  const file=new File(['glTF'],'my-building.glb');
  fireEvent.change(screen.getByLabelText('GLB building file'),{target:{files:[file]}});
  fireEvent.change(screen.getByLabelText('Model units'),{target:{value:'millimetres'}});
  fireEvent.change(screen.getByLabelText('Building name (optional)'),{target:{value:'My building'}});
  fireEvent.change(screen.getByLabelText('Building height (m, optional)'),{target:{value:'9'}});
  fireEvent.click(screen.getByRole('button',{name:'Import & place'}));
  await waitFor(()=>expect(pick).toHaveBeenCalledWith(model));
  expect(upload).toHaveBeenCalledWith('project',file,'My building','millimetres',9);
});

it('retains the selected file and units after a failed upload and allows a deliberate retry', async () => {
  upload.mockRejectedValueOnce({response:{data:{detail:'The model could not be saved. Try again.'}}}).mockResolvedValueOnce(model);
  const pick=vi.fn();render(<ImportGlbDialog projectId="project" onImported={pick} onClose={vi.fn()}/>);
  const file=new File(['glTF'],'house.glb');
  fireEvent.change(screen.getByLabelText('GLB building file'),{target:{files:[file]}});
  fireEvent.change(screen.getByLabelText('Model units'),{target:{value:'feet'}});
  fireEvent.click(screen.getByRole('button',{name:'Import & place'}));
  expect(await screen.findByRole('alert')).toHaveTextContent('could not be saved');
  expect(screen.getByLabelText('Model units')).toHaveValue('feet');
  expect(screen.getByText('house.glb')).toBeVisible();expect(pick).not.toHaveBeenCalled();
  fireEvent.click(screen.getByRole('button',{name:'Import & place'}));
  await waitFor(()=>expect(pick).toHaveBeenCalledWith(model));
});

it('blocks a wrong file type or oversized file before starting a request', () => {
  render(<ImportGlbDialog projectId="project" onImported={vi.fn()} onClose={vi.fn()}/>);
  fireEvent.change(screen.getByLabelText('GLB building file'),{target:{files:[new File(['bad'],'drawing.txt')]}});
  expect(screen.getByRole('alert')).toHaveTextContent('.glb');
  expect(screen.getByRole('button',{name:'Import & place'})).toBeDisabled();
  const huge=new File(['glTF'],'huge.glb');Object.defineProperty(huge,'size',{value:50*1024*1024+1});
  fireEvent.change(screen.getByLabelText('GLB building file'),{target:{files:[huge]}});
  expect(screen.getByRole('alert')).toHaveTextContent('50 MB');expect(upload).not.toHaveBeenCalled();
});
