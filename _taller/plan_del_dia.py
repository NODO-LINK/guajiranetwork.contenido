"""Plan del día: decide QUÉ se hace hoy para que cada día sea distinto (sin repetir) y con sentido.

Uso:  python3 _taller/plan_del_dia.py [AAAA-MM-DD] [--guardar]
  - Sin fecha usa hoy (America/Caracas).
  - --guardar anota el plan en _taller/plan_usado.json (hazlo al publicar).
Imprime un JSON con el brief del video, la música y los 3 flyers.
"""
import json, sys, random, datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

AQUI = Path(__file__).parent
USADO = AQUI / "plan_usado.json"

# ───────── Ángulos (temas). Solo datos reales de MARCA.md ─────────
ANG = {
 "plan1":         dict(grupo="planes", idea="Plan 1: 300 Mbps por $20/mes", datos=["Plan 1", "300 Mbps", "$20/mes", "fibra óptica"],
                       ganchos=["300 megas por $20 al mes", "Tu casa conectada por $20", "Plan 1: 300 Mbps de fibra", "Arranca con 300 Mbps"]),
 "plan2":         dict(grupo="planes", idea="Plan 2: 600 Mbps por $25/mes", datos=["Plan 2", "600 Mbps", "$25/mes", "fibra óptica"],
                       ganchos=["600 Mbps. Así de simple.", "El doble de velocidad: Plan 2", "Para la casa full de equipos: 600 Mbps", "¿Quieres más? 600 Mbps"]),
 "comparar":      dict(grupo="planes", idea="Comparar Plan 1 y Plan 2", datos=["300 Mbps $20", "600 Mbps $25"],
                       ganchos=["¿300 o 600? Tú eliges", "Dos planes, una sola fibra", "Elige tu velocidad", "¿Cuál va contigo?"]),
 "cambio_plan":   dict(grupo="planes", idea="Pásate al Plan 2 escribiendo a Atención al cliente", datos=["Plan 2 600 Mbps $25", "0424-4825404 (cambios de plan)"],
                       ganchos=["¿Te quedó corto el Plan 1?", "Sube a 600 Mbps cuando quieras", "Cambiar de plan es por WhatsApp"]),
 "fibra":         dict(grupo="servicio", idea="Internet por fibra óptica en San Rafael de El Moján", datos=["fibra óptica", "San Rafael de El Moján"],
                       ganchos=["La fibra llegó a San Rafael de El Moján", "Internet por fibra óptica, aquí mismo", "Fibra hasta tu casa"]),
 "cobertura":     dict(grupo="servicio", idea="Cobertura en San Rafael de El Moján", datos=["San Rafael de El Moján", "0414-3666377 (instalación)"],
                       ganchos=["Conectando San Rafael de El Moján", "¿Vives en San Rafael de El Moján?", "Tu zona, tu fibra"]),
 "instalacion":   dict(grupo="servicio", idea="Pide tu instalación por WhatsApp de soporte e instalación", datos=["0414-3666377"],
                       ganchos=["¿Quieres instalar? Escríbenos", "Tu instalación empieza con un mensaje", "Instalaciones: 0414-3666377"]),
 "soporte":       dict(grupo="soporte", idea="Soporte e instalación (fallas)", datos=["0414-3666377"],
                       ganchos=["¿Algo falla? Escríbenos", "Soporte por WhatsApp", "Un número para soporte e instalación"]),
 "consejo_reinicio": dict(grupo="consejos", idea="Antes de reportar lentitud: reinicia el router (apágalo 30 s), revisa que los cables estén bien conectados y acércate al router; si sigue, escribe a soporte", datos=["0414-3666377"],
                       ganchos=["¿Internet lento? Prueba esto primero", "3 pasos antes de escribirnos", "El truco de los 30 segundos"]),
 "consejo_router": dict(grupo="consejos", idea="Ubica el router en un lugar alto, central y despejado, lejos de paredes gruesas y del microondas", datos=["0414-3666377"],
                       ganchos=["¿Dónde pones el router?", "Tu WiFi rinde más si…", "Un buen lugar para tu router"]),
 "consejo_clave": dict(grupo="consejos", idea="Cuida tu clave WiFi: no la compartas con desconocidos; si necesitas ayuda, escribe a soporte", datos=["0414-3666377"],
                       ganchos=["Tu clave WiFi es solo tuya", "¿Quién más usa tu WiFi?", "Protege tu conexión"]),
 "atencion":      dict(grupo="atencion", idea="Atención al cliente: pagos, cambios de plan y consultas", datos=["0424-4825404"],
                       ganchos=["Estamos para atenderte", "Pagos, planes y consultas", "¿Dudas? Escríbenos"]),
 "reporta_pago":  dict(grupo="atencion", idea="Reporta tu pago en la web guajiranetwork.ve", datos=["guajiranetwork.ve", "0424-4825404"],
                       ganchos=["Reporta tu pago en guajiranetwork.ve", "¿Pagaste? Repórtalo en la web", "Tu pago, en 1 minuto"]),
 "usd_bs":        dict(grupo="atencion", idea="Pagas en dólares o su equivalente en bolívares", datos=["USD o equivalente en Bs", "0424-4825404"],
                       ganchos=["Paga en $ o en Bs", "Dólares o su equivalente en bolívares", "Pagar es fácil"]),
 "recordatorio_pago": dict(grupo="atencion", idea="Recordatorio: el pago es antes del día 4; repórtalo en guajiranetwork.ve", datos=["día 4", "guajiranetwork.ve", "0424-4825404"],
                       ganchos=["Recuerda: tu pago antes del día 4", "No te quedes sin internet", "Ya estamos a inicio de mes"], solo_dias=[1, 2, 3]),
 "usos_casa":     dict(grupo="usos", idea="Para estudiar, trabajar y ver tus series desde casa", datos=["300 Mbps", "600 Mbps"],
                       ganchos=["Clases, trabajo y series", "Toda la casa conectada", "Una conexión para todo"]),
 "usos_gamer":    dict(grupo="usos", idea="Para jugar en línea: conoce el Plan 2 de 600 Mbps", datos=["600 Mbps", "$25/mes"],
                       ganchos=["¿Gamer? Esto es para ti", "Juega con fibra", "600 Mbps para tu partida"]),
 "usos_familia":  dict(grupo="usos", idea="Todos conectados en casa al mismo tiempo: elige tu plan", datos=["300 Mbps $20", "600 Mbps $25"],
                       ganchos=["Todos conectados, al mismo tiempo", "Para toda la familia", "Cada quien en lo suyo"]),
 "instagram":     dict(grupo="comunidad", idea="Síguenos en Instagram @guajiranetwork", datos=["@guajiranetwork"],
                       ganchos=["¿Ya nos sigues?", "Estamos en Instagram", "Síguenos: @guajiranetwork"]),
 "web":           dict(grupo="comunidad", idea="Visita guajiranetwork.ve (planes y reporte de pagos)", datos=["guajiranetwork.ve"],
                       ganchos=["Todo en guajiranetwork.ve", "Visita nuestra web", "Planes y pagos en la web"]),
 "correo":        dict(grupo="comunidad", idea="También nos escribes por correo", datos=["atencionalcliente@guajiranetwork.ve"],
                       ganchos=["¿Prefieres correo?", "Escríbenos también por correo"]),
 "empresa_local": dict(grupo="marca", idea="Empresa de la Guajira habilitada por CONATEL (HGST-00852)", datos=["GUAJIRA NETWORK 2107, C.A.", "CONATEL HGST-00852"],
                       ganchos=["Empresa habilitada por CONATEL", "De aquí, para la Guajira", "Somos de aquí"]),
 "eslogan":       dict(grupo="marca", idea="El hilo que conecta a la Guajira", datos=["eslogan"],
                       ganchos=["El hilo que conecta a la Guajira", "Un hilo nos conecta", "Juntos, conectados"]),
}

# Preferencia por día de la semana (0 = lunes)
SEMANA = {0: ["planes", "servicio"], 1: ["soporte", "consejos"], 2: ["planes", "usos"], 3: ["atencion", "consejos"],
          4: ["usos", "planes"], 5: ["comunidad", "servicio"], 6: ["marca", "usos"]}

VIDEO = {
 "tipografia_cinetica": "Palabras grandes que entran, se empujan y cambian de tamaño al ritmo; 1 idea por frase.",
 "velocimetro": "Un medidor/arco que sube hasta la velocidad del plan con el número contando; termina en el precio.",
 "hilo_de_luz": "Un hilo de fibra luminoso recorre la pantalla y 'escribe' o une los elementos de cada escena.",
 "checklist": "Lista que se va marcando con checks animados (ideal para consejos o para lo que incluye el servicio).",
 "chat": "Burbujas de conversación genéricas (no imitar la interfaz de WhatsApp) que preguntan y responden; cierra con los números.",
 "barra_carga": "Barra de progreso que se llena por etapas; cada etapa revela un dato; al 100 % aparece el logo.",
 "pantalla_dividida": "Pantalla partida en dos que compara (p. ej. 300 vs 600) y se une al final.",
 "mosaico": "Cuadrícula de tarjetas que voltean una por una revelando datos; se ordenan en el cierre.",
 "maquina_escribir": "Texto que se escribe letra a letra con cursor, frases cortas y pausas con golpe musical.",
 "zoom_tunel": "Zoom continuo hacia el centro: cada escena aparece dentro de la anterior (efecto túnel de fibra).",
}
FLYER = {
 "numero_gigante": "Un número enorme (300 / 600 / 4 / 30 s) domina la pieza; texto mínimo alrededor.",
 "comparativa_columnas": "Dos columnas lado a lado con jerarquía clara y un ganador visual sin desmerecer el otro.",
 "tarjeta_central": "Fondo de color con una tarjeta blanca centrada (sombra suave) que contiene el mensaje.",
 "lista_checks": "Título + 3 líneas con checks; ideal para consejos o para 'pagos / cambios / consultas'.",
 "titular_editorial": "Titular enorme a sangre en 3–4 líneas, alineado a la izquierda, estilo revista.",
 "banda_diagonal": "Una banda diagonal de color cruza la pieza con el dato clave encima.",
 "pasos_numerados": "1-2-3 grandes con texto breve; para consejos o para reportar el pago.",
 "poster_tipografico": "Solo tipografía en distintos pesos y tamaños formando un bloque compacto.",
 "marco_hilo": "El hilo de fibra enmarca el contenido (sale de un borde y abraza el texto).",
 "minimal_blanco": "Mucho blanco, un solo acento índigo, logo y un mensaje corto.",
 "noche_neon": "Fondo casi negro con líneas lila luminosas y textos blancos de alto contraste.",
 "burbuja_mensaje": "Una gran burbuja de mensaje con la pregunta del cliente y la respuesta abajo.",
}
PALETAS = {
 "claro_lila": "Fondo blanco/lila muy suave, textos negros, acentos índigo.",
 "noche": "Fondo #0B0A12→#2E1065, textos blancos, acentos lila.",
 "degradado_indigo": "Degradado #1E1B4B→#4338CA→#6D28D9, textos blancos.",
 "morado_intenso": "Morado #6D28D9 dominante con blanco y lila.",
 "blanco_negro_acento": "Blanco y negro puros con un solo acento índigo.",
 "lila_suave": "Lila #EDE9FE dominante, textos índigo profundo.",
}
MUSICA = {"electro": (116, 124), "dembow": (92, 100), "gaitera": (108, 116), "lofi": (80, 88), "house": (120, 126), "trap": (136, 144)}
TONO = {"cercano": "Cercano y zuliano, sin exagerar (\"¿Qué más, vecino?\", \"Pendiente…\").",
        "directo": "Directo e informativo: dato + acción.",
        "entusiasta": "Entusiasta, con energía (signos de exclamación con moderación).",
        "util": "Útil y educativo: primero ayudar, después vender.",
        "festivo": "Festivo y cálido para fechas especiales."}

def nth_weekday(y, m, weekday, n):  # n-ésimo día de la semana del mes
    d = dt.date(y, m, 1); d += dt.timedelta((weekday - d.weekday()) % 7); return d + dt.timedelta(weeks=n - 1)

def especial(d):
    """Fechas reales (sin política ni religión). Devuelve (nombre, guía) o None."""
    y = d.year
    fijos = {(1, 1): "Año Nuevo", (12, 31): "Fin de año", (12, 24): "Nochebuena", (12, 25): "Navidad",
             (2, 14): "Día del Amor y la Amistad", (5, 1): "Día del Trabajador", (5, 17): "Día Mundial del Internet",
             (11, 18): "Feria en el Zulia (saludo festivo zuliano, sin imágenes ni referencias religiosas)"}
    if (d.month, d.day) in fijos: return fijos[(d.month, d.day)]
    if d == nth_weekday(y, 5, 6, 2): return "Día de la Madre"
    if d == nth_weekday(y, 6, 6, 3): return "Día del Padre"
    if d == nth_weekday(y, 7, 6, 3): return "Día del Niño"
    if d.month == 12 and d.day < 24: return "Temporada navideña / gaitas (ambiente decembrino, sin fecha concreta)"
    return None

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    hoy = dt.date.fromisoformat(args[0]) if args else dt.datetime.now(ZoneInfo("America/Caracas")).date()
    usado = json.loads(USADO.read_text()) if USADO.exists() else {}
    previos = {k: v for k, v in usado.items() if dt.date.fromisoformat(k) < hoy}
    rnd = random.Random(int(hoy.strftime("%Y%m%d")))
    fecha_esp = especial(hoy)
    grupos = SEMANA[hoy.weekday()]

    def edad(campo, k):
        """Días desde la última vez que se usó k en ese campo (999 = nunca)."""
        fechas = [dt.date.fromisoformat(f) for f, p in previos.items() if k in (p.get(campo) or [])]
        return (hoy - max(fechas)).days if fechas else 999
    def ranking(pool, campo, bonus=lambda k: 0):
        """Rotación: primero lo que hace más tiempo no se usa; el bonus y un poco de azar desempatan."""
        return sorted(pool, key=lambda k: min(edad(campo, k), 40) + bonus(k) + rnd.random() * 1.5, reverse=True)

    validos = [k for k, a in ANG.items() if not a.get("solo_dias") or hoy.day in a["solo_dias"]]
    pref = lambda k: 3 if ANG[k]["grupo"] in grupos else 0
    ang_video = ranking(validos, "angulos", pref)[0]
    flyers_ang = ["recordatorio_pago"] if hoy.day in (1, 2, 3) and ang_video != "recordatorio_pago" else []
    for k in ranking([k for k in validos if k != ang_video], "angulos", pref):
        if len(flyers_ang) == 3: break
        if k not in flyers_ang and all(ANG[k]["grupo"] != ANG[x]["grupo"] for x in flyers_ang + [ang_video]): flyers_ang.append(k)
    for k in ranking([k for k in validos if k != ang_video], "angulos"):
        if len(flyers_ang) == 3: break
        if k not in flyers_ang: flyers_ang.append(k)

    estilo_video = ranking(VIDEO, "video")[0]
    temporada = (hoy.month == 11 and hoy.day >= 15) or hoy.month == 12
    musica = ranking(MUSICA, "musica", lambda k: 6 if (temporada and k == "gaitera") else 0)[0]
    layouts = ranking(FLYER, "layouts")[:3]
    paletas = ranking(PALETAS, "paletas")[:3]
    tono = "festivo" if fecha_esp else ranking([t for t in TONO if t != "festivo"], "tono")[0]
    lo, hi = MUSICA[musica]

    plan = {
      "fecha": hoy.isoformat(), "dia_semana": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"][hoy.weekday()],
      "fecha_especial": fecha_esp, "tono": tono, "guia_tono": TONO[tono],
      "video": {"angulo": ang_video, **{k: v for k, v in ANG[ang_video].items() if k != "solo_dias"},
                "estilo": estilo_video, "como": VIDEO[estilo_video], "duracion_sugerida": rnd.choice([12, 12.5, 13, 14, 15])},
      "musica": {"estilo": musica, "bpm": rnd.randint(lo, hi), "tono": rnd.randint(-4, 4), "semilla": int(hoy.strftime("%Y%m%d"))},
      "flyers": [{"n": i + 1, "angulo": a, **{k: v for k, v in ANG[a].items() if k != "solo_dias"},
                  "layout": layouts[i], "como": FLYER[layouts[i]], "paleta": paletas[i], "colores": PALETAS[paletas[i]]}
                 for i, a in enumerate(flyers_ang[:3])],
      "recuerda": "Los ganchos son ideas: puedes escribir uno mejor, pero sin inventar datos. RIF y CONATEL legibles en todo.",
    }
    print(json.dumps(plan, ensure_ascii=False, indent=1))
    if "--guardar" in sys.argv:
        usado[hoy.isoformat()] = {"angulos": [ang_video] + flyers_ang[:3], "video": [estilo_video], "musica": [musica],
                                  "layouts": layouts, "paletas": paletas, "tono": [tono]}
        usado = {k: usado[k] for k in sorted(usado)[-60:]}
        USADO.write_text(json.dumps(usado, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
