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
await p.addScriptTag({ path: path.join(path.dirname(new URL(import.meta.url).pathname), 'revisar.js') });
const avisos = new Set();
for (let i = 0; i < N; i++) {
  const t = i / 30; await p.evaluate(t => window.render(t), t);
  if (i % 15 === 0 && t > .8 && t < +dur - .8) (await p.evaluate(() => window.__revisar())).forEach(x => avisos.add(`${x} (≈${t.toFixed(1)} s)`));
  await p.screenshot({ path: `${out}/${String(i).padStart(4, '0')}.png` });
}
console.log(avisos.size ? 'REVISIÓN VIDEO ⚠\n  ' + [...avisos].slice(0, 25).join('\n  ') : 'Revisión del video OK');
await b.close(); console.log('frames:', N);
