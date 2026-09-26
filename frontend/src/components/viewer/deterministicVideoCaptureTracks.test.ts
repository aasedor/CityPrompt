import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

const muxers: Array<{ chunks: unknown[]; finalized: boolean; width: number; height: number }> = [];

vi.mock('mp4-muxer', () => ({
  ArrayBufferTarget: class {
    buffer = new ArrayBuffer(4096);
  },
  Muxer: class {
    chunks: unknown[] = [];
    finalized = false;
    width: number;
    height: number;
    constructor(options: { video: { width: number; height: number } }) {
      this.width = options.video.width;
      this.height = options.video.height;
      muxers.push(this);
    }
    addVideoChunk(chunk: unknown) { this.chunks.push(chunk); }
    finalize() { this.finalized = true; }
  },
}));

import { captureDeterministicVideo, captureDeterministicVideoTracks } from './deterministicVideoCapture';

interface EncodedFrame { timestamp: number; keyFrame: boolean }

const encoders: Array<{ frames: EncodedFrame[]; closed: boolean; flushed: boolean }> = [];

class FakeVideoFrame {
  timestamp: number;
  closed = false;
  constructor(_source: unknown, init: { timestamp: number }) { this.timestamp = init.timestamp; }
  close() { this.closed = true; }
}

class FakeVideoEncoder {
  static supported = true;
  static isConfigSupported(config: unknown) { return Promise.resolve({ supported: FakeVideoEncoder.supported, config }); }
  state: 'configured' | 'closed' = 'configured';
  encodeQueueSize = 0;
  private readonly output: (chunk: unknown, metadata: unknown) => void;
  private readonly record = { frames: [] as EncodedFrame[], closed: false, flushed: false };
  constructor(init: { output: (chunk: unknown, metadata: unknown) => void }) {
    this.output = init.output;
    encoders.push(this.record);
  }
  configure() {}
  encode(frame: FakeVideoFrame, options: { keyFrame: boolean }) {
    this.record.frames.push({ timestamp: frame.timestamp, keyFrame: options.keyFrame });
    this.output({ timestamp: frame.timestamp }, {});
  }
  flush() { this.record.flushed = true; return Promise.resolve(); }
  close() { this.record.closed = true; this.state = 'closed'; }
  addEventListener() {}
}

function canvasOf(width: number, height: number): HTMLCanvasElement {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  return canvas;
}

describe('captureDeterministicVideoTracks', () => {
  beforeEach(() => {
    muxers.length = 0;
    encoders.length = 0;
    FakeVideoEncoder.supported = true;
    vi.stubGlobal('VideoEncoder', FakeVideoEncoder);
    vi.stubGlobal('VideoFrame', FakeVideoFrame);
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('renders each frame once and encodes every track with identical timestamps', async () => {
    const renderFrame = vi.fn();
    const result = await captureDeterministicVideoTracks({
      tracks: [
        { id: 'beauty', canvas: canvasOf(1280, 720) },
        { id: 'depth', canvas: canvasOf(1280, 720), bitrate: 6_000_000 },
      ],
      durationSeconds: 1,
      fps: 4,
      renderFrame,
    });

    expect(renderFrame).toHaveBeenCalledTimes(4);
    expect(renderFrame.mock.calls.map(([frame]) => frame.index)).toEqual([0, 1, 2, 3]);
    expect(result.encoder).toBe('webcodecs_h264');
    expect(result.droppedTrackIds).toEqual([]);
    expect(Object.keys(result.tracks)).toEqual(['beauty', 'depth']);
    expect(encoders).toHaveLength(2);
    expect(encoders[0].frames.map((frame) => frame.timestamp)).toEqual([0, 250_000, 500_000, 750_000]);
    expect(encoders[1].frames.map((frame) => frame.timestamp)).toEqual(encoders[0].frames.map((frame) => frame.timestamp));
    expect(encoders[0].frames[0].keyFrame).toBe(true);
    expect(encoders.every((encoder) => encoder.flushed && encoder.closed)).toBe(true);
    expect(muxers.every((muxer) => muxer.finalized && muxer.chunks.length === 4)).toBe(true);
    expect(result.tracks.depth.blob.type).toBe('video/mp4');
    expect(result.tracks.depth).toMatchObject({ frameCount: 4, fps: 4, width: 1280, height: 720 });
  });

  it('keeps the single-canvas wrapper shape', async () => {
    const result = await captureDeterministicVideo({
      canvas: canvasOf(640, 360),
      durationSeconds: 1,
      fps: 2,
      renderFrame: () => {},
    });
    expect(result).toMatchObject({ encoder: 'webcodecs_h264', frameCount: 2, fps: 2, width: 640, height: 360 });
  });

  it('rejects duplicate track ids before rendering anything', async () => {
    const renderFrame = vi.fn();
    await expect(captureDeterministicVideoTracks({
      tracks: [{ id: 'beauty', canvas: canvasOf(64, 36) }, { id: 'beauty', canvas: canvasOf(64, 36) }],
      renderFrame,
    })).rejects.toThrow('unique');
    expect(renderFrame).not.toHaveBeenCalled();
  });

  it('falls back to recording the first track only when WebCodecs is unavailable', async () => {
    FakeVideoEncoder.supported = false;
    const dataListeners: Array<(event: { data: Blob }) => void> = [];
    const stopListeners: Array<() => void> = [];
    class FakeMediaRecorder {
      static isTypeSupported() { return true; }
      state: 'recording' | 'inactive' = 'inactive';
      mimeType = 'video/webm';
      addEventListener(type: string, listener: (event: { data: Blob }) => void) {
        if (type === 'dataavailable') dataListeners.push(listener);
        if (type === 'stop') stopListeners.push(listener as unknown as () => void);
      }
      start() { this.state = 'recording'; }
      stop() {
        this.state = 'inactive';
        dataListeners.forEach((listener) => listener({ data: new Blob([new Uint8Array(2048)], { type: 'video/webm' }) }));
        stopListeners.forEach((listener) => listener());
      }
    }
    vi.stubGlobal('MediaRecorder', FakeMediaRecorder);
    const beauty = canvasOf(320, 180);
    const streamTrack = { requestFrame: vi.fn(), stop: vi.fn() };
    Object.defineProperty(beauty, 'captureStream', {
      value: () => ({ getVideoTracks: () => [streamTrack], getTracks: () => [streamTrack] }),
    });
    const renderFrame = vi.fn();

    const result = await captureDeterministicVideoTracks({
      tracks: [{ id: 'beauty', canvas: beauty }, { id: 'depth', canvas: canvasOf(320, 180) }],
      durationSeconds: 1,
      fps: 8,
      renderFrame,
    });

    expect(result.encoder).toBe('media_recorder_webm');
    expect(Object.keys(result.tracks)).toEqual(['beauty']);
    expect(result.droppedTrackIds).toEqual(['depth']);
    expect(renderFrame).toHaveBeenCalledTimes(8);
    expect(streamTrack.requestFrame).toHaveBeenCalledTimes(8);
    expect(result.tracks.beauty.blob.type).toBe('video/webm');
  });
});
