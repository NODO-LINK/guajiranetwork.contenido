"""Música y efectos (SIN VOZ) sincronizados con el video del día — v2 con 6 estilos.

Uso:  python3 audio.py pistas.json salida.wav

pistas.json (tiempos en segundos; plan_del_dia.py sugiere estilo, bpm, tono y semilla):
{
  "estilo": "electro",       # electro | dembow | gaitera | lofi | house | trap
  "duracion": 12.5,          # igual al largo del video
  "semilla": 20261113,       # AAAAMMDD → cada día suena distinto
  "tono": 0,                 # transposición en semitonos (-5 … +5)
  "bpm": 120,                # opcional; si falta se usa el típico del estilo
  "intro_hasta": 3.0,        # parte suave (sin batería) antes del primer golpe
  "cortes": [3.0, 6.0, 9.0], # cambios de escena: whoosh + impacto
  "conteos": [[3.3, 4.2]],   # números contando (ticks que suben)
  "pops": [4.5],             # algo aparece de golpe (precio, sello, check…)
  "deslizes": [9.5, 10.0],   # elementos que entran de lado (swish corto)
  "arpegio": 10.5,           # destello (o null)
  "fin_bateria": 11.5        # golpe final; queda sonando el acorde
}
Consejo: haz coincidir los cortes con tiempos del compás (múltiplos de 60/bpm desde intro_hasta).
"""
import json, sys, wave
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

cfg = json.load(open(sys.argv[1])); salida = sys.argv[2]
ESTILO = cfg.get("estilo", "electro")
BPM_TIPICO = {"electro": 120, "dembow": 96, "gaitera": 112, "lofi": 84, "house": 124, "trap": 140}
SR = 48000; DUR = float(cfg["duracion"]); N = int(SR * DUR)
rng = np.random.default_rng(int(cfg.get("semilla", 1)))
TONO = int(cfg.get("tono", 0)); BPM = float(cfg.get("bpm") or BPM_TIPICO.get(ESTILO, 120)); BEAT = 60 / BPM
L = np.zeros(N); R = np.zeros(N)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[i:i+n] += sig[:n] * gain * l * 1.414; R[i:i+n] += sig[:n] * gain * r * 1.414
tt = lambda d: np.arange(max(1, int(d * SR))) / SR
lp = lambda x, f, o=2: sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
hp = lambda x, f, o=2: sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
bp = lambda x, lo, hi, o=2: sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
saw = lambda f, t: 2 * ((t * f) % 1) - 1
nf = lambda n: 440 * 2 ** ((n + TONO - 69) / 12)
ruido = lambda d: rng.standard_normal(len(tt(d)))

# ───────── Instrumentos ─────────
def kick(g=1, grave=48, punch=110, dec=.16):
    t = tt(.45); f = grave + punch * np.exp(-t / .035)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / dec) + .09 * np.exp(-t / .004) * ruido(.45)) * g
def snare(tono=190, dec=.12):
    t = tt(.3); cuerpo = np.sin(2 * np.pi * tono * t) * np.exp(-t / .05)
    return (cuerpo * .6 + bp(ruido(.3), 1500, 8000) * np.exp(-t / dec) * .7) * .6
def clap():
    t = tt(.3); n = bp(ruido(.3), 900, 4000)
    e = sum(np.exp(-np.maximum(t - d, 0) / .012) * (t >= d) for d in (0, .01, .022)) + .4 * np.exp(-t / .09)
    return n * e * .5
def rim():
    t = tt(.08); return (np.sin(2 * np.pi * 1700 * t) * .5 + bp(ruido(.08), 2000, 6000) * .5) * np.exp(-t / .012) * .5
def hat(abierto=False):
    d = .28 if abierto else .07; t = tt(d); return hp(ruido(d), 7000) * np.exp(-t / (.09 if abierto else .018)) * .35
def shaker(d=.09):
    t = tt(d); return bp(ruido(d), 4000, 11000) * np.sin(np.pi * t / d) ** 2 * .3
def tambora(tono=95, g=1):
    t = tt(.35); f = tono * (1 + .5 * np.exp(-t / .02))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .14) * g + lp(ruido(.35), 900) * np.exp(-t / .03) * .25 * g
def blip(f, d=.06):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t / .02) * np.minimum(1, t / .002)
def cuerda(f, d=1.2, brillo=.5, decay=.996):
    """Karplus-Strong: cuerda pulsada (suena a cuatro/guitarra)."""
    n = int(d * SR); P = max(2, int(SR / f)); y = np.zeros(n + P)
    exc = rng.uniform(-1, 1, P); exc = lp(exc, 1500 + 6000 * brillo) if P > 12 else exc
    y[:P] = exc
    for i in range(P, n + P, P):
        seg = y[i - P:i]; prev = np.concatenate(([y[i - P - 1] if i - P - 1 >= 0 else 0], seg[:-1]))
        y[i:i + P] = (decay * .5 * (seg + prev))[:len(y[i:i + P])]
    return y[P:P + n] * np.minimum(1, tt(d)[:n] / .002)
def rasgueo(fs, d=.9, sube=True, g=1):
    s = np.zeros(int(d * SR)); orden = fs if sube else fs[::-1]
    for k, f in enumerate(orden):
        c = cuerda(f, d, .55); off = int(k * .012 * SR); s[off:] += c[:len(s) - off] * (1 - .08 * k)
    return s / len(fs) * g
def pluck(fs, d=1.2, bright=6000):
    t = tt(d); s = sum(saw(f, t) + .5 * saw(f * 1.004, t) for f in fs) / len(fs)
    return lp(s, bright) * np.exp(-t / .35) * np.minimum(1, t / .003)
def epiano(fs, d=1.0):
    t = tt(d); s = sum(np.sin(2 * np.pi * f * t) + .25 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t / .2) for f in fs) / len(fs)
    return s * np.exp(-t / .8) * np.minimum(1, t / .004) * (1 + .15 * np.sin(2 * np.pi * 5 * t))
def organo(fs, d=.25):
    t = tt(d); s = sum(np.sin(2 * np.pi * f * t) + .5 * np.sin(4 * np.pi * f * t) + .3 * np.sin(6 * np.pi * f * t) for f in fs) / len(fs)
    return lp(s, 3000) * np.minimum(1, t / .005) * np.exp(-t / .15)
def sub808(f, d=.6):
    t = tt(d); return np.tanh(2 * np.sin(2 * np.pi * f * t * (1 + .3 * np.exp(-t / .03)))) * np.exp(-t / .45) * np.minimum(1, t / .003)
def whoosh(d=.56):
    t = tt(d); n = ruido(d); out = np.zeros_like(n)
    for i in range(0, len(n), 256):
        fc = 300 + 5200 * (np.sin(np.pi * i / len(n)) ** 1.5)
        out[i:i+256] = bp(n[i:i+256], max(120, fc * .6), min(20000, fc * 1.4), 1)
    return out * np.sin(np.pi * t / d) ** 2 * .9
def impact():
    t = tt(1.4); sub = np.sin(2 * np.pi * (38 + 60 * np.exp(-t / .08)) * t) * np.exp(-t / .5)
    return sub * .9 + lp(ruido(1.4), 2500) * np.exp(-t / .12) * .35
def pad(fs, d, cutoff=1400):
    t = tt(d); s = np.zeros_like(t)
    for f in fs:
        for det in (-.12, 0, .11): s += saw(f * 2 ** (det / 12), t + rng.random())
    return lp(s / (len(fs) * 3), cutoff, 4)
def riser(d):
    t = tt(d); x = t / d
    return np.sin(2 * np.pi * np.cumsum(200 + 1800 * x ** 2) / SR) * x ** 2 * .15 + hp(ruido(d), 3000) * x ** 3 * .25
def vinilo(d):
    t = tt(d); c = np.zeros_like(t); idx = rng.integers(0, len(t), int(d * 18)); c[idx] = rng.uniform(-.6, .6, len(idx))
    return lp(c, 6000) * .25 + lp(ruido(d), 1200) * .015

# ───────── Armonía ─────────
PROG = [[(57, 60, 64), (53, 57, 60), (55, 60, 64), (55, 59, 62)],   # Am F C G
        [(53, 57, 60), (55, 60, 64), (57, 60, 64), (55, 59, 62)],   # F C Am G
        [(57, 60, 64), (55, 59, 62), (53, 57, 60), (55, 60, 64)],   # Am G F C
        [(50, 53, 57), (53, 57, 60), (55, 60, 64), (55, 59, 62)],   # Dm F C G
        [(52, 55, 59), (48, 52, 55), (55, 59, 62), (50, 54, 57)]]   # Em C G D
if ESTILO == "gaitera": PROG = [[(55, 59, 62), (50, 54, 57), (52, 55, 59), (48, 52, 55)], [(57, 61, 64), (52, 56, 59), (54, 57, 61), (50, 54, 57)]]  # mayor y alegre
if ESTILO == "lofi": PROG = [[(50, 53, 57, 60), (55, 59, 62, 65), (48, 52, 55, 59), (57, 60, 64, 67)], [(53, 57, 60, 64), (52, 55, 59, 62), (50, 53, 57, 60), (55, 59, 62, 65)]]
prog = [[nf(n) for n in ch] for ch in PROG[rng.integers(len(PROG))]]
I0 = float(cfg.get("intro_hasta", 3.0)); FIN = float(cfg.get("fin_bateria", DUR - 1))
DEC = 4 * BEAT  # compás

# ───────── Intro ─────────
intro_pad = (epiano if ESTILO == "lofi" else None)
if ESTILO in ("gaitera",):
    for k, b in enumerate(np.arange(0, I0 - .2, BEAT * 1.5)): add(rasgueo([c * 2 for c in prog[0]], .8, k % 2 == 0, .9), b, .55, -.1)
elif ESTILO == "lofi":
    add(epiano([c for c in prog[0]], I0 + .4), 0, .55); add(vinilo(DUR), 0, 1)
else:
    add(pad(prog[0], I0 + .2, 900) * np.minimum(1, tt(I0 + .2) / 1.2), 0, .45, -.2)
s = bp(ruido(min(1.3, I0)), 2500, 9000); add(s * np.linspace(0, 1, len(s)) ** 2 * .2, .1, 1, .3)
esc = [0, 3, 7, 12, 15, 19, 24, 27, 31]
for k, ti in enumerate(np.arange(.15, min(1.3, I0 - .3), .14)): add(blip(nf(84 + esc[k % 9]), .25) * .22, ti, .5, -.6 + k * .15)
add(riser(.6), max(0, I0 - .6), .9)

# ───────── Cortes ─────────
for i, c in enumerate(cfg.get("cortes", [])): add(whoosh(.56), c - .28, .6, .3 if i % 2 == 0 else -.3); add(impact(), c, .7)

# ───────── Ritmo por estilo ─────────
def compas_bateria(b0):
    s16 = BEAT / 4
    if ESTILO == "electro":
        for k in range(4):
            add(kick(), b0 + k * BEAT, .85); add(hat(), b0 + k * BEAT + BEAT / 2, .5, .35); add(hat(), b0 + k * BEAT, .22, -.35)
            if k % 2: add(clap(), b0 + k * BEAT, .55, .05)
    elif ESTILO == "dembow":
        for i in (0, 4, 8, 12): add(kick(1, 46, 95, .18), b0 + i * s16, .9)
        for i in (3, 6, 11, 14): add(snare(210, .1), b0 + i * s16, .6, .05)
        for i in range(0, 16, 2): add(hat(), b0 + i * s16, .3, .3)
    elif ESTILO == "gaitera":  # sensación 6/8: el compás se divide en 4 grupos de 3 corcheas de tresillo
        t3 = BEAT / 3
        for g in range(4):
            base = b0 + g * BEAT
            add(tambora(92, 1), base, .75); add(tambora(140, .5), base + 2 * t3, .5, .2)
            for j in range(3): add(shaker(.08), base + j * t3, .55 if j == 0 else .35, -.3)
        add(sub808(prog[0][0] / 4, .5), b0, .25)
    elif ESTILO == "lofi":
        sw = s16 * .33
        for i in (0, 7, 10): add(kick(.8, 50, 70, .14) , b0 + i * s16, .7)
        for i in (4, 12): add(rim(), b0 + i * s16, .7, .1)
        for i in range(0, 16, 2): add(hat(), b0 + i * s16 + (sw if (i // 2) % 2 else 0), .22, .3)
    elif ESTILO == "house":
        for k in range(4):
            add(kick(1, 50, 120, .15), b0 + k * BEAT, .85); add(hat(True), b0 + k * BEAT + BEAT / 2, .35, .3)
            if k % 2: add(clap(), b0 + k * BEAT, .5)
    elif ESTILO == "trap":
        for i in (0, 6, 10): add(sub808(prog[0][0] / 4, .55), b0 + i * s16, .55)
        add(kick(.7, 50, 90, .1), b0, .5)
        add(snare(180, .14), b0 + 2 * BEAT, .6); add(clap(), b0 + 2 * BEAT, .35)
        for i in range(16):
            add(hat(), b0 + i * s16, .22, .3)
            if i in (11, 15):
                for j in range(1, 3): add(hat(), b0 + i * s16 + j * s16 / 3, .16, .3)
def compas_armonia(b0, ch, d):
    if ESTILO == "gaitera":
        t3 = BEAT / 3
        for g in range(4):
            if b0 + g * BEAT >= FIN: break
            add(rasgueo([c * 2 for c in ch], .5, True, .9), b0 + g * BEAT, .45, -.1); add(rasgueo([c * 2 for c in ch], .35, False, .6), b0 + g * BEAT + 2 * t3, .35, .1)
        add(cuerda(ch[0] / 2, 1.6, .3, .998), b0, .5)
    elif ESTILO == "lofi":
        add(epiano(ch, d + .2), b0, .45); add(lp(cuerda(ch[0] / 2, d, .2, .998), 900), b0, .45)
    elif ESTILO == "house":
        add(pad(ch, d + .3, 1600), b0, .22)
        for k in (1, 3): add(organo([c * 2 for c in ch], .22), b0 + k * BEAT + BEAT / 2, .35, .15)
        bb = b0
        while bb < min(b0 + d, FIN) - 1e-6:
            t_ = tt(BEAT / 2 - .02); add(lp(saw(ch[0] / 4, t_), 600) * np.exp(-t_ / .12), bb + BEAT / 2, .45); bb += BEAT
    elif ESTILO == "trap":
        add(pad(ch, d + .3, 1200), b0, .25); add(pluck([c * 2 for c in ch], .6, 5000), b0, .25)
    else:  # electro y dembow
        add(pad(ch, d + .3, 1800) * np.minimum(1, tt(d + .3) / .05), b0, .28, -.15)
        bb = b0; j = 0; root = ch[0] / 4
        while bb < min(b0 + d, FIN) - 1e-6:
            t_ = tt(BEAT / 2 - .01); add(lp(saw(root * (2 if j % 4 == 3 else 1), t_), 700) * np.exp(-t_ / .15), bb, .5 if j % 2 == 0 else .3)
            bb += BEAT / 2; j += 1
        if ESTILO == "dembow":
            for k in (0, 1.5, 3): add(pluck([c * 2 for c in ch], .35, 7000), b0 + k * BEAT, .2, .2)

b = I0; ci = 0
while b < DUR - .05:
    d = min(DEC, DUR - b); ch = prog[ci % len(prog)]
    if b < FIN: compas_bateria(b)
    compas_armonia(b, ch, d)
    b += DEC; ci += 1

# ───────── Eventos del video ─────────
for a, z in cfg.get("conteos", []):
    for k, ti in enumerate(np.arange(a, z, .05)): add(blip(700 + k * 75), ti, .26, (-1) ** k * .3)
for i, t0 in enumerate(cfg.get("pops", [])):
    ch = prog[(i + 1) % len(prog)]
    if ESTILO in ("gaitera", "lofi"): add(rasgueo([c * 2 for c in ch] + [ch[0] * 4], 1.0), t0, .6)
    else: add(pluck([c * 2 for c in ch] + [ch[0] * 4], 1.0, 9000), t0, .42)
    add(blip(nf(93), .2), t0, .22)
for t0 in cfg.get("deslizes", []): add(whoosh(.35), t0 - .05, .33, .5)
if cfg.get("arpegio") is not None:
    for k, n_ in enumerate([69, 72, 76, 79]):
        sig = cuerda(nf(n_ + 12), .8, .7) if ESTILO in ("gaitera", "lofi") else pluck([nf(n_ + 12)], .8, 8000)
        add(sig, cfg["arpegio"] + k * .125, .25, -.4 + k * .25)
if FIN < DUR:
    add(impact(), FIN, .45)
    if ESTILO in ("gaitera", "lofi"): add(rasgueo([c * 2 for c in prog[0]], DUR - FIN + .3), FIN, .6)
    else: add(pad(prog[0], DUR - FIN, 1200), FIN, .4)

# ───────── Mezcla final ─────────
ir_t = tt(1.1); ir = lp(rng.standard_normal(len(ir_t)) * np.exp(-ir_t / (.45 if ESTILO == "lofi" else .3)), 5000); ir /= np.sqrt(np.sum(ir ** 2))
mix = np.stack([L + .22 * fftconvolve(L, ir)[:N], R + .22 * np.roll(fftconvolve(R, ir)[:N], 240)], 1)
mix = hp(mix.T, 28).T
if ESTILO == "lofi": mix = lp(mix.T, 7000).T
f = np.ones(N); i0 = int(max(0, DUR - .5) * SR); f[i0:] = np.linspace(1, 0, N - i0) ** 1.5; mix *= f[:, None]
fi = int(.02 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.3); mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
with wave.open(salida, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
print(f'audio ok · estilo {ESTILO} · {BPM:.0f} bpm · {DUR} s')
