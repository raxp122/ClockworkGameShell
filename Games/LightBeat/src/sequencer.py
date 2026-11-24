# -*- coding: utf-8 -*-
"""
Real-time chiptune player for MIDI songs.

Every note starts a short looping waveform on a pygame mixer channel and is
faded out when the note ends; SDL does the mixing in C, so this stays light
enough for the GameShell. Pure Python, Python 2 and 3.
"""
from __future__ import division

import heapq
import math
import random
from array import array

import pygame

from midi import DRUM_CHANNEL

LOOP_SECONDS = 0.05
NUM_CHANNELS = 24


def _to_bytes(arr):
    return arr.tobytes() if hasattr(arr, "tobytes") else arr.tostring()


class Synth(object):
    """Builds and caches pygame Sounds for tones and drums."""
    def __init__(self):
        init = pygame.mixer.get_init()
        self.ok = bool(init)
        if not self.ok:
            return
        self.rate, size, self.stereo = init[0], init[1], init[2] >= 2
        self.ok = abs(size) == 16
        self.cache = {}
        self.rng = random.Random(1)
        pygame.mixer.set_num_channels(NUM_CHANNELS)

    def _sound(self, samples):
        arr = array("h")
        for v in samples:
            s = int(v * 32000)
            arr.append(s)
            if self.stereo:
                arr.append(s)
        data = _to_bytes(arr)
        try:
            return pygame.mixer.Sound(buffer=data)
        except TypeError:          # very old pygame
            return pygame.mixer.Sound(data)

    def tone(self, wave, pitch):
        key = (wave, pitch)
        snd = self.cache.get(key)
        if snd is None:
            f = 440.0 * 2 ** ((pitch - 69) / 12.0)
            periods = max(1, int(round(LOOP_SECONDS * f)))
            n = max(2, int(round(periods * self.rate / f)))
            step = periods / float(n)
            if wave == "triangle":
                samples = [2 * abs(2 * ((i * step) % 1.0) - 1) - 1 for i in range(n)]
            else:
                duty = 0.25 if wave == "pulse" else 0.5
                samples = [1.0 if (i * step) % 1.0 < duty else -1.0 for i in range(n)]
            snd = self.cache[key] = self._sound(samples)
        return snd

    def drum(self, kind):
        snd = self.cache.get(kind)
        if snd is None:
            r = self.rate
            rnd = self.rng.uniform
            if kind == "kick":
                n, ph, out = int(0.14 * r), 0.0, []
                for i in range(n):
                    t = i / float(r)
                    ph += (45 + 110 * math.exp(-t / 0.03)) / r
                    out.append(math.sin(2 * math.pi * ph) * math.exp(-t / 0.06) * 0.9)
            elif kind == "snare":
                n = int(0.12 * r)
                out = [(rnd(-1, 1) * math.exp(-i / (0.04 * r)) +
                        0.4 * math.sin(2 * math.pi * 190 * i / r) * math.exp(-i / (0.03 * r)))
                       * 0.55 for i in range(n)]
            else:
                n, prev, out = int(0.04 * r), 0.0, []
                for i in range(n):
                    v = rnd(-1, 1)
                    out.append((v - prev) * 0.25 * math.exp(-i / (0.01 * r)))
                    prev = v
            snd = self.cache[kind] = self._sound(out)
        return snd


def drum_kind(pitch):
    if pitch in (35, 36):
        return "kick"
    if pitch in (37, 38, 39, 40):
        return "snare"
    return "hat"


class Sequencer(object):
    """Plays a MIDI song's notes. Call update() every frame with the song time."""
    def __init__(self, synth, song, volume=1.0):
        self.synth = synth
        self.volume = volume
        self.ons = []        # (time, end, sound, level, one_shot)
        self.offs = []       # heap of (time, seq, channel, sound)
        self.seq = 0
        self.i = 0
        if not synth.ok:
            return
        part = song["parts"][song["part"]]
        means = dict(((p["track"], p["channel"]), p["mean"]) for p in song["parts"])
        for start, end, ch, pitch, vel, track, _beat in song["notes"]:
            level = 0.35 + 0.65 * vel / 127.0
            if ch == DRUM_CHANNEL:
                kind = drum_kind(pitch)
                lvl = {"kick": 0.9, "snare": 0.6, "hat": 0.35}[kind]
                self.ons.append((start, end, synth.drum(kind), lvl * level, True))
            elif track == part["track"] and ch == part["channel"]:
                self.ons.append((start, end, synth.tone("pulse", pitch), 0.42 * level, False))
            elif means.get((track, ch), 60) < 52:
                self.ons.append((start, end, synth.tone("triangle", pitch), 0.55 * level, False))
            else:
                self.ons.append((start, end, synth.tone("square", pitch), 0.12 * level, False))
        self.ons.sort(key=lambda e: e[0])

    def update(self, t):
        while self.i < len(self.ons) and self.ons[self.i][0] <= t:
            start, end, snd, level, one_shot = self.ons[self.i]
            self.i += 1
            if t - start > 0.25:      # far behind (e.g. after a hiccup): skip
                continue
            ch = snd.play() if one_shot else snd.play(-1)
            if ch is None:
                continue
            ch.set_volume(level * self.volume)
            if not one_shot:
                self.seq += 1
                heapq.heappush(self.offs, (end, self.seq, ch, snd))
        while self.offs and self.offs[0][0] <= t:
            _end, _s, ch, snd = heapq.heappop(self.offs)
            if ch.get_sound() is snd:
                ch.fadeout(30)

    def set_volume(self, volume):
        self.volume = volume

    def stop(self):
        if self.synth.ok:
            pygame.mixer.stop()
        self.offs = []
