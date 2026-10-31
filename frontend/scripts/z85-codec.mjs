// Z85 v1 alphabet and unsigned big-endian words: https://rfc.zeromq.org/spec/32/
// Deflate frames use at most three declared zero bytes of application padding.
export const Z85_ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ.-:+=^!/*?&<>()[]{}@%$#';

export function encodeZ85(bytes) {
  if (bytes.length % 4) throw new Error('Z85 source length must be divisible by four');
  const view = new DataView(bytes.buffer,bytes.byteOffset,bytes.byteLength);
  const output = new Array(bytes.length / 4 * 5);
  for (let offset = 0; offset < bytes.length; offset += 4) {
    let word = view.getUint32(offset,false);
    for (let digit = 4; digit >= 0; digit--) {
      output[offset / 4 * 5 + digit] = Z85_ALPHABET[word % 85];
      word = Math.floor(word / 85);
    }
  }
  return output.join('');
}

/** This exact function is embedded in the pure browser decoder by the packer. */
export function decodeZ85(encoded, byteLength = encoded.length / 5 * 4) {
  const size = encoded.length / 5 * 4;
  if (typeof encoded !== 'string' || encoded.length % 5 || !Number.isInteger(byteLength)
    || byteLength < 0 || byteLength > size || byteLength <= size - 4) throw new Error('Invalid Z85 transport length');
  const lookup = new Uint8Array(128).fill(255);
  for (let index = 0; index < Z85_ALPHABET.length; index++) lookup[Z85_ALPHABET.charCodeAt(index)] = index;
  const bytes = new Uint8Array(size), view = new DataView(bytes.buffer);
  for (let offset = 0; offset < encoded.length; offset += 5) {
    let word = 0;
    for (let digit = 0; digit < 5; digit++) {
      const char = encoded.charCodeAt(offset + digit);
      if (char >= 128 || lookup[char] === 255) throw new Error('Invalid Z85 transport character');
      word = word * 85 + lookup[char];
    }
    if (word > 0xffffffff) throw new Error('Invalid Z85 transport word');
    view.setUint32(offset / 5 * 4,word,false);
  }
  for (let index = byteLength; index < size; index++) if (bytes[index] !== 0) throw new Error('Invalid Z85 transport padding');
  return bytes.subarray(0,byteLength);
}
