/**
 * CustomStyleEditor — editor for "Custom" zones where the user defines their
 * vision with a free-text prompt and uploaded reference photos / PDFs instead
 * of picking a catalog archetype.
 *
 * - Photos become Gemini reference images at render time (max 3 used).
 * - PDF text (extracted server-side) feeds the LLM prompt expansion.
 * - "Generate detailed description" calls POST /api/v1/custom-style/expand and
 *   caches the result on the zone; the user can edit it or regenerate.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import type { CustomStyleAttachment, CustomStyleDomain, SiteZone, SiteZoneProperties } from '@/types';
import { customStyleApi, documentsApi, resolveApiFileUrl } from '@/services/api';

const MAX_ATTACHMENTS = 6;
const MAX_RENDER_PHOTOS = 3;
const ACCEPTED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'pdf'];

const labelClass = 'block text-[10px] font-black uppercase text-[#151515]/55';
const fieldClass = 'mt-0.5 w-full rounded-lg border-2 border-[#151515] bg-white px-2.5 py-1.5 text-sm font-semibold text-[#151515] shadow-[2px_2px_0_0_rgba(21,21,21,0.2)] focus:bg-[#fff9ec] focus:outline-none focus:ring-2 focus:ring-[#c9ff3d]';
const textareaClass = `${fieldClass} resize-none font-medium`;

/** Stable hash of the expansion inputs — detects when the cached expansion is stale. */
export function computeExpansionHash(prompt: string, pdfDocumentIds: string[]): string {
  const input = `${prompt.trim()}::${[...pdfDocumentIds].sort().join(',')}`;
  let hash = 5381;
  for (let i = 0; i < input.length; i++) {
    hash = ((hash * 33) ^ input.charCodeAt(i)) >>> 0;
  }
  return hash.toString(16);
}

const DOMAIN_PLACEHOLDER: Record<CustomStyleDomain, string> = {
  building: 'e.g. A cluster of low timber eco-lodges with green roofs around a central pond, cedar cladding, big overhangs...',
  open_space: 'e.g. A naturalized stormwater park with boardwalks, native prairie grasses, and a small amphitheatre...',
  street: 'e.g. A curbless woonerf shared street with granite pavers, staggered planters, and catenary lighting...',
};

interface CustomStyleEditorProps {
  domain: CustomStyleDomain;
  zone: SiteZone;
  props: SiteZoneProperties;
  setProps: React.Dispatch<React.SetStateAction<SiteZoneProperties>>;
  areaSqm?: number;
}

export function CustomStyleEditor({ domain, zone, props, setProps, areaSqm }: CustomStyleEditorProps) {
  const [uploading, setUploading] = useState(false);
  const [expanding, setExpanding] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [docStatuses, setDocStatuses] = useState<Record<string, string>>({});
  const fileInputRef = useRef<HTMLInputElement>(null);

  const rawPrompt = (props.custom_style_prompt as string) || '';
  const expandedPrompt = (props.custom_style_expanded_prompt as string) || '';
  const attachments: CustomStyleAttachment[] = Array.isArray(props.custom_style_attachments)
    ? (props.custom_style_attachments as CustomStyleAttachment[])
    : [];
  const pdfDocumentIds = attachments.filter((a) => a.kind === 'pdf').map((a) => a.document_id);
  const photoCount = attachments.filter((a) => a.kind === 'photo').length;

  const currentHash = computeExpansionHash(rawPrompt, pdfDocumentIds);
  const isStale = !!expandedPrompt
    && !props.custom_style_expanded_edited
    && props.custom_style_expansion_hash !== currentHash;

  // Poll extraction status for PDFs that are still processing. A single
  // transient request failure must NOT mark the document failed — only the
  // server-reported status can, or three consecutive request errors.
  const pollErrorCountsRef = useRef<Record<string, number>>({});
  useEffect(() => {
    const pendingIds = pdfDocumentIds.filter((id) => {
      const s = docStatuses[id];
      return s === undefined || s === 'pending' || s === 'processing';
    });
    if (pendingIds.length === 0) return;

    let cancelled = false;
    const poll = async () => {
      for (const id of pendingIds) {
        try {
          const doc = await documentsApi.get(id);
          pollErrorCountsRef.current[id] = 0;
          if (!cancelled) {
            setDocStatuses((prev) => (prev[id] === doc.processing_status ? prev : { ...prev, [id]: doc.processing_status }));
          }
        } catch {
          const errors = (pollErrorCountsRef.current[id] || 0) + 1;
          pollErrorCountsRef.current[id] = errors;
          if (!cancelled && errors >= 3) setDocStatuses((prev) => ({ ...prev, [id]: 'failed' }));
        }
      }
    };
    poll();
    const timer = window.setInterval(poll, 3000);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pdfDocumentIds.join(','), Object.entries(docStatuses).map(([k, v]) => `${k}:${v}`).join(',')]);

  const handleFilesSelected = useCallback(async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    setError(null);

    const room = MAX_ATTACHMENTS - attachments.length;
    if (room <= 0) {
      setError(`Maximum ${MAX_ATTACHMENTS} attachments per zone.`);
      return;
    }

    const selected = Array.from(files).slice(0, room);
    setUploading(true);
    try {
      const uploaded: CustomStyleAttachment[] = [];
      for (const file of selected) {
        const ext = (file.name.split('.').pop() || '').toLowerCase();
        if (!ACCEPTED_EXTENSIONS.includes(ext)) {
          setError(`"${file.name}" skipped — only JPG, PNG, and PDF are supported.`);
          continue;
        }
        const doc = await documentsApi.upload(zone.project_id, file, 'reference');
        uploaded.push({
          document_id: doc.id,
          filename: doc.filename,
          file_type: ext,
          kind: ext === 'pdf' ? 'pdf' : 'photo',
          url: `/api/v1/documents/${doc.id}/file`,
        });
      }
      if (uploaded.length > 0) {
        setProps((p) => {
          const existing = Array.isArray(p.custom_style_attachments)
            ? (p.custom_style_attachments as CustomStyleAttachment[])
            : [];
          return { ...p, custom_style_attachments: [...existing, ...uploaded].slice(0, MAX_ATTACHMENTS) };
        });
      }
    } catch (e) {
      console.error('[CustomStyle] Upload failed:', e);
      setError('Upload failed — please try again.');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  }, [attachments.length, setProps, zone.project_id]);

  const removeAttachment = useCallback((documentId: string) => {
    setProps((p) => {
      const existing = Array.isArray(p.custom_style_attachments)
        ? (p.custom_style_attachments as CustomStyleAttachment[])
        : [];
      const next = existing.filter((a) => a.document_id !== documentId);
      return { ...p, custom_style_attachments: next.length > 0 ? next : undefined };
    });
  }, [setProps]);

  const handleExpand = useCallback(async () => {
    if (!rawPrompt.trim() || rawPrompt.trim().length < 3) {
      setError('Describe your vision first (a sentence or two is enough).');
      return;
    }
    setError(null);
    setExpanding(true);
    try {
      const zoneContext: Record<string, unknown> = {
        zone_type: zone.zone_type,
        area_sqm: areaSqm != null ? Math.round(areaSqm) : undefined,
        floors: props.floors ?? undefined,
        height_m: props.height ?? undefined,
      };
      const result = await customStyleApi.expand({
        project_id: zone.project_id,
        zone_id: zone.id,
        user_prompt: rawPrompt.trim(),
        document_ids: pdfDocumentIds,
        zone_context: zoneContext,
        domain,
      });
      // Hash only the documents whose text the expansion actually used — a
      // still-processing PDF must leave the hash stale so the "out of date"
      // badge prompts a regenerate once its extraction completes.
      const usedDocIds = result.used_documents.filter((d) => d.status === 'completed').map((d) => d.id);
      setProps((p) => ({
        ...p,
        custom_style_expanded_prompt: result.expanded_prompt,
        custom_style_expanded_at: new Date().toISOString(),
        custom_style_expansion_hash: computeExpansionHash(rawPrompt, usedDocIds),
        custom_style_expanded_edited: false,
      }));
      const skipped = result.used_documents.filter((d) => d.status !== 'completed');
      if (skipped.length > 0) {
        setError(`Note: ${skipped.map((d) => d.filename).join(', ')} not used (still processing) — regenerate later to include.`);
      }
    } catch (e) {
      console.error('[CustomStyle] Expansion failed:', e);
      setError("Couldn't generate a detailed description — your raw description will be used for renders.");
    } finally {
      setExpanding(false);
    }
  }, [areaSqm, domain, pdfDocumentIds, props.floors, props.height, rawPrompt, setProps, zone.id, zone.project_id, zone.zone_type]);

  return (
    <div className="space-y-2.5">
      <div>
        <label className={labelClass}>Describe your vision</label>
        <textarea
          rows={4}
          value={rawPrompt}
          placeholder={DOMAIN_PLACEHOLDER[domain]}
          onChange={(e) => setProps((p) => ({ ...p, custom_style_prompt: e.target.value || undefined }))}
          className={textareaClass}
        />
      </div>

      <div>
        <label className={labelClass}>Reference photos & documents</label>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".jpg,.jpeg,.png,.pdf"
          className="hidden"
          onChange={(e) => handleFilesSelected(e.currentTarget.files)}
        />
        <button
          type="button"
          disabled={uploading || attachments.length >= MAX_ATTACHMENTS}
          onClick={() => fileInputRef.current?.click()}
          className="mt-1 w-full rounded-lg border-2 border-dashed border-[#151515]/40 bg-white px-2.5 py-2 text-[11px] font-bold text-[#151515]/70 hover:border-[#151515] hover:bg-[#fff9ec] disabled:opacity-50"
        >
          {uploading ? 'Uploading…' : `+ Add photos or PDFs (${attachments.length}/${MAX_ATTACHMENTS})`}
        </button>
        {attachments.length > 0 && (
          <ul className="mt-1.5 space-y-1">
            {attachments.map((att, idx) => {
              const photoIndex = attachments.filter((a, i) => a.kind === 'photo' && i < idx).length;
              const photoUnused = att.kind === 'photo' && photoIndex >= MAX_RENDER_PHOTOS;
              const status = att.kind === 'pdf' ? (docStatuses[att.document_id] || 'pending') : undefined;
              return (
                <li
                  key={att.document_id}
                  className="flex items-center gap-2 rounded-lg border-2 border-[#151515]/15 bg-white px-2 py-1"
                >
                  {att.kind === 'photo' ? (
                    <img
                      src={resolveApiFileUrl(att.url)}
                      alt={att.filename}
                      className="h-8 w-8 rounded object-cover border border-[#151515]/20"
                      onError={(e) => { (e.currentTarget as HTMLImageElement).style.opacity = '0.25'; }}
                    />
                  ) : (
                    <span className="flex h-8 w-8 items-center justify-center rounded bg-[#151515]/5 text-[9px] font-black text-[#151515]/60">PDF</span>
                  )}
                  <div className="min-w-0 flex-1">
                    <div className="truncate text-[11px] font-semibold text-[#151515]/80">{att.filename}</div>
                    <div className="text-[9px] font-bold uppercase text-[#151515]/45">
                      {att.kind === 'photo'
                        ? (photoUnused ? 'not used in render (max 3 photos)' : 'render reference')
                        : status === 'completed' ? 'text extracted'
                          : status === 'failed' ? 'extraction failed'
                            : 'extracting text…'}
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeAttachment(att.document_id)}
                    className="rounded px-1.5 py-0.5 text-[11px] font-black text-[#151515]/50 hover:bg-red-50 hover:text-red-600"
                    aria-label={`Remove ${att.filename}`}
                  >
                    ✕
                  </button>
                </li>
              );
            })}
          </ul>
        )}
        {photoCount > MAX_RENDER_PHOTOS && (
          <p className="mt-0.5 text-[10px] text-[#151515]/50">Only the first {MAX_RENDER_PHOTOS} photos are sent to the render model.</p>
        )}
      </div>

      <div>
        <div className="flex items-center justify-between">
          <label className={labelClass}>Detailed description</label>
          {isStale && (
            <span className="rounded bg-orange-100 px-1.5 py-0.5 text-[9px] font-black uppercase text-orange-600">
              out of date
            </span>
          )}
        </div>
        <button
          type="button"
          disabled={expanding || !rawPrompt.trim()}
          onClick={handleExpand}
          className="mt-1 w-full rounded-lg border-2 border-[#151515] bg-[#c9ff3d] px-2.5 py-1.5 text-[11px] font-black uppercase text-[#151515] shadow-[2px_2px_0_0_rgba(21,21,21,0.2)] hover:bg-[#d7ff6b] disabled:opacity-50"
        >
          {expanding ? 'Generating…' : expandedPrompt ? 'Regenerate description' : 'Generate detailed description'}
        </button>
        {/* Keep the textarea mounted once an expansion has existed — otherwise
            clearing all its text would unmount it mid-edit and drop focus */}
        {(expandedPrompt || props.custom_style_expanded_at) && (
          <textarea
            rows={6}
            value={expandedPrompt}
            onChange={(e) => setProps((p) => ({
              ...p,
              custom_style_expanded_prompt: e.target.value || undefined,
              custom_style_expanded_edited: true,
            }))}
            className={`${textareaClass} mt-1.5`}
          />
        )}
        {!expandedPrompt && !props.custom_style_expanded_at && rawPrompt.trim() && (
          <p className="mt-0.5 text-[10px] text-[#151515]/50">
            Renders will use your raw description until you generate a detailed one.
          </p>
        )}
      </div>

      {error && (
        <p className="rounded-lg border-2 border-orange-200 bg-orange-50 px-2 py-1 text-[10px] font-semibold text-orange-700">{error}</p>
      )}
    </div>
  );
}
