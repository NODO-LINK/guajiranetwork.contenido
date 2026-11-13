// Revisión automática dentro de la página (la usan render_flyers.mjs y render_video.mjs).
// Devuelve una lista de problemas: textos fuera del lienzo / zona segura, legal ausente o invisible.
window.__revisar = function (opciones = {}) {
  const prob = [], W = 1080, H = 1920, SEG = { x0: 40, x1: 1040, y0: 200, y1: 1720 };
  const visible = el => { for (let e = el; e && e !== document.documentElement; e = e.parentElement) { const s = getComputedStyle(e); if (s.display === "none" || s.visibility === "hidden" || +s.opacity < .35) return false; } return true; };
  const textos = [...document.querySelectorAll("body *")].filter(e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()) && visible(e));
  const rango = document.createRange();
  for (const e of textos) {
    for (const n of e.childNodes) {
      if (n.nodeType !== 3 || !n.textContent.trim()) continue;
      rango.selectNodeContents(n); const r = rango.getBoundingClientRect(), txt = n.textContent.trim().slice(0, 40);
      if (r.width === 0 || r.height === 0) continue;
      if (r.left < -2 || r.right > W + 2 || r.top < -2 || r.bottom > H + 2) prob.push(`Texto fuera del lienzo: "${txt}"`);
      else if (!opciones.sinZona && (r.left < SEG.x0 || r.right > SEG.x1 || r.top < SEG.y0 || r.bottom > SEG.y1)) prob.push(`Texto fuera de la zona segura: "${txt}"`);
    }
    if (e.scrollWidth > e.clientWidth + 4 && getComputedStyle(e).overflow !== "visible") prob.push(`Texto cortado: "${e.textContent.trim().slice(0, 40)}"`);
  }
  const todo = textos.map(e => e.textContent).join(" ");
  if (!opciones.sinLegal) {
    if (!todo.includes("J-50842197-3")) prob.push("Falta el RIF J-50842197-3 (o no se ve)");
    if (!todo.includes("HGST-00852")) prob.push("Falta CONATEL HGST-00852 (o no se ve)");
  }
  const recorta = ["hidden", "clip"].includes(getComputedStyle(document.body).overflow) || ["hidden", "clip"].includes(getComputedStyle(document.documentElement).overflow);
  if (!recorta && (document.documentElement.scrollWidth > W + 2 || document.documentElement.scrollHeight > H + 2)) prob.push("La página es más grande que 1080×1920");
  return [...new Set(prob)];
};
