// Uso: node render_flyers.mjs <flyer1.html> <flyer2.html> <flyer3.html> <carpeta_salida>
// Cada HTML mide 1080x1920. Sale flyer1.jpg, flyer2.jpg, flyer3.jpg (calidad 95).
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright'); // usa la instalación global (NODE_PATH)
import path from 'path';
const args = process.argv.slice(2), out = args.pop();
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome' });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
for (const [i, f] of args.entries()) {
  await p.goto('file://' + path.resolve(f)); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(200);
  await p.screenshot({ path: `${out}/flyer${i + 1}.jpg`, type: 'jpeg', quality: 95 });
}
await b.close(); console.log('flyers:', args.length);
