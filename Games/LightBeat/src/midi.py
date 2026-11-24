# -*- coding: utf-8 -*-
"""
Minimal Standard MIDI File reader (formats 0 and 1) and the code that turns
a .mid file into a LightBeat song. Pure Python, works on Python 2 and 3.
"""
from __future__ import division

import os
import struct

from chart import make_charts

LEAD_IN = 2.5    # seconds before the first note
TAIL = 2.0
DRUM_CHANNEL = 9


class MidiError(Exception):
    pass


def _varlen(data, pos):
    value = 0
    while True:
        if pos >= len(data):
            raise MidiError("truncated variable-length value")
        b = data[pos]
        pos += 1
        value = (value << 7) | (b & 0x7F)
        if not b & 0x80:
            return value, pos


def read_midi(path):
    try:
        return _read_midi(path)
    except (IndexError, struct.error):
        raise MidiError("the file is damaged or incomplete")


def _read_midi(path):
    """-> dict(ppq, notes, tempos, names)
    notes:  (start_tick, end_tick, channel, pitch, velocity, track)
    tempos: (tick, microseconds_per_beat), sorted
    names:  {track: name}"""
    with open(path, "rb") as f:
        data = bytearray(f.read())
    if data[:4] != bytearray(b"MThd"):
        raise MidiError("not a MIDI file")
    hlen, fmt, ntracks, division = struct.unpack(">IHHH", bytes(data[4:14]))
    if division & 0x8000:
        raise MidiError("SMPTE time division is not supported")
    if fmt not in (0, 1):
        raise MidiError("MIDI format %d is not supported" % fmt)
    ppq = division
    pos = 8 + hlen
    notes, tempos, names = [], [], {}

    for track in range(ntracks):
        if data[pos:pos + 4] != bytearray(b"MTrk"):
            raise MidiError("missing track %d" % track)
        tlen = struct.unpack(">I", bytes(data[pos + 4:pos + 8]))[0]
        p, end = pos + 8, pos + 8 + tlen
        pos = end
        tick, status = 0, 0
        open_notes = {}
        while p < end:
            delta, p = _varlen(data, p)
            tick += delta
            b = data[p]
            if b & 0x80:
                status = b
                p += 1
            elif not status:
                raise MidiError("running status without a status byte")
            kind, ch = status & 0xF0, status & 0x0F
            if status == 0xFF:                      # meta event
                mtype = data[p]
                mlen, p = _varlen(data, p + 1)
                payload = data[p:p + mlen]
                p += mlen
                if mtype == 0x51 and mlen == 3:
                    tempos.append((tick, (payload[0] << 16) | (payload[1] << 8) | payload[2]))
                elif mtype == 0x03 and track not in names:
                    names[track] = bytes(payload).decode("latin-1").strip()
                elif mtype == 0x2F:
                    break
                status = 0
            elif status in (0xF0, 0xF7):            # sysex
                slen, p = _varlen(data, p)
                p += slen
                status = 0
            elif kind in (0x80, 0x90):
                pitch, vel = data[p], data[p + 1]
                p += 2
                key = (ch, pitch)
                if kind == 0x90 and vel > 0:
                    open_notes.setdefault(key, []).append((tick, vel))
                elif open_notes.get(key):
                    start, v = open_notes[key].pop(0)
                    notes.append((start, tick, ch, pitch, v, track))
            elif kind in (0xA0, 0xB0, 0xE0):
                p += 2
            elif kind in (0xC0, 0xD0):
                p += 1
            else:
                raise MidiError("unknown event 0x%02X" % status)
        for (ch, pitch), starts in open_notes.items():   # never released
            for start, v in starts:
                notes.append((start, tick, ch, pitch, v, track))

    tempos.sort()
    if not tempos or tempos[0][0] > 0:
        tempos.insert(0, (0, 500000))
    notes.sort()
    return {"ppq": ppq, "notes": notes, "tempos": tempos, "names": names}


class TempoMap(object):
    def __init__(self, ppq, tempos):
        self.ppq = ppq
        self.points = []          # (tick, seconds, us_per_beat)
        sec, last_tick, last_us = 0.0, 0, tempos[0][1]
        for tick, us in tempos:
            sec += (tick - last_tick) * last_us / 1e6 / ppq
            self.points.append((tick, sec, us))
            last_tick, last_us = tick, us

    def seconds(self, tick):
        lo, hi = 0, len(self.points) - 1
        while lo < hi:                         # last point with point.tick <= tick
            mid = (lo + hi + 1) // 2
            if self.points[mid][0] <= tick:
                lo = mid
            else:
                hi = mid - 1
        t0, s0, us = self.points[lo]
        return s0 + (tick - t0) * us / 1e6 / self.ppq


def find_parts(midi):
    """Groups of melodic notes by (track, channel), best melody candidate first."""
    groups = {}
    for n in midi["notes"]:
        if n[2] == DRUM_CHANNEL:
            continue
        groups.setdefault((n[5], n[2]), []).append(n)
    parts = []
    most = max([len(g) for g in groups.values()] or [1])
    for (track, ch), ns in groups.items():
        mean = sum(n[3] for n in ns) / float(len(ns))
        name = midi["names"].get(track) or "Track %d" % (track + 1)
        if len(groups) > 1 and any(k[0] == track and k[1] != ch for k in groups):
            name += " ch%d" % (ch + 1)
        # The melody is usually high and busy: rank by pitch, ignore tiny parts
        rank = mean if len(ns) >= 0.2 * most else mean - 100
        parts.append({"track": track, "channel": ch, "name": name,
                      "count": len(ns), "mean": mean, "rank": rank})
    parts.sort(key=lambda p: -p["rank"])
    return parts


def load_midi_song(path):
    midi = read_midi(path)
    parts = find_parts(midi)
    if not parts:
        raise MidiError("no melodic notes")
    tmap = TempoMap(midi["ppq"], midi["tempos"])
    first = min(n[0] for n in midi["notes"])
    shift = LEAD_IN - tmap.seconds(first)
    timed = []   # (start_s, end_s, channel, pitch, velocity, track, beat)
    for s, e, ch, pitch, vel, track in midi["notes"]:
        timed.append((tmap.seconds(s) + shift, tmap.seconds(e) + shift, ch, pitch,
                      vel, track, s / float(midi["ppq"])))
    length = max(n[1] for n in timed) + TAIL
    base = os.path.basename(path)
    title = os.path.splitext(base)[0].replace("_", " ")
    song = {
        "id": "midi:" + base, "kind": "midi", "path": path,
        "title": title, "composer": "MIDI file", "year": None,
        "bpm": int(round(60e6 / midi["tempos"][0][1])),
        "length": round(length, 3), "parts": parts, "part": 0, "notes": timed,
    }
    set_part(song, 0)
    return song


def set_part(song, index):
    """Choose which part is played on the lanes and rebuild the charts."""
    song["part"] = index % len(song["parts"])
    part = song["parts"][song["part"]]
    melody = [(n[0], n[3], n[6]) for n in song["notes"]
              if n[5] == part["track"] and n[2] == part["channel"]]
    song["charts"] = make_charts(melody)
