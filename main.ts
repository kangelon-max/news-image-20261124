// main.ts — entrypoint for news-image-20261124 (Node 22, standard library
// only). The poster beside this file, entry.png, is the entry: gen.py drew
// it at build time. This program proves the image is a whole, well-formed
// PNG at exactly the competition size (1024x1024, at most 1 MiB) before
// shipping it: it walks every chunk, verifies each chunk's CRC-32, parses
// the IHDR fields, rejects a duplicate IHDR, requires at least one IDAT
// chunk, rejects trailing bytes after IEND, then copies the file to the
// output directory and reads the copy back to prove the bytes that landed
// are the bytes that were validated. A manifest.json describing the
// shipped files lets the entry be verified byte for byte, and the manifest
// itself is read back and re-verified against the files on disk.
//
// Round-4 hardening: the chunk walk also rejects timestamp-bearing
// ancillary chunks (tEXt, iTXt, zTXt, tIME), so no metadata that could
// carry a date or a free-text note can sneak into the shipped PNG and
// break byte-for-byte reproduction; and the manifest read-back now
// cross-checks the entry.png hash against the hash validated in stage 1
// and requires every manifest path to be unique, so a duplicated or
// swapped manifest entry is caught instead of silently shipped.
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';

const SRC = new URL('./entry.png', import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const MAX_BYTES = 1048576; // 1 MiB gate
const EXACT_DIM = 1024; // gate: the judged image is exactly 1024 by 1024
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

interface PngChunk {
  type: string;
  length: number;
  offset: number;
}

interface PngInfo {
  width: number;
  height: number;
  bitDepth: number;
  colorType: number;
  chunks: PngChunk[];
}

// Walk the chunk stream of one PNG buffer. Each chunk is length(4)
// type(4) data(length) crc(4); the CRC covers the type bytes plus the
// data. The walk must land exactly on the end of the buffer, with IHDR
// first and IEND last — anything else means the PNG is truncated, padded
// or not a PNG at all. `label` names the file in error messages.
function walkPng(bytes: Buffer, label: string): PngInfo {
  if (bytes.length < PNG_MAGIC.length + 8) {
    fail(`${label} is too short to hold a PNG signature and one chunk`);
  }
  for (let i = 0; i < PNG_MAGIC.length; i++) {
    if (bytes[i] !== PNG_MAGIC[i]) fail(`${label} does not start with the PNG magic bytes`);
  }
  const chunks: PngChunk[] = [];
  let offset = PNG_MAGIC.length;
  let width = 0;
  let height = 0;
  let bitDepth = 0;
  let colorType = 0;
  let idatCount = 0;
  while (offset < bytes.length) {
    if (offset + 12 > bytes.length) {
      fail(`chunk header at offset ${offset} in ${label} runs past the end of the file`);
    }
    const length = bytes.readUInt32BE(offset);
    const type = bytes.toString('ascii', offset + 4, offset + 8);
    const dataStart = offset + 8;
    const dataEnd = dataStart + length;
    const crcEnd = dataEnd + 4;
    if (crcEnd > bytes.length) {
      fail(`chunk ${type} at offset ${offset} in ${label} claims ${length} data bytes and runs past the end of the file`);
    }
    const storedCrc = bytes.readUInt32BE(dataEnd);
    const computedCrc = crc32(bytes, offset + 4, dataEnd);
    if (storedCrc !== computedCrc) {
      fail(`chunk ${type} at offset ${offset} in ${label} fails its CRC-32 check (stored ${storedCrc}, computed ${computedCrc})`);
    }
    if (chunks.length === 0) {
      if (type !== 'IHDR') fail(`first chunk in ${label} is ${type}, not IHDR`);
      if (length !== 13) fail(`IHDR in ${label} is ${length} bytes, not the required 13`);
      width = bytes.readUInt32BE(dataStart);
      height = bytes.readUInt32BE(dataStart + 4);
      bitDepth = bytes[dataStart + 8];
      colorType = bytes[dataStart + 9];
    } else if (type === 'IHDR') {
      fail(`${label} carries a second IHDR chunk at offset ${offset}`);
    }
    if (type === 'IDAT') idatCount++;
    if (type === 'tEXt' || type === 'iTXt' || type === 'zTXt' || type === 'tIME') {
      fail(`${label} carries a ${type} chunk at offset ${offset}; timestamp-bearing or free-text metadata must never ship in the entry PNG`);
    }
    chunks.push({ type, length, offset });
    offset = crcEnd;
    if (type === 'IEND') break;
  }
  if (chunks.length === 0 || chunks[chunks.length - 1].type !== 'IEND') {
    fail(`${label} has no IEND chunk`);
  }
  if (chunks[chunks.length - 1].length !== 0) {
    fail(`IEND chunk in ${label} carries data; a well-formed IEND is empty`);
  }
  if (offset !== bytes.length) {
    fail(`${label} has ${bytes.length - offset} trailing bytes after IEND`);
  }
  if (idatCount === 0) {
    fail(`${label} carries no IDAT chunk, so it holds no image data`);
  }
  if (width === 0 || height === 0) {
    fail(`${label} has a degenerate IHDR dimension (${width}x${height})`);
  }
  if (![1, 2, 4, 8, 16].includes(bitDepth)) {
    fail(`${label} has an invalid IHDR bit depth (${bitDepth})`);
  }
  if (![0, 2, 3, 4, 6].includes(colorType)) {
    fail(`${label} has an invalid IHDR color type (${colorType})`);
  }
  return { width, height, bitDepth, colorType, chunks };
}

// ------------------------------------------------------------------ stage 1
// Read and validate the entry image.

const bytes = readFileSync(SRC);
console.log(`main.ts: stage 1 — read entry.png (${bytes.length} bytes)`);

if (bytes.length > MAX_BYTES) {
  fail(`entry.png is ${bytes.length} bytes, over the ${MAX_BYTES}-byte gate`);
}
const info = walkPng(bytes, 'entry.png');
console.log(
  `main.ts: stage 1 — chunk walk OK (${info.chunks.map((c) => `${c.type}:${c.length}@${c.offset}`).join(', ')}); ` +
    'every CRC-32 verified',
);
console.log(
  `main.ts: stage 1 — IHDR ${info.width}x${info.height}, bit depth ${info.bitDepth}, color type ${info.colorType}`,
);
if (info.width !== EXACT_DIM || info.height !== EXACT_DIM) {
  fail(`entry.png is ${info.width}x${info.height}, not the required ${EXACT_DIM}x${EXACT_DIM}`);
}

const srcHash = sha256(bytes);
console.log(`main.ts: stage 1 — entry.png sha256 ${srcHash}`);

// ------------------------------------------------------------------ stage 2
// Copy the validated bytes to the output directory and prove the copy.

mkdirSync(outDir, { recursive: true });
const dest = join(outDir, 'entry.png');
copyFileSync(SRC, dest);

// Read the copy back and prove it is byte-identical to the validated
// source; a short or corrupted write must never reach the judges.
const landed = readFileSync(dest);
if (landed.length !== bytes.length || sha256(landed) !== srcHash) {
  fail(`copied ${dest} does not match the validated entry.png`);
}
// A hash match alone does not prove the copy is a readable PNG: walk its
// chunks independently, so a truncated or re-encoded copy is caught even
// if the bytes somehow still hashed the same (they cannot — but the walk
// also proves the landed file parses on its own).
const landedInfo = walkPng(landed, dest);
if (landedInfo.width !== info.width || landedInfo.height !== info.height) {
  fail(`copied ${dest} parses as ${landedInfo.width}x${landedInfo.height}, not ${info.width}x${info.height}`);
}
console.log(
  `main.ts: stage 2 — wrote ${dest}, sha256 matches, and its own chunk walk parses ` +
    `(${landedInfo.chunks.length} chunks, IHDR ${landedInfo.width}x${landedInfo.height})`,
);

// ------------------------------------------------------------------ stage 3
// Manifest of the shipped files — path, bytes and sha256, sorted by
// codepoint. It carries no timestamp or environment value, so two runs
// write byte-identical manifests. The manifest is then read back and
// every entry is re-verified against the file on disk.

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
const manifestPath = join(outDir, 'manifest.json');
const manifest = JSON.stringify({ competition: 'news-image-20261124', files: entries }, null, 2) + '\n';
writeFileSync(manifestPath, manifest);
console.log(`main.ts: stage 3 — wrote ${manifestPath} (${entries.length} files)`);

const parsed = JSON.parse(readFileSync(manifestPath, 'utf8')) as {
  competition: string;
  files: { path: string; bytes: number; sha256: string }[];
};
if (parsed.competition !== 'news-image-20261124') {
  fail(`manifest read-back has competition ${parsed.competition}, not news-image-20261124`);
}
if (parsed.files.length !== entries.length) {
  fail(`manifest read-back lists ${parsed.files.length} files, expected ${entries.length}`);
}
for (const entry of parsed.files) {
  const data = readFileSync(new URL(entry.path, repoDir));
  if (data.length !== entry.bytes || sha256(data) !== entry.sha256) {
    fail(`manifest entry ${entry.path} does not match the file on disk`);
  }
}
// The manifest's entry.png hash must be the hash validated in stage 1:
// a manifest that names different bytes than the validated image is a
// swapped manifest, even if every entry matches its own file on disk.
const manifestPng = parsed.files.find((entry) => entry.path === 'entry.png');
if (manifestPng === undefined) {
  fail('manifest has no entry.png entry');
}
if (manifestPng.sha256 !== srcHash) {
  fail(`manifest entry.png sha256 ${manifestPng.sha256} does not match the validated image ${srcHash}`);
}
const seenPaths = new Set<string>();
for (const entry of parsed.files) {
  if (seenPaths.has(entry.path)) {
    fail(`manifest lists ${entry.path} twice`);
  }
  seenPaths.add(entry.path);
}
for (let i = 1; i < parsed.files.length; i++) {
  if (!(parsed.files[i - 1].path < parsed.files[i].path)) {
    fail(`manifest entries are not sorted by codepoint at ${parsed.files[i].path}`);
  }
}
const totalBytes = parsed.files.reduce((sum, entry) => sum + entry.bytes, 0);
console.log(`main.ts: stage 3 — manifest read-back verified (${parsed.files.length} entries re-hashed, sorted by codepoint, ${totalBytes} total bytes)`);
console.log('main.ts: done — entry.png is valid, copied and manifested');
