// gta6-meme-x-01 entry program (Node 22, standard library only).
//
// The entry is a post on X: the meme picture and its text live there, and the
// house reads the post itself. All this program does is hand in the post's
// address: it reads POST.json from the repository root, checks that it parses
// and names a url, and writes it to the output directory as POST.json.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const sourcePath = join(botDir, 'POST.json');
const raw = readFileSync(sourcePath, 'utf8');

let post: unknown;
try {
  post = JSON.parse(raw);
} catch {
  console.error(`POST.json is not valid JSON: ${sourcePath}`);
  process.exit(1);
}

if (
  typeof post !== 'object' ||
  post === null ||
  typeof (post as { url?: unknown }).url !== 'string'
) {
  console.error('POST.json must be a JSON object with a "url" string.');
  process.exit(1);
}

const url = (post as { url: string }).url;
if (!/^https:\/\/(www\.|mobile\.)?(x|twitter)\.com\/[^/]+\/status\/\d+$/.test(url)) {
  console.error(`POST.json url is not an X post address: ${url}`);
  process.exit(1);
}

mkdirSync(outputDir, { recursive: true });
writeFileSync(join(outputDir, 'POST.json'), raw);
console.log(`handed in the post: ${url}`);
