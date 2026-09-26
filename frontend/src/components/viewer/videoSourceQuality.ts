export interface VideoSourceFrameQuality {
  edgeRatio: number;
  dominantColorRatio: number;
  usable: boolean;
}

const MIN_EDGE_RATIO = 0.2;
const MAX_DOMINANT_COLOR_RATIO = 0.47;

/** Detect catastrophic near-field source frames before a provider can turn
 * clipped Google photogrammetry or a blank surface into invented buildings.
 * This is deliberately conservative: a paid enhancement is allowed only
 * when every sampled source frame contains enough architectural structure. */
export function assessVideoSourceFramePixels(
  pixels: Uint8ClampedArray,
  width: number,
  height: number,
): VideoSourceFrameQuality {
  if (pixels.length !== width * height * 4 || width < 2 || height < 2) {
    throw new Error('Video source quality requires a valid RGBA frame.');
  }
  const luminance = new Float32Array(width * height);
  const colorBins = new Map<number, number>();
  let dominantColorCount = 0;
  for (let pixel = 0; pixel < width * height; pixel += 1) {
    const offset = pixel * 4;
    const red = pixels[offset];
    const green = pixels[offset + 1];
    const blue = pixels[offset + 2];
    luminance[pixel] = 0.2126 * red + 0.7152 * green + 0.0722 * blue;
    const colorKey = ((red >> 5) << 6) | ((green >> 5) << 3) | (blue >> 5);
    const colorCount = (colorBins.get(colorKey) ?? 0) + 1;
    colorBins.set(colorKey, colorCount);
    dominantColorCount = Math.max(dominantColorCount, colorCount);
  }

  let edgePixels = 0;
  for (let y = 1; y < height; y += 1) {
    for (let x = 1; x < width; x += 1) {
      const index = y * width + x;
      const edgeStrength = Math.abs(luminance[index] - luminance[index - 1])
        + Math.abs(luminance[index] - luminance[index - width]);
      if (edgeStrength > 24) edgePixels += 1;
    }
  }
  const edgeRatio = edgePixels / ((width - 1) * (height - 1));
  const dominantColorRatio = dominantColorCount / (width * height);
  return {
    edgeRatio,
    dominantColorRatio,
    usable: edgeRatio >= MIN_EDGE_RATIO
      && dominantColorRatio <= MAX_DOMINANT_COLOR_RATIO,
  };
}

async function decodeFramePixels(dataUrl: string): Promise<ImageData> {
  const image = new Image();
  image.decoding = 'async';
  image.src = dataUrl;
  await image.decode();
  const canvas = document.createElement('canvas');
  canvas.width = 96;
  canvas.height = 54;
  const context = canvas.getContext('2d', { willReadFrequently: true });
  if (!context) throw new Error('The browser could not inspect the street source frame.');
  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  return context.getImageData(0, 0, canvas.width, canvas.height);
}

/** Report unusable near-field frames instead of aborting the capture.
 *
 * Throwing here used to kill the whole route capture, which also destroyed the
 * FREE local preview — so a student could not even look at their own route to
 * understand the problem. The advice is worth giving; withholding the picture
 * is not. Callers surface these as warnings and keep the paid provider call
 * behind an explicit confirmation. */
export async function inspectNearFieldVideoSourceQuality(
  framesBase64: string[],
): Promise<string[]> {
  const warnings: string[] = [];
  for (let index = 0; index < framesBase64.length; index += 1) {
    const imageData = await decodeFramePixels(framesBase64[index]);
    const quality = assessVideoSourceFramePixels(
      imageData.data,
      imageData.width,
      imageData.height,
    );
    if (!quality.usable) {
      warnings.push(
        `Frame ${index + 1} has clipped or blank foreground geometry. `
        + 'Move that route vertex farther from the facade, or from coarse Google photogrammetry, for a sharper result.',
      );
    }
  }
  return warnings;
}
