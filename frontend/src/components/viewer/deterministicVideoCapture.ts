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

interface CaptureOptions {
  canvas: HTMLCanvasElement;
  durationSeconds?: number;
  fps?: number;
  bitrate?: number;
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

async function captureWithWebCodecs(
  options: Required<Omit<CaptureOptions, 'renderFrame'>> & Pick<CaptureOptions, 'renderFrame'>,
  frames: DeterministicVideoFrame[],
  config: VideoEncoderConfig,
): Promise<DeterministicVideoCaptureResult> {
  const { VideoEncoderClass, VideoFrameClass } = webCodecsGlobals();
  if (!VideoEncoderClass || !VideoFrameClass) throw new Error('WebCodecs became unavailable during capture.');

  const target = new ArrayBufferTarget();
  const muxer = new Muxer({
    target,
    video: {
      codec: 'avc',
      width: options.canvas.width,
      height: options.canvas.height,
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

  try {
    for (const frame of frames) {
      await options.renderFrame(frame);
      if (encoderError) throw encoderError;
      await waitForEncoderCapacity(encoder);
      const videoFrame = new VideoFrameClass(options.canvas, {
        timestamp: frame.timestampMicroseconds,
        duration: frame.durationMicroseconds,
        alpha: 'discard',
      });
      try {
        encoder.encode(videoFrame, {
          keyFrame: frame.index === 0 || frame.index % (options.fps * 2) === 0,
        });
      } finally {
        videoFrame.close();
      }
    }
    await encoder.flush();
    if (encoderError) throw encoderError;
    muxer.finalize();
  } finally {
    if (encoder.state !== 'closed') encoder.close();
  }

  const blob = new Blob([target.buffer], { type: 'video/mp4' });
  if (blob.size < 1024) throw new Error('The fixed-frame H.264 route render was unexpectedly empty.');
  return {
    blob,
    encoder: 'webcodecs_h264',
    frameCount: frames.length,
    fps: options.fps,
    width: options.canvas.width,
    height: options.canvas.height,
  };
}

async function captureWithMediaRecorder(
  options: Required<Omit<CaptureOptions, 'renderFrame'>> & Pick<CaptureOptions, 'renderFrame'>,
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
 * Encode a fixed-timestep City Prompt route locally.
 *
 * WebCodecs is the preferred path because timestamps are supplied explicitly;
 * MediaRecorder is retained only so older browsers can still prepare a pilot.
 */
export async function captureDeterministicVideo(
  options: CaptureOptions,
): Promise<DeterministicVideoCaptureResult> {
  const durationSeconds = clampPositiveInteger(
    options.durationSeconds ?? CITY_PROMPT_VIDEO_DURATION_SECONDS,
    CITY_PROMPT_VIDEO_DURATION_SECONDS,
  );
  const fps = clampPositiveInteger(options.fps ?? CITY_PROMPT_VIDEO_FPS, CITY_PROMPT_VIDEO_FPS);
  const bitrate = clampPositiveInteger(options.bitrate ?? CITY_PROMPT_VIDEO_BITRATE, CITY_PROMPT_VIDEO_BITRATE);
  const completeOptions = { ...options, durationSeconds, fps, bitrate };
  const frames = buildDeterministicVideoFrames(durationSeconds, fps);
  const config = await supportedEncoderConfiguration(
    options.canvas.width,
    options.canvas.height,
    fps,
    bitrate,
  );

  if (config) {
    try {
      return await captureWithWebCodecs(completeOptions, frames, config);
    } catch (error) {
      console.warn('[Video Render] Fixed-frame H.264 encoding failed; using the WebM compatibility path.', error);
    }
  }
  return captureWithMediaRecorder(completeOptions, frames);
}
