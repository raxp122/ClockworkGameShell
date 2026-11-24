#!/usr/bin/env python3
"""
Render LightBeat songs: chiptune audio (.ogg) + note charts (.json).

The chart is generated from the same melody that is rendered to audio, so
notes are always exactly in sync with the music.

Usage:  python3 Games/LightBeat/tools/make_songs.py
Needs:  numpy, ffmpeg (with libvorbis)
"""
import json
import os
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from songs import SONGS  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "src", "songs")
SR = 44100
LEAD_IN = 2.5     # seconds of silence before the first bar (notes need to fall)
TAIL = 2.0
BAR = 8           # sixteenths per bar (2/4)

NOTE_BASE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# Difficulty: (grid in sixteenths a note must start on, min seconds between notes)
DIFFICULTY = {
    "easy": (4, 0.38),
    "normal": (2, 0.19),
    "hard": (1, 0.10),
}


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------
def note_to_midi(name):
    letter, rest = name[0].upper(), name[1:]
    acc = 0
    while rest and rest[0] in "#b":
        acc += 1 if rest[0] == "#" else -1
        rest = rest[1:]
    return 12 * (int(rest) + 1) + NOTE_BASE[letter] + acc


def parse_melody(seq):
    """-> list of (start16, length16, midi or None)"""
    events, pos = [], 0
    for tok in seq.replace("|", " ").split():
        name, length = tok.rsplit(".", 1)
        length = int(length)
        events.append((pos, length, None if name == "r" else note_to_midi(name)))
        pos += length
    return events, pos


def parse_chord(ch):
    root = ch[0]
    rest = ch[1:]
    if rest[:1] in ("#", "b"):
        root += rest[0]
        rest = rest[1:]
    midi = note_to_midi(root + "3") - 12  # around C2..B2
    if rest == "m":
        iv = [0, 3, 7]
    elif rest == "7":
        iv = [0, 4, 7, 10]
    elif rest == "m7":
        iv = [0, 3, 7, 10]
    elif rest == "":
        iv = [0, 4, 7]
    else:
        raise ValueError("unknown chord " + ch)
    return midi, iv


def assemble(song):
    melody, chords, pos = [], [], 0
    for sec in song["form"]:
        seq, chord_str = song["sections"][sec]
        evs, length = parse_melody(seq)
        bars = chord_str.split()
        if length != len(bars) * BAR:
            raise ValueError("%s/%s: melody is %d sixteenths, chords cover %d"
                             % (song["id"], sec, length, len(bars) * BAR))
        melody += [(pos + s, l, m) for s, l, m in evs]
        chords += [(pos + i * BAR, parse_chord(c)) for i, c in enumerate(bars)]
        pos += length
    return melody, chords, pos


# --------------------------------------------------------------------------
# Synth
# --------------------------------------------------------------------------
def freq(midi):
    return 440.0 * 2 ** ((midi - 69) / 12.0)


def envelope(n, attack=0.004, decay=0.12, sustain=0.6, release=0.02):
    t = np.arange(n) / SR
    env = np.where(t < attack, t / attack,
                   sustain + (1 - sustain) * np.exp(-(t - attack) / decay))
    r = int(release * SR)
    if r and n > r:
        env[-r:] *= np.linspace(1, 0, r)
    return env


def square(f, n, duty=0.25):
    ph = (np.arange(n) * f / SR) % 1.0
    return np.where(ph < duty, 1.0, -1.0)


def triangle(f, n):
    ph = (np.arange(n) * f / SR) % 1.0
    return 2 * np.abs(2 * ph - 1) - 1


class Mixer(object):
    def __init__(self, seconds):
        self.buf = np.zeros(int(seconds * SR) + SR)
        self.rng = np.random.default_rng(1234)

    def add(self, t, wave):
        i = int(round(t * SR))
        self.buf[i:i + len(wave)] += wave[:max(0, len(self.buf) - i)]

    def tone(self, t, dur, midi, vol, kind="square", duty=0.25, gate=0.88, **env):
        n = int(dur * gate * SR)
        if n <= 0:
            return
        w = square(freq(midi), n, duty) if kind == "square" else triangle(freq(midi), n)
        self.add(t, w * envelope(n, **env) * vol)

    def kick(self, t, vol=0.5):
        n = int(0.14 * SR)
        tt = np.arange(n) / SR
        f = 45 + 110 * np.exp(-tt / 0.03)
        w = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt / 0.06)
        self.add(t, w * vol)

    def snare(self, t, vol=0.25):
        n = int(0.12 * SR)
        tt = np.arange(n) / SR
        w = self.rng.uniform(-1, 1, n) * np.exp(-tt / 0.04)
        w += 0.4 * np.sin(2 * np.pi * 190 * tt) * np.exp(-tt / 0.03)
        self.add(t, w * vol)

    def hat(self, t, vol=0.08):
        n = int(0.04 * SR)
        tt = np.arange(n) / SR
        w = np.diff(self.rng.uniform(-1, 1, n + 1)) * np.exp(-tt / 0.01)
        self.add(t, w * vol)


DRUMS = {
    #          kick         snare        hat
    "march": ([0, 4], [6], [0, 2, 4, 6]),
    "rag": ([0, 4], [2, 6], [1, 3, 5, 7]),
    "galop": ([0, 4], [2, 6], [0, 1, 2, 3, 4, 5, 6, 7]),
}


def render(song, melody, chords, total16):
    s16 = 60.0 / song["bpm"] / 4
    length = LEAD_IN + total16 * s16 + TAIL
    mx = Mixer(length)
    at = lambda p: LEAD_IN + p * s16  # noqa: E731

    # Melody (lead square) + quiet octave-down shadow for body
    for start, ln, midi in melody:
        if midi is None:
            continue
        mx.tone(at(start), ln * s16, midi, song.get("lead", 0.25), duty=0.25)
        mx.tone(at(start), ln * s16, midi - 12, 0.06, duty=0.5)

    # Bass + chords, one pattern per bar
    style = song["bass"]
    for start, (root, iv) in chords:
        third, fifth = root + iv[1], root + iv[2]
        if style == "alberti":
            seq = [(0, root + 12), (2, fifth + 12), (4, third + 12), (6, fifth + 12)]
            for off, m in seq:
                mx.tone(at(start + off), 2 * s16, m, 0.22, kind="triangle")
        else:
            low2 = fifth - 12 if style == "stride" else fifth
            for off, m in ((0, root), (4, low2)):
                mx.tone(at(start + off), 2 * s16, m + 12, 0.28, kind="triangle")
            for off in (2, 6):
                for i in iv[1:]:
                    mx.tone(at(start + off), 1.5 * s16, root + 24 + i, 0.045,
                            duty=0.5, gate=0.6, decay=0.05, sustain=0.2)

    # Drums (skip during the count-in silence)
    kicks, snares, hats = DRUMS[song["drums"]]
    for bar in range(0, total16, BAR):
        for o in kicks:
            mx.kick(at(bar + o))
        for o in snares:
            mx.snare(at(bar + o))
        for o in hats:
            mx.hat(at(bar + o))

    buf = mx.buf[:int(length * SR)]
    buf = buf / max(1e-9, np.max(np.abs(buf))) * 0.89
    return buf, length, s16


def encode_ogg(buf, path):
    pcm = (buf * 32767).astype("<i2").tobytes()
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "s16le", "-ar", str(SR),
           "-ac", "1", "-i", "-", "-c:a", "libvorbis", "-q:a", "3",
           "-map_metadata", "-1", "-fflags", "+bitexact", "-flags:a", "+bitexact",
           path]
    subprocess.run(cmd, input=pcm, check=True)


# --------------------------------------------------------------------------
# Charts
# --------------------------------------------------------------------------
def make_chart(melody, s16, grid, min_gap):
    notes, last_t = [], -9.0
    for start, _ln, midi in melody:
        if midi is None or start % grid:
            continue
        t = LEAD_IN + start * s16
        if t - last_t < min_gap - 1e-6:
            continue
        notes.append((t, midi))
        last_t = t

    # Lanes follow the melody's contour inside a small window
    lanes, prev_lane, prev_pitch = [], 1, None
    for i, (_t, p) in enumerate(notes):
        win = [q for _, q in notes[max(0, i - 3):i + 4]]
        lo, hi = min(win), max(win)
        lane = prev_lane if hi == lo else int(round((p - lo) / float(hi - lo) * 3))
        if prev_pitch is not None:
            if p == prev_pitch:
                lane = prev_lane
            elif lane == prev_lane:  # pitch moved: move the lane the same way
                lane = min(3, lane + 1) if p > prev_pitch else max(0, lane - 1)
                if lane == prev_lane:
                    lane = prev_lane - 1 if p > prev_pitch else prev_lane + 1
        lanes.append(lane)
        prev_lane, prev_pitch = lane, p
    return [[round(t, 4), l] for (t, _), l in zip(notes, lanes)]


def main():
    os.makedirs(OUT, exist_ok=True)
    index = []
    for song in SONGS:
        melody, chords, total16 = assemble(song)
        buf, length, s16 = render(song, melody, chords, total16)
        encode_ogg(buf, os.path.join(OUT, song["id"] + ".ogg"))
        charts = {d: make_chart(melody, s16, g, gap)
                  for d, (g, gap) in DIFFICULTY.items()}
        meta = {
            "id": song["id"], "title": song["title"], "composer": song["composer"],
            "year": song["year"], "bpm": song["bpm"], "length": round(length, 3),
            "audio": song["id"] + ".ogg", "charts": charts,
        }
        with open(os.path.join(OUT, song["id"] + ".json"), "w") as f:
            json.dump(meta, f, separators=(",", ":"))
        index.append(song["id"])
        print("%-12s %5.1fs  easy %3d  normal %3d  hard %3d" % (
            song["id"], length, len(charts["easy"]), len(charts["normal"]),
            len(charts["hard"])))
    with open(os.path.join(OUT, "index.json"), "w") as f:
        json.dump(index, f)


if __name__ == "__main__":
    main()
