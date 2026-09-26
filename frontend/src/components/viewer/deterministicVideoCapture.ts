import { ArrayBufferTarget, Muxer } from 'mp4-muxer';

import { selectVideoRecorderMimeType } from './videoRouteControls';

export const CITY_PROMPT_VIDEO_WIDTH = 1280;
export const CITY_PROMPT_VIDEO_HEIGHT = 720;
export const CITY_PROMPT_VIDEO_FPS = 24;
export const CITY_PROMPT_VIDEO_DURATION_SECONDS = 8;
export const CITY_PROMPT_VIDEO_FRAME_COUNT =
  CITY_PROMPT_VIDEO_FPS * CITY_PROMPT_VIDEO_DURATION_SECONDS;
export const CITY_PROMPT_VIDEO_BITRATE = 12_000_000;

export type DeterministicVideoEncoder = 'webcodecs_h264' | 'media_recorder_webm';

export interface DeterministicVideoFrame {
  index: number;
  progress: number;
  timestampMicroseconds: number;
  durationMicroseconds: number;
}

export interface DeterministicVideoCaptureResult {
  blob: Blob;
  encoder: DeterministicVideoEncoder;
  frameCount: number;
  fps: number;
  width: number;
  height: number;
}

export interface SourceCropRect {
  sx: number;
  sy: number;
  sw: number;
  sh: number;
}

/** One canvas encoded alongside the others from the same frame clock. */
export interface DeterministicVideoTrack {
  /** Stable id the caller reads the encoded result back with, e.g. 'beauty'. */
  id: string;
  canvas: HTMLCanvasElement;
  bitrate?: number;
}

export interface DeterministicVideoTracksResult {
  tracks: Record<string, DeterministicVideoCaptureResult>;
  encoder: DeterministicVideoEncoder;
  frameCount: number;
  fps: number;
  /** Requested tracks the compatibility path could not produce. */
  droppedTrackIds: string[];
}

interface CaptureOptions {
  canvas: HTMLCanvasElement;
  durationSeconds?: number;
  fps?: number;
  bitrate?: number;
  renderFrame: (frame: DeterministicVideoFrame) => Promise<void> | void;
}

interface TracksCaptureOptions {
  tracks: DeterministicVideoTrack[];
  durationSeconds?: number;
  fps?: number;
  renderFrame: (frame: DeterministicVideoFrame) => Promise<void> | void;
}

const clampPositiveInteger = (value: number, fallback: number) => (
  Number.isFinite(value) && value > 0 ? Math.max(1, Math.round(value)) : fallback
);

/**
 * Build the immutable frame clock for a City Prompt route render.
 *
 * Camera progress is derived from the frame index instead of wall-clock time,
 * so a slow GPU can make capture take longer without skipping part of the
 * route. The final frame deliberately lands on the route endpoint.
 */
export function buildDeterministicVideoFrames(
  durationSeconds = CITY_PROMPT_VIDEO_DURATION_SECONDS,
  fps = CITY_PROMPT_VIDEO_FPS,
): DeterministicVideoFrame[] {
  const safeDuration = clampPositiveInteger(durationSeconds, CITY_PROMPT_VIDEO_DURATION_SECONDS);
  const safeFps = clampPositiveInteger(fps, CITY_PROMPT_VIDEO_FPS);
  const frameCount = safeDuration * safeFps;
  const durationMicroseconds = Math.round(1_000_000 / safeFps);

  return Array.from({ length: frameCount }, (_, index) => ({
    index,
    progress: frameCount <= 1 ? 1 : index / (frameCount - 1),
    timestampMicroseconds: Math.round(index * 1_000_000 / safeFps),
    durationMicroseconds,
  }));
}

/** Center-crop a source canvas to the exact output aspect ratio. */
export function getCenterCropRect(
  sourceWidth: number,
  sourceHeight: number,
  targetWidth = CITY_PROMPT_VIDEO_WIDTH,
  targetHeight = CITY_PROMPT_VIDEO_HEIGHT,
): SourceCropRect {
  const safeSourceWidth = Math.max(1, sourceWidth);
  const safeSourceHeight = Math.max(1, sourceHeight);
  const sourceAspect = safeSourceWidth / safeSourceHeight;
  const targetAspect = Math.max(1, targetWidth) / Math.max(1, targetHeight);

  if (sourceAspect > targetAspect) {
    const sw = safeSourceHeight * targetAspect;
    return {
      sx: (safeSourceWidth - sw) / 2,
      sy: 0,
      sw,
      sh: safeSourceHeight,
    };
  }

  const sh = safeSourceWidth / targetAspect;
  return {
    sx: 0,
    sy: (safeSourceHeight - sh) / 2,
    sw: safeSourceWidth,
    sh,
  };
}

function webCodecsGlobals(): {
  VideoEncoderClass?: typeof VideoEncoder;
  VideoFrameClass?: typeof VideoFrame;
} {
  const codecs = globalThis as typeof globalThis & {
    VideoEncoder?: typeof VideoEncoder;
    VideoFrame?: typeof VideoFrame;
  };
  return {
    VideoEncoderClass: codecs.VideoEncoder,
    VideoFrameClass: codecs.VideoFrame,
  };
}

const encoderConfigurations = (
  width: number,
  height: number,
  fps: number,
  bitrate: number,
): VideoEncoderConfig[] => [
  // Prefer High Profile for facade lines, foliage, and fine PBR texture.
  {
    codec: 'avc1.640028',
    width,
    height,
    framerate: fps,
    bitrate,
    bitrateMode: 'variable',
    latencyMode: 'quality',
    hardwareAcceleration: 'prefer-hardware',
    avc: { format: 'avc' },
  },
  // Main/Baseline are compatibility fallbacks on older integrated GPUs.
  {
    codec: 'avc1.4d4028',
    width,
    height,
    framerate: fps,
    bitrate,
    latencyMode: 'quality',
    avc: { format: 'avc' },
  },
  {
    codec: 'avc1.420028',
    width,
    height,
    framerate: fps,
    bitrate,
    avc: { format: 'avc' },
  },
];

async function supportedEncoderConfiguration(
  width: number,
  height: number,
  fps: number,
  bitrate: number,
): Promise<VideoEncoderConfig | null> {
  const { VideoEncoderClass, VideoFrameClass } = webCodecsGlobals();
  if (!VideoEncoderClass || !VideoFrameClass || !VideoEncoderClass.isConfigSupported) return null;

  for (const config of encoderConfigurations(width, height, fps, bitrate)) {
    try {
      const support = await VideoEncoderClass.isConfigSupported(config);
      if (support.supported) return support.config ?? config;
    } catch {
      // Try the next AVC profile. Browser codec support is intentionally
      // treated as a runtime capability rather than a hard requirement.
    }
  }
  return null;
}

const waitForEncoderCapacity = async (encoder: VideoEncoder, maxQueueSize = 6) => {
  while (encoder.encodeQueueSize > maxQueueSize) {
    await new Promise<void>((resolve) => {
      encoder.addEventListener('dequeue', () => resolve(), { once: true });
    });
  }
};

interface PreparedTrack {
  track: DeterministicVideoTrack;
  config: VideoEncoderConfig;
}

/**
 * Encode every track from one shared frame clock. `renderFrame` runs once per
 * index; each track's canvas is then encoded with the same timestamp, so a
 * depth or mask track lines up with the beauty track frame for frame.
 */
async function captureWithWebCodecs(
  options: { fps: number; renderFrame: TracksCaptureOptions['renderFrame'] },
  frames: DeterministicVideoFrame[],
  prepared: PreparedTrack[],
): Promise<Record<string, DeterministicVideoCaptureResult>> {
  const { VideoEncoderClass, VideoFrameClass } = webCodecsGlobals();
  if (!VideoEncoderClass || !VideoFrameClass) throw new Error('WebCodecs became unavailable during capture.');

  const lanes = prepared.map(({ track, config }) => {
    const target = new ArrayBufferTarget();
    const muxer = new Muxer({
      target,
      video: {
        codec: 'avc',
        width: track.canvas.width,
        height: track.canvas.height,
        frameRate: options.fps,
      },
      fastStart: 'in-memory',
    });
    let encoderError: Error | null = null;
    const encoder = new VideoEncoderClass({
      output: (chunk, metadata) => muxer.addVideoChunk(chunk, metadata),
      error: (error) => {
        encoderError = error instanceof Error ? error : new Error(String(error));
      },
    });
    encoder.configure(config);
    return { track, target, muxer, encoder, error: () => encoderError };
  });

  try {
    for (const frame of frames) {
      await options.renderFrame(frame);
      for (const lane of lanes) {
        const encoderError = lane.error();
        if (encoderError) throw encoderError;
        await waitForEncoderCapacity(lane.encoder);
        const videoFrame = new VideoFrameClass(lane.track.canvas, {
          timestamp: frame.timestampMicroseconds,
          duration: frame.durationMicroseconds,
          alpha: 'discard',
        });
        try {
          lane.encoder.encode(videoFrame, {
            keyFrame: frame.index === 0 || frame.index % (options.fps * 2) === 0,
          });
        } finally {
          videoFrame.close();
        }
      }
    }
    for (const lane of lanes) {
      await lane.encoder.flush();
      const encoderError = lane.error();
      if (encoderError) throw encoderError;
      lane.muxer.finalize();
    }
  } finally {
    for (const lane of lanes) {
      if (lane.encoder.state !== 'closed') lane.encoder.close();
    }
  }

  const results: Record<string, DeterministicVideoCaptureResult> = {};
  for (const lane of lanes) {
    const blob = new Blob([lane.target.buffer], { type: 'video/mp4' });
    if (blob.size < 1024) throw new Error(`The fixed-frame H.264 ${lane.track.id} render was unexpectedly empty.`);
    results[lane.track.id] = {
      blob,
      encoder: 'webcodecs_h264',
      frameCount: frames.length,
      fps: options.fps,
      width: lane.track.canvas.width,
      height: lane.track.canvas.height,
    };
  }
  return results;
}

async function captureWithMediaRecorder(
  options: { canvas: HTMLCanvasElement; fps: number; bitrate: number; renderFrame: TracksCaptureOptions['renderFrame'] },
  frames: DeterministicVideoFrame[],
): Promise<DeterministicVideoCaptureResult> {
  if (typeof MediaRecorder === 'undefined' || typeof options.canvas.captureStream !== 'function') {
    throw new Error('This browser cannot encode the deterministic route preview.');
  }

  const stream = options.canvas.captureStream(0);
  const track = stream.getVideoTracks()[0] as CanvasCaptureMediaStreamTrack | undefined;
  const recorderMimeType = selectVideoRecorderMimeType((mime) => MediaRecorder.isTypeSupported(mime));
  const recorder = new MediaRecorder(stream, {
    ...(recorderMimeType ? { mimeType: recorderMimeType } : {}),
    videoBitsPerSecond: options.bitrate,
  });
  const chunks: Blob[] = [];
  recorder.addEventListener('dataavailable', (event) => {
    if (event.data.size > 0) chunks.push(event.data);
  });
  const stopped = new Promise<void>((resolve, reject) => {
    recorder.addEventListener('stop', () => resolve(), { once: true });
    recorder.addEventListener('error', () => reject(new Error('The browser could not record the route preview.')), { once: true });
  });

  try {
    recorder.start(500);
    for (const frame of frames) {
      await options.renderFrame(frame);
      track?.requestFrame?.();
      // MediaRecorder has no caller-supplied timestamps. Pace its compatibility
      // path at 24 fps; the primary WebCodecs path remains fully offline.
      await new Promise<void>((resolve) => window.setTimeout(resolve, 1000 / options.fps));
    }
    recorder.stop();
    await stopped;
  } finally {
    if (recorder.state !== 'inactive') recorder.stop();
    stream.getTracks().forEach((streamTrack) => streamTrack.stop());
  }

  const blob = new Blob(chunks, { type: recorder.mimeType || 'video/webm' });
  if (blob.size < 1024) throw new Error('The deterministic route preview was unexpectedly empty.');
  return {
    blob,
    encoder: 'media_recorder_webm',
    frameCount: frames.length,
    fps: options.fps,
    width: options.canvas.width,
    height: options.canvas.height,
  };
}

/**
 * Encode one or more canvases from a single fixed-timestep City Prompt route.
 *
 * WebCodecs is the preferred path because timestamps are supplied explicitly
 * and every track shares them. MediaRecorder is retained only so older
 * browsers can still prepare a pilot; it records the first track alone and
 * reports the others as dropped.
 */
export async function captureDeterministicVideoTracks(
  options: TracksCaptureOptions,
): Promise<DeterministicVideoTracksResult> {
  if (options.tracks.length === 0) throw new Error('A deterministic capture needs at least one track.');
  if (new Set(options.tracks.map((track) => track.id)).size !== options.tracks.length) {
    throw new Error('Deterministic capture track ids must be unique.');
  }
  const durationSeconds = clampPositiveInteger(
    options.durationSeconds ?? CITY_PROMPT_VIDEO_DURATION_SECONDS,
    CITY_PROMPT_VIDEO_DURATION_SECONDS,
  );
  const fps = clampPositiveInteger(options.fps ?? CITY_PROMPT_VIDEO_FPS, CITY_PROMPT_VIDEO_FPS);
  const frames = buildDeterministicVideoFrames(durationSeconds, fps);
  const bitrateOf = (track: DeterministicVideoTrack) => (
    clampPositiveInteger(track.bitrate ?? CITY_PROMPT_VIDEO_BITRATE, CITY_PROMPT_VIDEO_BITRATE)
  );

  const prepared: PreparedTrack[] = [];
  for (const track of options.tracks) {
    const config = await supportedEncoderConfiguration(track.canvas.width, track.canvas.height, fps, bitrateOf(track));
    if (!config) {
      prepared.length = 0;
      break;
    }
    prepared.push({ track, config });
  }

  if (prepared.length === options.tracks.length) {
    try {
      const tracks = await captureWithWebCodecs({ fps, renderFrame: options.renderFrame }, frames, prepared);
      return { tracks, encoder: 'webcodecs_h264', frameCount: frames.length, fps, droppedTrackIds: [] };
    } catch (error) {
      console.warn('[Video Render] Fixed-frame H.264 encoding failed; using the WebM compatibility path.', error);
    }
  }

  const [primary, ...rest] = options.tracks;
  const result = await captureWithMediaRecorder(
    { canvas: primary.canvas, fps, bitrate: bitrateOf(primary), renderFrame: options.renderFrame },
    frames,
  );
  return {
    tracks: { [primary.id]: result },
    encoder: 'media_recorder_webm',
    frameCount: frames.length,
    fps,
    droppedTrackIds: rest.map((track) => track.id),
  };
}

/** Encode a single canvas; kept for callers that only need the beauty track. */
export async function captureDeterministicVideo(
  options: CaptureOptions,
): Promise<DeterministicVideoCaptureResult> {
  const result = await captureDeterministicVideoTracks({
    tracks: [{ id: 'primary', canvas: options.canvas, bitrate: options.bitrate }],
    durationSeconds: options.durationSeconds,
    fps: options.fps,
    renderFrame: options.renderFrame,
  });
  return result.tracks.primary;
}
