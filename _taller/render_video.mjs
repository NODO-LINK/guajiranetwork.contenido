// Uso: node render_video.mjs <anim.html> <segundos> <carpeta_frames>
// El HTML debe exponer window.render(t) (t en segundos) y medir 1080x1920.
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright'); // usa la instalación global (NODE_PATH)
import fs from 'fs'; import path from 'path';
const [html, dur, out] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
await p.goto('file://' + path.resolve(html)); await p.evaluate(() => document.fonts.ready);
const N = Math.round(+dur * 30);
for (let i = 0; i < N; i++) { await p.evaluate(t => window.render(t), i / 30); await p.screenshot({ path: `${out}/${String(i).padStart(4, '0')}.png` }); }
await b.close(); console.log('frames:', N);
