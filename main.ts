// main.ts — entrypoint for news-image-20261124 (Node 22, standard library
// only). The poster beside this file, entry.png, is the entry: gen.py drew
// it at build time. This program checks the image against the competition
// gate (a whole PNG, at most 1 MiB, at most 1024x1024) and copies it to the
// output directory as entry.png, together with a manifest.json describing
// the shipped files so the entry can be verified byte for byte.
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

const bytes = readFileSync(SRC);
console.log(`main.ts: read entry.png (${bytes.length} bytes)`);

if (bytes.length > MAX_BYTES) {
  fail(`entry.png is ${bytes.length} bytes, over the ${MAX_BYTES}-byte gate`);
}
for (let i = 0; i < PNG_MAGIC.length; i++) {
  if (bytes[i] !== PNG_MAGIC[i]) fail('entry.png does not start with the PNG magic bytes');
}

// IHDR sits right after the 8-byte signature: length(4) type(4) then
// width and height as big-endian uint32 at offsets 16 and 20.
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
console.log(`main.ts: IHDR ${width}x${height}`);
if (width > MAX_DIM || height > MAX_DIM) {
  fail(`entry.png is ${width}x${height}, over the ${MAX_DIM}x${MAX_DIM} gate`);
}
if (bytes.toString('ascii', 12, 16) !== 'IHDR') {
  fail('entry.png has no IHDR chunk right after the signature');
}
// A whole PNG ends with the 12-byte IEND chunk; a truncated file fails here.
const IEND = [0, 0, 0, 0, 0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82];
const tail = bytes.subarray(bytes.length - IEND.length);
if (!IEND.every((b, i) => tail[i] === b)) {
  fail('entry.png does not end with the IEND chunk');
}
console.log('main.ts: chunk structure OK (IHDR first, IEND last)');

mkdirSync(outDir, { recursive: true });
const dest = join(outDir, 'entry.png');
copyFileSync(SRC, dest);
console.log(`main.ts: wrote ${dest}`);

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
      sha256: createHash('sha256').update(data).digest('hex'),
    };
  })
  .sort((a, b) => (a.path < b.path ? -1 : a.path > b.path ? 1 : 0));
const manifest = JSON.stringify({ competition: 'news-image-20261124', files: entries }, null, 2) + '\n';
writeFileSync(join(outDir, 'manifest.json'), manifest);
console.log(`main.ts: wrote ${join(outDir, 'manifest.json')} (${entries.length} files)`);
