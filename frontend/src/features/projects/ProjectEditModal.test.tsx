import '@testing-library/jest-dom/vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';
import type { Project } from '@/types';
import { ProjectEditModal } from './ProjectEditModal';

it('labels the project name and saves an edit through that field', () => {
  const onSave = vi.fn();
  render(<ProjectEditModal project={{ id: 'project', name: 'Original project' } as Project}
    isSaving={false} onClose={vi.fn()} onSave={onSave} />);

  const name = screen.getByRole('textbox', { name: /^Project Name/ });
  expect(name).toHaveValue('Original project');
  fireEvent.change(name, { target: { value: 'Renamed project' } });
  fireEvent.click(screen.getByRole('button', { name: 'Save Changes' }));

  expect(onSave).toHaveBeenCalledExactlyOnceWith({ name: 'Renamed project', description: null });
});
