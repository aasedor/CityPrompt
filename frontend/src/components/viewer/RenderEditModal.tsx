import { useCallback, useEffect, useRef, useState, type PointerEvent as ReactPointerEvent } from 'react';
import toast from 'react-hot-toast';
import { Brush, Check, Loader2, Minus, Plus, RotateCcw, Undo2, Wand2, X } from 'lucide-react';
import { getApiErrorMessage, rendersApi } from '@/services/api';
import type { SavedRender } from '@/types';
import { imageUrlToBase64 } from '@/utils/renderPersistence';
import { imageModelLabel } from '@/config/imageModels';
import { ImageModelSelect } from './ImageModelSelect';
import { useImageModelChoice } from './useImageModelChoice';
import { runImageModelBatch } from './runImageModelBatch';

interface RenderEditModalProps {
  projectId: string;
  render: SavedRender;
  imageUrl: string;
  onClose: () => void;
  onSaved: (render: SavedRender) => void;
}

const DEFAULT_BRUSH_SIZE = 44;
const MAX_UNDO_STEPS = 30;
const MIN_ZOOM = 0.5;
const MAX_ZOOM = 2.5;
const ZOOM_STEP = 0.25;

interface CanvasSnapshot {
  overlay: ImageData;
  mask: ImageData;
  hasMask: boolean;
}

function getCanvasBase64(canvas: HTMLCanvasElement): string {
  return canvas.toDataURL('image/png').split(',')[1] || '';
}

function drawBrushDot(ctx: CanvasRenderingContext2D, x: number, y: number, radius: number) {
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.fill();
}

export function RenderEditModal({ projectId, render, imageUrl, onClose, onSaved }: RenderEditModalProps) {
  const overlayCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const maskCanvasRef = useRef<HTMLCanvasElement | null>(null);
  const isDrawingRef = useRef(false);
  const lastPointRef = useRef<{ x: number; y: number } | null>(null);
  const undoStackRef = useRef<CanvasSnapshot[]>([]);

  const [prompt, setPrompt] = useState('');
  const { imageModel, setImageModel, availability: imageModelAvailability } = useImageModelChoice();
  const [imageProgress, setImageProgress] = useState('');
  const [brushSize, setBrushSize] = useState(DEFAULT_BRUSH_SIZE);
  const [zoom, setZoom] = useState(1);
  const [imageSize, setImageSize] = useState<{ width: number; height: number } | null>(null);
  const [displaySize, setDisplaySize] = useState<{ width: number; height: number } | null>(null);
  const [hasMask, setHasMask] = useState(false);
  const [canUndo, setCanUndo] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const updateUndoAvailability = useCallback(() => {
    setCanUndo(undoStackRef.current.length > 0);
  }, []);

  useEffect(() => {
    undoStackRef.current = [];
    isDrawingRef.current = false;
    lastPointRef.current = null;
    setPrompt('');
    setBrushSize(DEFAULT_BRUSH_SIZE);
    setZoom(1);
    setImageSize(null);
    setDisplaySize(null);
    setHasMask(false);
    setCanUndo(false);
    setPreviewUrl(null);
  }, [imageUrl, render.id]);

  const pushUndoSnapshot = useCallback(() => {
    const overlay = overlayCanvasRef.current;
    const mask = maskCanvasRef.current;
    const overlayCtx = overlay?.getContext('2d');
    const maskCtx = mask?.getContext('2d');
    if (!overlay || !mask || !overlayCtx || !maskCtx) return;

    undoStackRef.current = [
      ...undoStackRef.current.slice(-(MAX_UNDO_STEPS - 1)),
      {
        overlay: overlayCtx.getImageData(0, 0, overlay.width, overlay.height),
        mask: maskCtx.getImageData(0, 0, mask.width, mask.height),
        hasMask,
      },
    ];
    updateUndoAvailability();
  }, [hasMask, updateUndoAvailability]);

  const undoLastStroke = useCallback(() => {
    const snapshot = undoStackRef.current.pop();
    const overlay = overlayCanvasRef.current;
    const mask = maskCanvasRef.current;
    const overlayCtx = overlay?.getContext('2d');
    const maskCtx = mask?.getContext('2d');
    if (!snapshot || !overlay || !mask || !overlayCtx || !maskCtx) {
      updateUndoAvailability();
      return;
    }

    overlayCtx.putImageData(snapshot.overlay, 0, 0);
    maskCtx.putImageData(snapshot.mask, 0, 0);
    setHasMask(snapshot.hasMask);
    lastPointRef.current = null;
    updateUndoAvailability();
  }, [updateUndoAvailability]);

  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && !submitting) {
        event.preventDefault();
        onClose();
        return;
      }

      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z' && !submitting) {
        event.preventDefault();
        undoLastStroke();
      }
    };
    window.addEventListener('keydown', handleKey, true);
    return () => window.removeEventListener('keydown', handleKey, true);
  }, [onClose, submitting, undoLastStroke]);

  const clearMask = useCallback(() => {
    const overlay = overlayCanvasRef.current;
    const mask = maskCanvasRef.current;
    if (!overlay || !mask) return;

    overlay.getContext('2d')?.clearRect(0, 0, overlay.width, overlay.height);
    const maskCtx = mask.getContext('2d');
    if (maskCtx) {
      maskCtx.fillStyle = '#000';
      maskCtx.fillRect(0, 0, mask.width, mask.height);
    }
    undoStackRef.current = [];
    updateUndoAvailability();
    setHasMask(false);
    lastPointRef.current = null;
  }, [updateUndoAvailability]);

  const configureCanvases = useCallback((width: number, height: number) => {
    for (const canvas of [overlayCanvasRef.current, maskCanvasRef.current]) {
      if (!canvas) continue;
      canvas.width = width;
      canvas.height = height;
    }
    clearMask();
  }, [clearMask]);

  const handleImageLoad = useCallback((event: React.SyntheticEvent<HTMLImageElement>) => {
    const img = event.currentTarget;
    const nextSize = {
      width: Math.max(1, img.naturalWidth),
      height: Math.max(1, img.naturalHeight),
    };
    setImageSize(nextSize);
    setZoom(1);
    requestAnimationFrame(() => {
      const rect = img.getBoundingClientRect();
      setDisplaySize({
        width: Math.max(1, rect.width),
        height: Math.max(1, rect.height),
      });
      configureCanvases(nextSize.width, nextSize.height);
    });
  }, [configureCanvases]);

  const adjustZoom = useCallback((delta: number) => {
    setZoom((current) => Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, Number((current + delta).toFixed(2)))));
  }, []);

  const getCanvasPoint = useCallback((event: ReactPointerEvent<HTMLCanvasElement>) => {
    const canvas = overlayCanvasRef.current;
    if (!canvas) return null;
    const rect = canvas.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * canvas.width;
    const y = ((event.clientY - rect.top) / rect.height) * canvas.height;
    return {
      x: Math.min(Math.max(x, 0), canvas.width),
      y: Math.min(Math.max(y, 0), canvas.height),
    };
  }, []);

  const drawAt = useCallback((point: { x: number; y: number }) => {
    const overlay = overlayCanvasRef.current;
    const mask = maskCanvasRef.current;
    if (!overlay || !mask) return;

    const overlayCtx = overlay.getContext('2d');
    const maskCtx = mask.getContext('2d');
    if (!overlayCtx || !maskCtx) return;

    const radius = brushSize / 2;
    const previous = lastPointRef.current;

    overlayCtx.fillStyle = 'rgba(244, 63, 94, 0.34)';
    maskCtx.fillStyle = '#fff';
    overlayCtx.strokeStyle = 'rgba(244, 63, 94, 0.46)';
    maskCtx.strokeStyle = '#fff';
    overlayCtx.lineCap = 'round';
    maskCtx.lineCap = 'round';
    overlayCtx.lineJoin = 'round';
    maskCtx.lineJoin = 'round';
    overlayCtx.lineWidth = brushSize;
    maskCtx.lineWidth = brushSize;

    if (previous) {
      overlayCtx.beginPath();
      overlayCtx.moveTo(previous.x, previous.y);
      overlayCtx.lineTo(point.x, point.y);
      overlayCtx.stroke();
      maskCtx.beginPath();
      maskCtx.moveTo(previous.x, previous.y);
      maskCtx.lineTo(point.x, point.y);
      maskCtx.stroke();
    } else {
      drawBrushDot(overlayCtx, point.x, point.y, radius);
      drawBrushDot(maskCtx, point.x, point.y, radius);
    }

    lastPointRef.current = point;
    setHasMask(true);
  }, [brushSize]);

  const handlePointerDown = useCallback((event: ReactPointerEvent<HTMLCanvasElement>) => {
    if (submitting) return;
    const point = getCanvasPoint(event);
    if (!point) return;
    event.currentTarget.setPointerCapture(event.pointerId);
    pushUndoSnapshot();
    isDrawingRef.current = true;
    lastPointRef.current = null;
    drawAt(point);
  }, [drawAt, getCanvasPoint, pushUndoSnapshot, submitting]);

  const handlePointerMove = useCallback((event: ReactPointerEvent<HTMLCanvasElement>) => {
    if (!isDrawingRef.current || submitting) return;
    const point = getCanvasPoint(event);
    if (point) drawAt(point);
  }, [drawAt, getCanvasPoint, submitting]);

  const stopDrawing = useCallback((event: ReactPointerEvent<HTMLCanvasElement>) => {
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
    isDrawingRef.current = false;
    lastPointRef.current = null;
  }, []);

  const handleSubmit = useCallback(async () => {
    const mask = maskCanvasRef.current;
    const editPrompt = prompt.trim();
    if (!mask || !hasMask || !editPrompt || submitting) return;

    setSubmitting(true);
    setPreviewUrl(null);
    try {
      const sourceBase64 = await imageUrlToBase64(imageUrl);
      const fullPrompt = [
        'Edit the completed SiteForge architectural render only inside the white mask.',
        'Preserve camera angle, composition, geometry, lighting, shadows, and all unmasked areas exactly.',
        `Requested local change: ${editPrompt}`,
        'CRITICAL: Only alter the circled/masked region. Do not redesign or repaint the rest of the image.',
      ].join('\n');

      const maskBase64 = getCanvasBase64(mask);
      await runImageModelBatch(imageModel, async (model) => ({ model, response: await rendersApi.generateEdit({
        image_base64: sourceBase64,
        previous_render_base64: sourceBase64,
        mask_base64: maskBase64,
        prompt: fullPrompt,
        project_id: projectId,
        model,
        image_quality: render.image_quality || 'auto',
      }) }), async ({ model, response }) => {
        const resultUrl = `data:image/png;base64,${response.image_base64}`;
        setPreviewUrl(resultUrl);
        const saved = await rendersApi.save(projectId, {
          image_base64: response.image_base64,
          prompt: `${render.prompt || 'Saved render'}\n\nEdit: ${editPrompt}`,
          style: render.style ? `${render.style} edit` : 'masked edit',
          seed: response.seed,
          model: response.model ?? model,
          image_quality: render.image_quality || 'auto',
        });
        onSaved(saved);
      }, (model, index, total) => setImageProgress(`${index + 1}/${total} · ${imageModelLabel(model)}`));
      toast.success('Edited render saved');
      onClose();
    } catch (error) {
      toast.error(getApiErrorMessage(error, 'Failed to edit render'));
    } finally {
      setSubmitting(false);
      setImageProgress('');
    }
  }, [hasMask, imageUrl, imageModel, onClose, onSaved, projectId, prompt, render.image_quality, render.prompt, render.style, submitting]);

  const canSubmit = Boolean(hasMask && prompt.trim() && imageSize && !submitting);

  return (
    <div
      className="fixed inset-0 z-[320] flex items-center justify-center bg-black/85 p-4 backdrop-blur-sm"
      onClick={(event) => {
        if (event.target === event.currentTarget && !submitting) onClose();
      }}
    >
      <div className="flex h-[82vh] max-h-[56rem] min-h-[38rem] w-full max-w-6xl flex-col overflow-hidden rounded-xl bg-gray-950 shadow-2xl ring-1 ring-white/10">
        <div className="flex items-center justify-between border-b border-white/10 px-4 py-3">
          <div className="flex items-center gap-2">
            <Wand2 size={18} className="text-amber-300" />
            <div>
              <h2 className="text-sm font-bold text-white">Edit Render</h2>
              <p className="text-xs text-white/50">Mark the area to change, then describe the change.</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            disabled={submitting}
            className="rounded-full bg-white/10 p-2 text-white/75 transition hover:bg-white/15 hover:text-white disabled:opacity-50"
            aria-label="Close edit render"
          >
            <X size={18} />
          </button>
        </div>

        <div className="grid min-h-0 flex-1 gap-0 lg:grid-cols-[minmax(0,1fr)_20rem]">
          <div className="relative min-h-0 min-w-0 overflow-hidden bg-black">
            <div className="absolute left-6 top-6 z-20 flex w-fit items-center gap-1 rounded-full bg-black/70 p-1 shadow-lg ring-1 ring-white/15 backdrop-blur-sm">
              <button
                type="button"
                onClick={() => adjustZoom(-ZOOM_STEP)}
                disabled={submitting || zoom <= MIN_ZOOM}
                className="flex h-8 w-8 items-center justify-center rounded-full text-white/80 transition hover:bg-white/15 hover:text-white disabled:cursor-not-allowed disabled:opacity-35"
                aria-label="Zoom out"
                title="Zoom out"
              >
                <Minus size={15} />
              </button>
              <button
                type="button"
                onClick={() => setZoom(1)}
                disabled={submitting || zoom === 1}
                className="h-8 rounded-full px-2 text-[11px] font-bold text-white/80 transition hover:bg-white/15 hover:text-white disabled:cursor-not-allowed disabled:opacity-35"
                title="Reset zoom"
              >
                {Math.round(zoom * 100)}%
              </button>
              <button
                type="button"
                onClick={() => adjustZoom(ZOOM_STEP)}
                disabled={submitting || zoom >= MAX_ZOOM}
                className="flex h-8 w-8 items-center justify-center rounded-full text-white/80 transition hover:bg-white/15 hover:text-white disabled:cursor-not-allowed disabled:opacity-35"
                aria-label="Zoom in"
                title="Zoom in"
              >
                <Plus size={15} />
              </button>
            </div>

            <div className="h-full w-full overflow-auto p-4">
              <div
                className="mx-auto"
                style={displaySize ? {
                  width: displaySize.width * zoom,
                  height: displaySize.height * zoom,
                } : undefined}
              >
                <div
                  className="relative overflow-hidden rounded-lg border border-white/10 bg-gray-900"
                  style={displaySize ? {
                    width: displaySize.width,
                    height: displaySize.height,
                    transform: `scale(${zoom})`,
                    transformOrigin: 'top left',
                  } : undefined}
                >
                  <img
                    src={previewUrl || imageUrl}
                    alt={render.prompt || 'Saved render'}
                    onLoad={handleImageLoad}
                    className={displaySize ? 'block h-full w-full select-none object-contain' : 'block max-h-[72vh] max-w-full select-none object-contain'}
                    draggable={false}
                  />
                  {!previewUrl && (
                    <>
                      <canvas ref={maskCanvasRef} className="hidden" />
                      <canvas
                        ref={overlayCanvasRef}
                        className="absolute inset-0 h-full w-full cursor-crosshair touch-none"
                        onPointerDown={handlePointerDown}
                        onPointerMove={handlePointerMove}
                        onPointerUp={stopDrawing}
                        onPointerCancel={stopDrawing}
                        onPointerLeave={stopDrawing}
                        aria-label="Draw edit mask"
                      />
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>

          <aside className="flex min-h-0 flex-col gap-4 border-t border-white/10 bg-gray-900/80 p-4 text-white lg:border-l lg:border-t-0">
            <ImageModelSelect value={imageModel} onChange={setImageModel} disabled={submitting} availability={imageModelAvailability} />
            {imageProgress && <p role="status" className="text-xs">{imageProgress}</p>}
            <div className="rounded-lg bg-white/[0.04] p-3 ring-1 ring-white/10">
              <label htmlFor="render-edit-brush" className="flex items-center justify-between text-xs font-semibold text-white/75">
                <span className="flex items-center gap-1.5"><Brush size={13} /> Brush</span>
                <span>{brushSize}px</span>
              </label>
              <input
                id="render-edit-brush"
                type="range"
                min={16}
                max={120}
                value={brushSize}
                disabled={submitting}
                onChange={(event) => setBrushSize(Number(event.target.value))}
                className="mt-3 w-full accent-amber-400"
              />
            </div>

            <label className="flex min-h-0 flex-1 flex-col text-xs font-semibold text-white/75">
              Description
              <textarea
                value={prompt}
                disabled={submitting}
                onChange={(event) => setPrompt(event.target.value)}
                placeholder="Example: add a row of mature trees here, or make this plaza more active with seating."
                className="mt-2 min-h-36 flex-1 resize-none rounded-lg border border-white/10 bg-black/35 px-3 py-2 text-sm font-normal text-white placeholder:text-white/30 focus:border-amber-400/70 focus:outline-none"
              />
            </label>

            <div className="flex gap-2">
              <button
                type="button"
                onClick={undoLastStroke}
                disabled={submitting || !canUndo}
                className="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
                title="Undo last brush stroke"
              >
                <Undo2 size={14} />
                Undo
              </button>
              <button
                type="button"
                onClick={clearMask}
                disabled={submitting || !hasMask}
                className="flex items-center gap-2 rounded-lg border border-white/10 px-3 py-2 text-xs font-semibold text-white/70 transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-40"
              >
                <RotateCcw size={14} />
                Clear
              </button>
              <button
                type="button"
                onClick={handleSubmit}
                disabled={!canSubmit}
                className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-amber-400 px-3 py-2 text-sm font-bold text-black transition hover:bg-amber-300 disabled:cursor-not-allowed disabled:bg-gray-700 disabled:text-gray-400"
              >
                {submitting ? <Loader2 size={16} className="animate-spin" /> : <Check size={16} />}
                {submitting ? 'Reprocessing...' : 'Reprocess'}
              </button>
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
