import { useRef, useState } from 'react';
import { FileDown } from 'lucide-react';
import toast from 'react-hot-toast';
import { api } from '@/services/api';

export function ProjectPdfDownloadButton({ projectId }: { projectId: string }) {
  const [busy, setBusy] = useState(false);
  const pending = useRef(false);
  const download = async () => {
    if (pending.current) return;
    pending.current = true;
    setBusy(true);
    try {
      const { data } = await api.get<Blob>(`/api/v1/reports/projects/${projectId}/report`, { responseType: 'blob' });
      const url = URL.createObjectURL(data);
      const link = document.createElement('a');
      link.href = url;
      link.download = `cityprompt-${projectId}-report.pdf`;
      document.body.appendChild(link);
      try { link.click(); } finally {
        link.remove();
        window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
      }
    } catch {
      toast.error('Could not download the project PDF. Please try again.');
    } finally {
      pending.current = false;
      setBusy(false);
    }
  };
  return <button type="button" onClick={() => void download()} disabled={busy} className="btn-secondary shrink-0">
    <FileDown size={16} className="mr-2" aria-hidden />
    {busy ? 'Downloading PDF…' : 'Download project PDF'}
  </button>;
}
