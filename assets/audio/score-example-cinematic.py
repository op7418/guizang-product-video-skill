"""Example score (cinematic electronic) from the CodePilot film — 50 s, 120 BPM, F minor.
Pure synthesis (numpy/scipy/soundfile): supersaw pads, plucked arps through a dotted-8th delay,
synth drums with sidechain, risers, impacts and a convolution reverb. Deterministic.

This is ONE genre for ONE storyboard. Copy the techniques, not the piece: re-derive key, tempo,
palette and every section time from the new film's DIRECTION.md and plan.json shot boundaries.
Its arrangement followed that film's shots:
  0–4 hook (drone + riser, gap at 3.8) · 4 impact · 4–8 brand (pad bloom, bells)
  8–14 reveal (kick in, bass) · 14 / 24 / 34 chapter hits with 1.5 s breaks
  15.5–24, 25.5–34, 35.5–41 groove · 41–44.5 montage build · 44.5 impact · 44.5–50 resolve
Usage: python -m venv .venv && .venv/bin/pip install numpy scipy soundfile
       .venv/bin/python score.py assets/music.wav
"""
import sys, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000; BPM = 120; BEAT = 60 / BPM; DUR = 50.0; N = int(SR * DUR)
rng = np.random.default_rng(418)
buses = {k: np.zeros((N, 2)) for k in ['drums', 'bass', 'pad', 'arp', 'bell', 'fx']}

def hz(n): return 440 * 2 ** ((n - 69) / 12)
def put(bus, t0, sig, pan=0.0, gain=1.0):
    i = int(round(t0 * SR))
    if i >= N: return
    if sig.ndim == 1: sig = np.stack([sig * np.sqrt((1 - pan) / 2), sig * np.sqrt((1 + pan) / 2)], 1)
    j = min(N, i + len(sig)); buses[bus][max(0, i):j] += sig[max(0, -i):j - i] * gain
def tt(d): return np.arange(int(d * SR)) / SR
def env(t, a, d, r_at=None, r=0.3):
    e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t * d)
    if r_at is not None: e *= np.clip((r_at + r - t) / r, 0, 1)
    return e
def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * 0.45), 'low', fs=SR, output='sos'), x, axis=0)
def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x, axis=0)
def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x, axis=0)
def sweep_lp(x, f0, f1, block=1024):
    """Time-varying low-pass (exponential cutoff sweep), processed in blocks with carried state."""
    out = np.zeros_like(x); zi = None; nb = int(np.ceil(len(x) / block))
    for b in range(nb):
        fc = f0 * (f1 / f0) ** (b / max(1, nb - 1))
        sos = butter(2, min(fc, SR * 0.45), 'low', fs=SR, output='sos')
        if zi is None: zi = np.zeros((sos.shape[0], 2) + x.shape[1:])
        seg = x[b * block:(b + 1) * block]
        y, zi = sosfilt(sos, seg, axis=0, zi=zi); out[b * block:(b + 1) * block] = y
    return out

# ── instruments ────────────────────────────────────────────────────────────
def saw(f, t, k_max=36, phase=0.0):
    k_top = int(min(k_max, (SR * 0.45) // f)); s = np.zeros_like(t)
    for k in range(1, k_top + 1): s += np.sin(2 * np.pi * k * f * t + phase * k) / k
    return s
def supersaw(note, dur, amp, cut=1800, bright_to=None, attack=0.6, release=0.8):
    t = tt(dur + release); f = hz(note); L = np.zeros_like(t); R = np.zeros_like(t)
    for i, c in enumerate([-14, -7, 0, 7, 14]):
        v = saw(f * 2 ** (c / 1200), t, 24, rng.uniform(0, 6.28)); p = (i - 2) / 2.2
        L += v * np.sqrt((1 - p) / 2); R += v * np.sqrt((1 + p) / 2)
    x = np.stack([L, R], 1) / 5
    x = sweep_lp(x, cut, bright_to or cut)
    e = np.minimum(1, t / attack) * np.clip((dur + release - t) / release, 0, 1)
    return x * e[:, None] * amp
def pluck(note, amp, dur=0.9):
    t = tt(dur); f = hz(note); s = np.zeros_like(t)
    for k in range(1, int(min(28, (SR * 0.45) // f)) + 1): s += np.sin(2 * np.pi * k * f * t) / k * np.exp(-t * (4 + k * 1.6))
    return s * np.minimum(1, t / 0.002) * amp
def bell(note, amp, dur=2.6):
    t = tt(dur); f = hz(note)
    return np.sin(2 * np.pi * f * t + 2.2 * np.exp(-t * 3) * np.sin(2 * np.pi * f * 3.5 * t)) * np.exp(-t * 1.6) * np.minimum(1, t / 0.003) * amp
def sub(note, dur, amp):
    t = tt(dur); f = hz(note); s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return np.tanh(1.6 * s) * env(t, 0.005, 0.0, dur - 0.08, 0.08) * amp
def kick(amp):
    t = tt(0.45); ph = 2 * np.pi * (45 * t + (130 - 45) * 0.045 * (1 - np.exp(-t / 0.045)))
    body = np.sin(ph) * np.exp(-t * 7.5); click = hp(rng.uniform(-1, 1, len(t)), 2500) * np.exp(-t * 180) * 0.35
    return np.tanh(1.4 * (body + click)) * amp
def clap(amp):
    t = tt(0.35); n = rng.uniform(-1, 1, len(t)); e = np.zeros_like(t)
    for o in [0, 0.011, 0.022]: e += (t >= o) * np.exp(-np.maximum(0, t - o) * (60 if o < 0.02 else 14))
    return bp(n * e, 900, 3200) * amp
def hat(amp, open_=False):
    t = tt(0.3 if open_ else 0.06); n = hp(rng.uniform(-1, 1, len(t)), 7000, 4)
    return n * np.exp(-t * (14 if open_ else 70)) * amp
def impact(amp):
    t = tt(3.2); ph = 2 * np.pi * (28 * t + (70 - 28) * 0.25 * (1 - np.exp(-t / 0.25)))
    boom = np.sin(ph) * np.exp(-t * 1.6); noise = lp(rng.uniform(-1, 1, len(t)), 900) * np.exp(-t * 6) * 0.9
    return np.tanh(1.3 * (boom + noise)) * amp
def riser(dur, amp, f0=300, f1=9000):
    t = tt(dur); n = rng.uniform(-1, 1, (len(t), 2))
    x = sweep_lp(n, f0, f1); x = hp(x, 200)
    glide = np.sin(2 * np.pi * (220 * t + (880 - 220) * t ** 2 / (2 * dur)))[:, None] * 0.12
    return (x + glide) * ((t / dur) ** 2.2)[:, None] * amp
def swell(dur, amp):   # reverse-cymbal style swell into a hit
    t = tt(dur); n = hp(rng.uniform(-1, 1, (len(t), 2)), 3000)
    return n * ((t / dur) ** 3)[:, None] * amp

# ── harmony ────────────────────────────────────────────────────────────────
CH = {'Fm9': (41, [56, 60, 63, 67]), 'Db': (37, [53, 56, 60, 65]), 'Ab': (44, [51, 55, 60, 63]), 'Eb': (39, [55, 58, 60, 65])}
PROG = ['Fm9', 'Db', 'Ab', 'Eb']
def chord_at(t): return PROG[int(t // 4) % 4]
ARP = [0, 2, 1, 3, 2, 1, 3, 2]

# hook: drone + riser, gap before 4.0
put('pad', 0.0, supersaw(41 + 12, 3.8, 0.10, cut=300, bright_to=1400, attack=1.5, release=0.05))
put('bass', 0.0, sub(29, 3.78, 0.11))
put('fx', 0.6, riser(3.2, 0.32))
put('fx', 2.3, swell(1.5, 0.22))
# brand: impact, pad bloom, bells
put('fx', 4.0, impact(0.9))
put('pad', 4.0, supersaw(56, 3.9, 0.07, cut=500, bright_to=3200, attack=0.05))
for n in [60, 63, 67]: put('pad', 4.0, supersaw(n, 3.9, 0.05, cut=500, bright_to=3200, attack=0.05))
for i, (t0, n) in enumerate([(4.0, 72), (4.75, 79), (5.5, 75), (6.0, 84), (6.5, 79), (7.25, 75)]): put('bell', t0, bell(n, 0.16), -0.4 + 0.16 * i)

HITS = [14.0, 24.0, 34.0]; BREAK = 1.5
def in_break(t): return any(h <= t < h + BREAK for h in HITS)
# pads through the body
for bar in range(4, 22):
    t0 = bar * 2.0
    root, voic = CH[chord_at(t0)]
    level = 0.042 if t0 < 15.5 else 0.05
    bright = 1600 if t0 < 30 else 2600
    for i, n in enumerate(voic): put('pad', t0, supersaw(n, 2.0, level, cut=900, bright_to=bright, attack=0.25, release=0.35), (i - 1.5) * 0.3)
# drums, bass, arps from 8.0 to 41.0
for b in range(int(8.0 / BEAT), int(41.0 / BEAT)):
    t0 = b * BEAT
    if in_break(t0): continue
    full = t0 >= 15.5
    put('drums', t0, kick(0.8 if full else 0.6))
    if full and b % 2 == 1: put('drums', t0, clap(0.28), 0.05)
    if t0 >= 10.0:
        for h in range(4 if full else 2):
            put('drums', t0 + h * BEAT / (4 if full else 2), hat(0.07 if h % 2 else 0.045, open_=(full and h == 2 and b % 4 == 3)), 0.3 if h % 2 else -0.3)
    root, voic = CH[chord_at(t0)]
    for k, off in enumerate([0.25] if not full else [0.0, 0.25]):
        put('bass', t0 + off, sub(root + (12 if (full and k == 1 and b % 4 == 2) else 0), 0.22, 0.26 if full else 0.2))
    if full:
        for s16 in range(2):
            step = (b * 2 + s16) % 8
            n = voic[ARP[step] % 4] + 12
            put('arp', t0 + s16 * BEAT / 2, pluck(n, 0.085 if s16 == 0 else 0.06), -0.35 if s16 else 0.35)
# chapter hits and breaks
for h in HITS:
    put('fx', h, impact(0.75)); put('fx', h - 1.0, swell(1.0, 0.2))
    root, voic = CH[chord_at(h)]
    put('bass', h, sub(root - 12, 1.4, 0.22))
    for i, n in enumerate(voic): put('bell', h + 0.02 + i * 0.09, bell(n + 12, 0.07), (i - 1.5) * 0.4)
    put('fx', h + BREAK - 1.2, riser(1.2, 0.18, 800, 7000))
# montage build 41–44.5: 8ths → 16ths snare, riser, filter lift
for b in range(int(41.0 / BEAT), int(44.5 / BEAT)):
    t0 = b * BEAT; put('drums', t0, kick(0.85))
    div = 2 if t0 < 43.0 else 4
    for s in range(div): put('drums', t0 + s * BEAT / div, clap(0.12 + 0.12 * (t0 - 41) / 3.5), 0.1)
    root, voic = CH['Db'] if t0 < 43 else CH['Eb']
    put('bass', t0, sub(root, 0.2, 0.26)); put('bass', t0 + 0.25, sub(root + 12, 0.2, 0.2))
    for s16 in range(2): put('arp', t0 + s16 * 0.25, pluck(voic[(b * 2 + s16) % 4] + 12, 0.08))
for i, n in enumerate(CH['Eb'][1]): put('pad', 41.0, supersaw(n, 3.4, 0.045, cut=900, bright_to=5200, attack=0.4, release=0.1), (i - 1.5) * 0.3)
put('fx', 41.2, riser(3.3, 0.36)); put('fx', 43.5, swell(1.0, 0.25))
# end: impact, resolve on Db → Fm(add9), bell motif, long tail
put('fx', 44.5, impact(1.0))
for i, n in enumerate([53, 56, 60, 65]): put('pad', 44.5, supersaw(n, 2.4, 0.055, cut=2400, bright_to=900, attack=0.05, release=0.6), (i - 1.5) * 0.3)
for i, n in enumerate([56, 60, 63, 67, 72]): put('pad', 46.5, supersaw(n, 2.6, 0.045, cut=1800, bright_to=500, attack=0.3, release=0.8), (i - 2) * 0.25)
put('bass', 44.5, sub(37, 2.0, 0.24)); put('bass', 46.5, sub(29, 2.9, 0.22))
for t0, n in [(45.0, 72), (45.5, 75), (46.0, 79), (46.5, 84), (47.5, 80), (48.0, 79)]: put('bell', t0, bell(n, 0.12), 0.1)

# ── mix ────────────────────────────────────────────────────────────────────
t_all = np.arange(N) / SR
def sidechain(depth=0.55, rel=0.22):
    g = np.ones(N)
    kicks = [b * BEAT for b in range(int(8 / BEAT), int(44.5 / BEAT)) if not in_break(b * BEAT)]
    for k in kicks:
        i = int(k * SR); j = min(N, i + int(0.5 * SR)); x = (np.arange(j - i) / SR)
        g[i:j] = np.minimum(g[i:j], 1 - depth * np.exp(-x / rel * 2.2))
    return g[:, None]
sc = sidechain()
buses['pad'] *= sc; buses['bass'] *= sidechain(0.7, 0.12); buses['arp'] *= sidechain(0.35, 0.15)
# dotted-8th ping-pong delay on arps and bells
def delay(x, time=0.375, fb=0.38, mix=0.32):
    d = int(time * SR); y = x.copy()
    for k in range(1, 6):
        tap = np.zeros_like(x); tap[k * d:] = x[:N - k * d]
        if k % 2: tap = tap[:, ::-1]
        y += tap * mix * fb ** (k - 1)
    return y
buses['arp'] = delay(lp(buses['arp'], 5200))
buses['bell'] = delay(buses['bell'], 0.5, 0.3, 0.25)
# convolution reverb (stereo decorrelated noise IR, 2.8 s)
ti = tt(2.8); ir = np.stack([rng.normal(0, 1, len(ti)), rng.normal(0, 1, len(ti))], 1) * np.exp(-ti * 2.4)[:, None]
ir = lp(ir, 6000); ir /= np.sqrt((ir ** 2).sum())
send = buses['pad'] * 0.35 + buses['bell'] * 0.6 + buses['arp'] * 0.3 + buses['fx'] * 0.35 + hp(buses['drums'], 400) * 0.12
wet = np.stack([fftconvolve(send[:, c], ir[:, c])[:N] for c in range(2)], 1) * 0.9
mix = buses['drums'] * 0.95 + buses['bass'] * 0.68 + buses['pad'] * 0.9 + buses['arp'] * 0.8 + buses['bell'] * 0.8 + buses['fx'] * 0.9 + wet
mix = hp(mix, 28)
fade = np.clip((DUR - t_all) / 2.2, 0, 1) ** 1.5 * np.minimum(1, t_all / 0.05)
mix *= fade[:, None]
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.abs(mix).max() / 0.92
out = sys.argv[1] if len(sys.argv) > 1 else 'assets/music.wav'
sf.write(out, mix.astype(np.float32), SR, subtype='FLOAT')
print(out, f'{DUR}s', 'peak', round(float(np.abs(mix).max()), 3))
