/* Guajira Network · componentes de marca y ayudas de animación.
   Todo devuelve HTML/SVG en texto. El logo NO se modifica. */
(function () {
  const CH = '<path d="M17 19l13 13-13 13" fill="none" stroke="#C4B5FD" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M33 19l13 13-13 13" fill="none" stroke="#fff" stroke-width="7.5" stroke-linecap="round" stroke-linejoin="round"/>';
  const GN = {
    DATOS: {
      razon: "GUAJIRA NETWORK 2107, C.A.", rif: "J-50842197-3", conatel: "HGST-00852",
      eslogan: "El hilo que conecta a la Guajira", zona: "San Rafael de El Moján",
      atencion: "0424-4825404", soporte: "0414-3666377", ig: "@guajiranetwork",
      web: "guajiranetwork.ve", correo: "atencionalcliente@guajiranetwork.ve",
      plan1: { mbps: 300, precio: 20 }, plan2: { mbps: 600, precio: 25 }
    },
    /** Logo exacto (cuadrado índigo + doble chevron) */
    logo(px = 86) { return `<svg width="${px}" height="${px}" viewBox="0 0 64 64" aria-label="Guajira Network"><rect width="64" height="64" rx="16" fill="#4F46E5"/>${CH}</svg>`; },
    /** Logo + GUAJIRA / NETWORK. tema: "claro" (fondo claro) | "oscuro" */
    marca(tema = "claro", px = 86) {
      const o = tema === "oscuro";
      return `<div class="gn-marca">${GN.logo(px)}<div class="wm"><b style="font-size:${px * .5}px;color:${o ? "#fff" : "#0B0A12"}">GUAJIRA</b><span style="font-size:${px * .245}px;color:${o ? "#C4B5FD" : "#8A8798"}">NETWORK</span></div></div>`;
    },
    /** RIF + CONATEL (obligatorio en todas las piezas). y por defecto 1640 (dentro de la zona segura) */
    legal(tema = "claro", y = 1640) {
      const c = tema === "oscuro" ? "#A9A3D9" : "#8A8798";
      return `<div class="gn-legal" style="top:${y}px;color:${c}">${GN.DATOS.razon} · RIF ${GN.DATOS.rif}<br>Habilitado por CONATEL · ${GN.DATOS.conatel}</div>`;
    },
    /** Ícono de WhatsApp (solo como indicador del canal) */
    waIcono(px = 60, color = "#25D366") { return `<svg width="${px}" height="${px}" viewBox="0 0 24 24"><path fill="${color}" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm5.8 14.1c-.2.7-1.4 1.3-2 1.4-.5.1-1.2.1-1.9-.1a17 17 0 0 1-1.7-.6 13.4 13.4 0 0 1-5.1-4.5c-.4-.5-1-1.5-1-2.8 0-1.3.7-2 1-2.3.2-.3.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 2c.1.2.1.4 0 .5l-.3.5-.4.4c-.1.1-.3.3-.1.6.2.3.7 1.2 1.6 2a7.3 7.3 0 0 0 2.3 1.4c.3.1.5.1.6-.1l.9-1.1c.2-.3.4-.2.6-.1l1.9.9c.3.1.5.2.5.3.1.1.1.7-.1 1.3Z"/></svg>`; },
    /** Píldora de contacto. tipo: "atencion" | "soporte" */
    contacto(tipo = "atencion") {
      const t = tipo === "soporte" ? ["SOPORTE E INSTALACIÓN", GN.DATOS.soporte] : ["ATENCIÓN AL CLIENTE", GN.DATOS.atencion];
      return `<div class="gn-wa"><i>${GN.waIcono(58)}</i><div><small>${t[0]}</small><strong>${t[1]}</strong></div></div>`;
    },
    /** Hilos de fibra (motivo de la marca). Varía y/amplitud/cantidad/color cada día. */
    hilos({ y = 1300, amp = 220, n = 3, color = "#C4B5FD", op = .3, grosor = 3, sep = 50, id = "h" } = {}) {
      let p = "";
      for (let i = 0; i < n; i++) { const yy = y + i * sep; p += `<path id="${id}${i}" d="M-80 ${yy} C 300 ${yy - amp}, 640 ${yy + amp * .9}, 1160 ${yy - amp * .7}" fill="none" stroke="${color}" stroke-opacity="${op * (1 - i * .25)}" stroke-width="${grosor}" stroke-linecap="round"/>`; }
      return `<svg class="abs" style="left:0;top:0" width="1080" height="1920">${p}</svg>`;
    },
    // ── Ayudas para video (render(t) determinista) ──
    cl: (x, a = 0, b = 1) => Math.min(b, Math.max(a, x)),
    prog: (t, a, b) => GN.cl((t - a) / (b - a)),
    eOut: x => 1 - Math.pow(1 - x, 3),
    eInOut: x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2,
    eBack: x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); },
    entra(el, t, a, d = .45, dy = 60, dx = 0) { const p = GN.eOut(GN.prog(t, a, a + d)); el.style.opacity = p; el.style.transform = `translate(${(1 - p) * dx}px,${(1 - p) * dy}px)`; },
    pop(el, t, a, d = .4) { const p = GN.prog(t, a, a + d); el.style.opacity = GN.cl(p * 3); el.style.transform = `scale(${p ? GN.eBack(p) : 0})`; },
    sale(el, t, a, d = .3) { const p = GN.prog(t, a, a + d); el.style.opacity = 1 - p; },
    escribir(el, texto, t, a, cps = 22) { const n = Math.floor(GN.cl((t - a) * cps, 0, texto.length)); el.textContent = texto.slice(0, n); return n >= texto.length; },
    contar(el, hasta, t, a, d = .9) { el.textContent = Math.round(hasta * GN.eOut(GN.prog(t, a, a + d))); }
  };
  window.GN = GN;
})();
