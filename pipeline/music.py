# Usage: python3 music.py EPISODE_DIR
# Synthesized BGM: 120 BPM synthwave/electro, key/progression/arp vary per episode, with
# transition whooshes at scene cuts and voice ducking. Output: music.wav (stereo).
import json, os, numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt

import sys, hashlib
EP = os.path.abspath(sys.argv[1]); D = os.path.join(EP, "build") + "/"
SR = 44100
DURS = json.load(open(D + "durs.json"))
SEED = int(hashlib.md5(os.path.basename(EP).encode()).hexdigest()[:8], 16)
VAR = np.random.default_rng(SEED)
TOTAL = sum(DURS)
N = int(TOTAL * SR) + SR
BPM = 120  # fixed: video beat-sync assumes 0.5 s beats
BEAT = 60 / BPM; BAR = 4 * BEAT; S16 = BEAT / 4
rng = np.random.default_rng(SEED)
L = np.zeros(N); R = np.zeros(N)
bus = {k: np.zeros(N) for k in ["pad", "bass", "arp", "drums", "fx"]}

def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], "band", fs=SR, output="sos"), x)
def saw(f, t, maxf=7000):
    n = max(1, min(24, int(maxf / f))); out = np.zeros_like(t)
    for k in range(1, n + 1): out += np.sin(2 * np.pi * k * f * t) / k
    return out * 0.6
def add(name, start, sig):
    i = int(start * SR)
    if i >= N: return
    j = min(N, i + len(sig)); bus[name][i:j] += sig[: j - i]
def m2f(m): return 440 * 2 ** ((m - 69) / 12)

# chords as midi (A minor): Am, F, C, G
# progression + key vary per episode (seeded by episode folder name)
PROGS = [  # (chords as semitone offsets from key root, bass root offsets)
    ([[0, 3, 7], [-4, 0, 3], [-9, -5, -2], [-2, 2, 5]], [0, -4, 3, -2]),      # i-VI-III-VII
    ([[0, 3, 7], [-2, 2, 5], [-4, 0, 3], [-5, -2, 2]], [0, -2, -4, -5]),      # i-VII-VI-v
    ([[-4, 0, 3], [-9, -5, -2], [-2, 2, 5], [0, 3, 7]], [-4, 3, -2, 0]),      # VI-III-VII-i
    ([[0, 3, 7], [-7, -3, 0], [-4, 0, 3], [-2, 2, 5]], [0, -7, -4, -2]),      # i-iv-VI-VII
]
key = 57 + int(VAR.integers(-3, 4)); pc, pr = PROGS[int(VAR.integers(0, len(PROGS)))]
CH = [[key + o for o in c] for c in pc]; ROOT = [key - 12 + o for o in pr]
ARP_PATS = [[0, 1, 2, 3, 2, 1, 0, 2, 0, 1, 2, 3, 4, 3, 2, 1], [0, 2, 1, 3, 0, 2, 4, 3, 0, 2, 1, 3, 4, 2, 3, 1], [0, 0, 2, 1, 3, 2, 4, 2, 0, 0, 2, 1, 3, 4, 3, 2]]
APAT = ARP_PATS[int(VAR.integers(0, len(ARP_PATS)))]
nbars = int(np.ceil(TOTAL / BAR))
FULL = 4                      # bar where full beat drops (t = 8 s)
END_BREAK = nbars - 1         # last bar: breakdown

for b in range(nbars):
    t0 = b * BAR; c = CH[b % 4]; r = ROOT[b % 4]
    # pad: detuned saws, soft attack/release
    tt = np.arange(int((BAR + 0.4) * SR)) / SR
    env = np.minimum(1, tt / 0.25) * np.minimum(1, np.maximum(0, (BAR + 0.4 - tt) / 0.4))
    pad = sum(saw(m2f(m) * d, tt, 3000) for m in c for d in (0.996, 1.004))
    add("pad", t0, lp(pad, 1600 if b >= FULL else 900) * env * 0.05)
    # bass: 8th-note pumping, sine + filtered saw
    if b >= 2 and b != END_BREAK:
        for k in range(8):
            f = m2f(r - 12 if k % 2 == 0 else r)
            tt = np.arange(int(BEAT / 2 * SR)) / SR
            e = np.exp(-tt * 6) * np.minimum(1, tt / 0.005)
            s = np.sin(2 * np.pi * f * tt) + 0.35 * lp(saw(f, tt, 2000), 500)
            add("bass", t0 + k * BEAT / 2, s * e * 0.22)
    # arp: 16ths over chord tones, pluck
    if b >= 1:
        pat = APAT
        tones = [c[0] + 12, c[1] + 12, c[2] + 12, c[0] + 24, c[1] + 24]
        for k in range(16):
            if b < FULL and k % 2: continue
            f = m2f(tones[pat[k]]); tt = np.arange(int(0.28 * SR)) / SR
            e = np.exp(-tt * 16) * np.minimum(1, tt / 0.003)
            s = (np.sign(np.sin(2 * np.pi * f * tt)) * 0.4 + saw(f, tt, 6000)) * e
            add("arp", t0 + k * S16, lp(s, 3200) * 0.06)
    # drums
    for k in range(4):
        bt = t0 + k * BEAT
        if b >= 2 and b != END_BREAK:  # kick
            tt = np.arange(int(0.35 * SR)) / SR
            ph = 2 * np.pi * np.cumsum(48 + 110 * np.exp(-tt * 28)) / SR
            add("drums", bt, np.sin(ph) * np.exp(-tt * 7) * 0.55)
        if b >= FULL and b != END_BREAK and k in (1, 3):  # clap
            tt = np.arange(int(0.25 * SR)) / SR
            n = bp(rng.standard_normal(len(tt)), 900, 3500)
            e = np.exp(-tt * 18) + 0.6 * np.exp(-np.maximum(0, tt - 0.012) * 30) * (tt > 0.012)
            add("drums", bt, n * e * 0.22)
        for h in range(2 if b >= FULL else 1):  # hats on offbeats (+16ths in full)
            ht = bt + BEAT / 2 + (h * BEAT / 4 if h else 0)
            tt = np.arange(int(0.06 * SR)) / SR
            add("drums", ht, hp(rng.standard_normal(len(tt)), 7000) * np.exp(-tt * 70) * (0.07 if h == 0 else 0.035))

# riser into the drop + impacts
def riser(end, dur, amp):
    tt = np.arange(int(dur * SR)) / SR; n = rng.standard_normal(len(tt))
    out = np.zeros_like(tt); seg = 2048
    for i in range(0, len(tt), seg):
        f = 400 + 7000 * (i / len(tt)) ** 2
        out[i:i + seg] = bp(n[i:i + seg], f, min(f * 1.6, 18000))
    add("fx", end - dur, out * (tt / dur) ** 2 * amp)
def impact(t, amp):
    tt = np.arange(int(1.6 * SR)) / SR
    ph = 2 * np.pi * np.cumsum(35 + 60 * np.exp(-tt * 8)) / SR
    boom = np.sin(ph) * np.exp(-tt * 2.5) + lp(rng.standard_normal(len(tt)), 1200) * np.exp(-tt * 6) * 0.4
    add("fx", t, boom * amp)
impact(0.0, 0.5)
riser(FULL * BAR, 2.0, 0.12)
impact(FULL * BAR, 0.35)

# whooshes at every scene cut
cut = 0
for d in DURS[:-1]:
    cut += d; tt = np.arange(int(0.7 * SR)) / SR; n = rng.standard_normal(len(tt))
    env = np.sin(np.pi * tt / 0.7) ** 2
    w = np.zeros_like(tt)
    for i in range(0, len(tt), 1024):
        f = 300 + 3500 * np.sin(np.pi * i / len(tt)); w[i:i + 1024] = bp(n[i:i + 1024], f, f * 2.2)
    add("fx", cut - 0.45, w * env * 0.16)
    impact(cut, 0.12)

# kick sidechain on pad/bass/arp
tt = np.arange(N) / SR
pos = np.mod(tt, BEAT); bar_i = (tt // BAR).astype(int)
sc = 1 - 0.55 * np.exp(-pos * 9) * ((bar_i >= 2) & (bar_i != END_BREAK))
for k in ("pad", "bass", "arp"): bus[k] *= sc

# voice ducking
v, vsr = sf.read(D + "voice.wav")
if v.ndim > 1: v = v.mean(1)
v = np.interp(np.arange(N) / SR, np.arange(len(v)) / vsr, np.abs(v), right=0)
env = lp(v, 6, 1); nz = env[env > 1e-4]; env = env / (np.percentile(nz, 90) + 1e-9) if nz.size else env * 0
duck = 1 - 0.5 * np.clip(env, 0, 1)
duck = lp(duck, 4, 1)

mus = (bus["pad"] + bus["bass"] + bus["arp"] + bus["drums"]) * duck
# stereo: arp ping-pong delay (3/16 note)
dl = int(3 * S16 * SR); echo = np.zeros(N); echo[dl:] = bus["arp"][:-dl] * duck[dl:] * 0.35
echo2 = np.zeros(N); echo2[2 * dl:] = bus["arp"][:-2 * dl] * duck[2 * dl:] * 0.18
L = mus + echo + bus["fx"] * 0.9; R = mus + echo2 + bus["fx"] * 0.9
# fades
fade = np.ones(N); fi = int(1.5 * SR); fe = int(TOTAL * SR)
fade[fe - fi:fe] = np.linspace(1, 0, fi); fade[fe:] = 0
out = np.stack([L * fade, R * fade], 1)[: int(TOTAL * SR)]
out = np.tanh(out * 1.2) / 1.2
out *= 0.7 / np.max(np.abs(out))
sf.write(D + "music.wav", out.astype(np.float32), SR)
print("music.wav", TOTAL, "s, bars", nbars)
