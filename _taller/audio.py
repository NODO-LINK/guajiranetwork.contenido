"""Música y efectos (SIN VOZ) sincronizados con el video del día.

Uso:  python3 audio.py pistas.json salida.wav

pistas.json (todos los tiempos en segundos; cambia valores cada día para que no suene igual):
{
  "duracion": 12.5,          # igual al largo del video
  "semilla": 20261113,       # usa la fecha → cada día suena distinto
  "tono": 0,                 # transposición en semitonos (-5 … +5)
  "bpm": 120,                # 100 … 128
  "intro_hasta": 3.0,        # parte suave (sin batería) antes del primer golpe
  "cortes": [3.0, 6.0, 9.0], # cambios de escena: whoosh + impacto
  "conteos": [[3.3, 4.2]],   # ventanas de números contando (ticks que suben)
  "pops": [4.5],             # algo aparece de golpe (precio, sello…)
  "deslizes": [9.5, 10.0],   # tarjetas que entran de lado (swish corto)
  "arpegio": 10.5,           # destello final (o null)
  "fin_bateria": 11.5        # golpe final y se queda sonando el acorde
}
"""
import json, sys, wave
import numpy as np
from scipy.signal import fftconvolve, butter, sosfilt

cfg = json.load(open(sys.argv[1])); salida = sys.argv[2]
SR = 48000; DUR = float(cfg["duracion"]); N = int(SR * DUR)
rng = np.random.default_rng(int(cfg.get("semilla", 1)))
TONO = int(cfg.get("tono", 0)); BPM = float(cfg.get("bpm", 120)); BEAT = 60 / BPM
L = np.zeros(N); R = np.zeros(N)

def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR); n = min(len(sig), N - i)
    if n <= 0 or i < 0: return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[i:i+n] += sig[:n] * gain * l * 1.414; R[i:i+n] += sig[:n] * gain * r * 1.414
tt = lambda d: np.arange(int(d * SR)) / SR
lp = lambda x, f, o=2: sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
hp = lambda x, f, o=2: sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
bp = lambda x, lo, hi, o=2: sosfilt(butter(o, [lo, hi], 'band', fs=SR, output='sos'), x)
saw = lambda f, t: 2 * ((t * f) % 1) - 1
nf = lambda n: 440 * 2 ** ((n + TONO - 69) / 12)

def kick(g=1):
    t = tt(.45); f = 48 + 110 * np.exp(-t / .035)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .16) + .09 * np.exp(-t / .004) * rng.standard_normal(len(t))) * g
def clap():
    t = tt(.3); n = bp(rng.standard_normal(len(t)), 900, 4000)
    e = sum(np.exp(-np.maximum(t - d, 0) / .012) * (t >= d) for d in (0, .01, .022)) + .4 * np.exp(-t / .09)
    return n * e * .5
def hat():
    t = tt(.07); return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t / .018) * .35
def blip(f, d=.06):
    t = tt(d); return np.sin(2 * np.pi * f * t) * np.exp(-t / .02) * np.minimum(1, t / .002)
def pluck(fs, d=1.2, bright=6000):
    t = tt(d); s = sum(saw(f, t) + .5 * saw(f * 1.004, t) for f in fs) / len(fs)
    return lp(s, bright) * np.exp(-t / .35) * np.minimum(1, t / .003)
def whoosh(d=.56):
    t = tt(d); n = rng.standard_normal(len(t)); out = np.zeros_like(n)
    for i in range(0, len(n), 256):
        fc = 300 + 5200 * (np.sin(np.pi * i / len(n)) ** 1.5)
        out[i:i+256] = bp(n[i:i+256], max(120, fc * .6), min(20000, fc * 1.4), 1)
    return out * np.sin(np.pi * t / d) ** 2 * .9
def impact():
    t = tt(1.4); sub = np.sin(2 * np.pi * (38 + 60 * np.exp(-t / .08)) * t) * np.exp(-t / .5)
    return sub * .9 + lp(rng.standard_normal(len(t)), 2500) * np.exp(-t / .12) * .35
def pad(fs, d, cutoff=1400):
    t = tt(d); s = np.zeros_like(t)
    for f in fs:
        for det in (-.12, 0, .11): s += saw(f * 2 ** (det / 12), t + rng.random())
    return lp(s / (len(fs) * 3), cutoff, 4)
def riser(d):
    t = tt(d); x = t / d
    return np.sin(2 * np.pi * np.cumsum(200 + 1800 * x ** 2) / SR) * x ** 2 * .15 + hp(rng.standard_normal(len(t)), 3000) * x ** 3 * .25

# Progresiones posibles (se elige una por la semilla → variedad diaria)
PROG = [[(57, 60, 64), (53, 57, 60), (55, 60, 64), (55, 59, 62)],   # Am F C G
        [(53, 57, 60), (55, 60, 64), (57, 60, 64), (55, 59, 62)],   # F C Am G
        [(57, 60, 64), (55, 59, 62), (53, 57, 60), (55, 60, 64)],   # Am G F C
        [(50, 53, 57), (53, 57, 60), (55, 60, 64), (55, 59, 62)]]   # Dm F C G
prog = [[nf(n) for n in ch] for ch in PROG[rng.integers(len(PROG))]]
I0 = float(cfg.get("intro_hasta", 3.0)); FIN = float(cfg.get("fin_bateria", DUR - 1))

# Intro suave
add(pad(prog[0], I0 + .2, 900) * np.minimum(1, tt(I0 + .2) / 1.2), 0, .45, -.2)
s = bp(rng.standard_normal(int(min(1.3, I0) * SR)), 2500, 9000); add(s * np.linspace(0, 1, len(s)) ** 2 * .25, .1, 1, .3)
esc = [0, 3, 7, 12, 15, 19, 24, 27, 31]
for k, ti in enumerate(np.arange(.15, min(1.3, I0 - .3), .14)): add(blip(nf(84 + esc[k % 9]), .25) * .25, ti, .5, -.6 + k * .15)
if I0 > 1.5: add(kick(.9), .95, .8); add(pluck([nf(69), nf(76)], .9), .95, .35)
add(riser(.6), max(0, I0 - .6), 1)
# Cortes
for i, c in enumerate(cfg.get("cortes", [])): add(whoosh(.56), c - .28, .6, .3 if i % 2 == 0 else -.3); add(impact(), c, .75)
# Ritmo
b = I0; k = 0
while b < FIN - 1e-6:
    add(kick(), b, .85)
    if k % 2 == 1: add(clap(), b, .55, .05)
    add(hat(), b + BEAT / 2, .5, .35); add(hat(), b, .25, -.35); b += BEAT; k += 1
compas = BEAT * 4; st = I0; ci = 0
while st < DUR - .05:
    d = min(compas, DUR - st); ch = prog[ci % 4]
    add(pad(ch, d + .3, 1800) * np.minimum(1, tt(d + .3) / .05), st, .3, -.15)
    root = ch[0] / 4; j = 0; bb = st
    while bb < min(st + d, FIN) - 1e-6:
        t_ = tt(BEAT / 2 - .01); add(lp(saw(root * (2 if j % 4 == 3 else 1), t_), 700) * np.exp(-t_ / .15), bb, .5 if j % 2 == 0 else .3)
        bb += BEAT / 2; j += 1
    st += compas; ci += 1
# Eventos
for a, z in cfg.get("conteos", []):
    for k, ti in enumerate(np.arange(a, z, .05)): add(blip(700 + k * 75), ti, .28, (-1) ** k * .3)
for i, t0 in enumerate(cfg.get("pops", [])):
    ch = prog[(i + 1) % 4]; add(pluck([c * 2 for c in ch] + [ch[0] * 4], 1.0, 9000), t0, .45); add(blip(nf(93), .2), t0, .25)
for t0 in cfg.get("deslizes", []): add(whoosh(.35), t0 - .05, .35, .5)
if cfg.get("arpegio") is not None:
    for k, n_ in enumerate([69, 72, 76, 79]): add(pluck([nf(n_ + 12)], .8, 8000), cfg["arpegio"] + k * .125, .22, -.4 + k * .25)
if FIN < DUR: add(impact(), FIN, .5); add(pad(prog[0], DUR - FIN, 1200), FIN, .4)
# Reverb + master
ir_t = tt(1.1); ir = lp(rng.standard_normal(len(ir_t)) * np.exp(-ir_t / .3), 5000); ir /= np.sqrt(np.sum(ir ** 2))
mix = np.stack([L + .22 * fftconvolve(L, ir)[:N], R + .22 * np.roll(fftconvolve(R, ir)[:N], 240)], 1)
mix = hp(mix.T, 28).T
f = np.ones(N); i0 = int(max(0, DUR - .5) * SR); f[i0:] = np.linspace(1, 0, N - i0) ** 1.5; mix *= f[:, None]
fi = int(.02 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.3); mix *= 10 ** (-1 / 20) / np.max(np.abs(mix))
with wave.open(salida, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix * 32767).astype('<i2').tobytes())
print('audio ok', DUR, 's')
