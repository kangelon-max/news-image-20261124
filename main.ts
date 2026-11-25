// main.ts — entrypoint for news-image-20261124 (Node 22, standard library
// only). The poster beside this file, entry.png, is the entry: gen.py drew
// it at build time. This program proves the image is a whole, well-formed
// PNG inside the competition gate (at most 1 MiB, at most 1024x1024) before
// shipping it: it walks every chunk, verifies each chunk's CRC-32, parses
// the IHDR fields, rejects trailing bytes after IEND, then copies the file
// to the output directory and reads the copy back to prove the bytes that
// landed are the bytes that were validated. A manifest.json describing the
// shipped files lets the entry be verified byte for byte.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';

const SRC = new URL('./entry.png', import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const MAX_BYTES = 1048576; // 1 MiB gate
const MAX_DIM = 1024; // gate: at most 1024 by 1024 pixels
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

function sha256(data: Buffer): string {
  return createHash('sha256').update(data).digest('hex');
}

// CRC-32 (PNG flavour: polynomial 0xEDB88320, reflected), table-driven so
// every chunk in the file can be checked without a dependency.
const CRC_TABLE = ((): Uint32Array => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(buf: Buffer, start: number, end: number): number {
  let c = 0xffffffff;
  for (let i = start; i < end; i++) {
    c = CRC_TABLE[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

const bytes = readFileSync(SRC);
console.log(`main.ts: read entry.png (${bytes.length} bytes)`);

if (bytes.length > MAX_BYTES) {
  fail(`entry.png is ${bytes.length} bytes, over the ${MAX_BYTES}-byte gate`);
}
if (bytes.length < PNG_MAGIC.length + 8) {
  fail('entry.png is too short to hold a PNG signature and one chunk');
}
for (let i = 0; i < PNG_MAGIC.length; i++) {
  if (bytes[i] !== PNG_MAGIC[i]) fail('entry.png does not start with the PNG magic bytes');
}

// Walk the chunk stream. Each chunk is length(4) type(4) data(length)
// crc(4); the CRC covers the type bytes plus the data. The walk must land
// exactly on the end of the file, with IHDR first and IEND last — anything
// else means the PNG is truncated, padded or not a PNG at all.
interface PngChunk {
  type: string;
  length: number;
}

const chunks: PngChunk[] = [];
let offset = PNG_MAGIC.length;
let width = 0;
let height = 0;
let bitDepth = 0;
let colorType = 0;
while (offset < bytes.length) {
  if (offset + 12 > bytes.length) {
    fail(`chunk header at offset ${offset} runs past the end of the file`);
  }
  const length = bytes.readUInt32BE(offset);
  const type = bytes.toString('ascii', offset + 4, offset + 8);
  const dataStart = offset + 8;
  const dataEnd = dataStart + length;
  const crcEnd = dataEnd + 4;
  if (crcEnd > bytes.length) {
    fail(`chunk ${type} at offset ${offset} claims ${length} data bytes and runs past the end of the file`);
  }
  const storedCrc = bytes.readUInt32BE(dataEnd);
  const computedCrc = crc32(bytes, offset + 4, dataEnd);
  if (storedCrc !== computedCrc) {
    fail(`chunk ${type} at offset ${offset} fails its CRC-32 check (stored ${storedCrc}, computed ${computedCrc})`);
  }
  if (chunks.length === 0) {
    if (type !== 'IHDR') fail(`first chunk is ${type}, not IHDR`);
    if (length !== 13) fail(`IHDR is ${length} bytes, not the required 13`);
    width = bytes.readUInt32BE(dataStart);
    height = bytes.readUInt32BE(dataStart + 4);
    bitDepth = bytes[dataStart + 8];
    colorType = bytes[dataStart + 9];
  }
  chunks.push({ type, length });
  offset = crcEnd;
  if (type === 'IEND') break;
}
if (chunks.length === 0 || chunks[chunks.length - 1].type !== 'IEND') {
  fail('entry.png has no IEND chunk');
}
if (chunks[chunks.length - 1].length !== 0) {
  fail('IEND chunk carries data; a well-formed IEND is empty');
}
if (offset !== bytes.length) {
  fail(`entry.png has ${bytes.length - offset} trailing bytes after IEND`);
}
console.log(
  `main.ts: chunk walk OK (${chunks.map((c) => `${c.type}:${c.length}`).join(', ')}); ` +
    'every CRC-32 verified',
);

if (width === 0 || height === 0) {
  fail(`entry.png has a degenerate IHDR dimension (${width}x${height})`);
}
if (width > MAX_DIM || height > MAX_DIM) {
  fail(`entry.png is ${width}x${height}, over the ${MAX_DIM}x${MAX_DIM} gate`);
}
if (![1, 2, 4, 8, 16].includes(bitDepth)) {
  fail(`entry.png has an invalid IHDR bit depth (${bitDepth})`);
}
if (![0, 2, 3, 4, 6].includes(colorType)) {
  fail(`entry.png has an invalid IHDR color type (${colorType})`);
}
console.log(`main.ts: IHDR ${width}x${height}, bit depth ${bitDepth}, color type ${colorType} — inside the gate`);

const srcHash = sha256(bytes);
console.log(`main.ts: entry.png sha256 ${srcHash}`);

mkdirSync(outDir, { recursive: true });
const dest = join(outDir, 'entry.png');
copyFileSync(SRC, dest);

// Read the copy back and prove it is byte-identical to the validated
// source; a short or corrupted write must never reach the judges.
const landed = readFileSync(dest);
if (landed.length !== bytes.length || sha256(landed) !== srcHash) {
  fail(`copied ${dest} does not match the validated entry.png`);
}
console.log(`main.ts: wrote ${dest} and verified its sha256 matches the source`);

// Manifest of the shipped files — path, bytes and sha256, sorted by
// codepoint. It carries no timestamp or environment value, so two runs
// write byte-identical manifests.
const repoDir = new URL('./', import.meta.url);
const names = ['LICENSE', 'README.md', 'entry.png', 'gen.py', 'main.ts'];
const entries = names
  .map((name) => {
    const data = readFileSync(new URL(name, repoDir));
    return {
      path: name,
      bytes: data.length,
      sha256: sha256(data),
    };
  })
  .sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
const manifest = JSON.stringify({ competition: 'news-image-20261124', files: entries }, null, 2) + '\n';
writeFileSync(join(outDir, 'manifest.json'), manifest);
console.log(`main.ts: wrote ${join(outDir, 'manifest.json')} (${entries.length} files)`);
