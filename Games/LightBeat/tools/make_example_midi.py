#!/usr/bin/env python3
"""
Write src/midi/Ode_to_Joy.mid: an example MIDI file (Beethoven, public domain)
shipped with LightBeat to show how user MIDI files work. It is a format 1
file with a tempo track, melody, bass and drums (channel 10), and uses
running status, like most MIDI files found online.

Usage:  python3 Games/LightBeat/tools/make_example_midi.py
"""
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "src", "midi", "Ode_to_Joy.mid")
PPQ = 480
NOTE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

# (note, beats). One phrase per line.
MELODY = """
E4 1 E4 1 F4 1 G4 1 G4 1 F4 1 E4 1 D4 1 C4 1 C4 1 D4 1 E4 1 E4 1.5 D4 0.5 D4 2
E4 1 E4 1 F4 1 G4 1 G4 1 F4 1 E4 1 D4 1 C4 1 C4 1 D4 1 E4 1 D4 1.5 C4 0.5 C4 2
D4 1 D4 1 E4 1 C4 1 D4 1 E4 0.5 F4 0.5 E4 1 C4 1 D4 1 E4 0.5 F4 0.5 E4 1 D4 1 C4 1 D4 1 G3 2
E4 1 E4 1 F4 1 G4 1 G4 1 F4 1 E4 1 D4 1 C4 1 C4 1 D4 1 E4 1 D4 1.5 C4 0.5 C4 2
"""
BASS = "C3 C3 G2 C3  C3 C3 G2 C3  G2 C3 G2 G2  C3 C3 G2 C3"   # one per bar (4 beats)


def midi_num(name):
    return 12 * (int(name[-1]) + 1) + NOTE[name[0]]


def varlen(v):
    out = [v & 0x7F]
    v >>= 7
    while v:
        out.insert(0, (v & 0x7F) | 0x80)
        v >>= 7
    return bytes(out)


def track(events, name):
    """events: (tick, bytes) absolute; running status for note events."""
    data = b"\x00\xff\x03" + varlen(len(name)) + name.encode()
    last, status = 0, None
    for tick, ev in sorted(events, key=lambda e: (e[0], e[1][0] & 0xF0 != 0x80)):
        data += varlen(tick - last)
        if ev[0] < 0xF0 and ev[0] == status:   # running status (channel msgs only)
            data += ev[1:]
        else:
            data += ev
            status = ev[0] if ev[0] < 0xF0 else None
        last = tick
    data += b"\x00\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + data


def notes_track(notes, ch, name):
    ev = []
    for start, length, pitch, vel in notes:
        ev.append((start, bytes([0x90 | ch, pitch, vel])))
        ev.append((start + length, bytes([0x90 | ch, pitch, 0])))   # note-on vel 0 = off
    return track(ev, name)


def main():
    toks = MELODY.split()
    mel, t = [], 0
    for name, beats in zip(toks[::2], toks[1::2]):
        ln = int(float(beats) * PPQ)
        mel.append((t, ln - 20, midi_num(name) + 12, 100))
        t += ln
    total = t
    bass = [(i * 4 * PPQ, 4 * PPQ - 40, midi_num(n), 90) for i, n in enumerate(BASS.split())]
    drums = []
    for beat in range(total // PPQ):
        drums.append((beat * PPQ, 60, 36 if beat % 2 == 0 else 38, 100))
        drums.append((beat * PPQ + PPQ // 2, 60, 42, 70))
    tempo = track([(0, b"\xff\x51\x03" + struct.pack(">I", 500000)[1:]),
                   (0, b"\xff\x58\x04\x04\x02\x18\x08")], "Tempo")
    body = (tempo + notes_track(mel, 0, "Melody") + notes_track(bass, 1, "Bass")
            + notes_track(drums, 9, "Drums"))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "wb") as f:
        f.write(b"MThd" + struct.pack(">IHHH", 6, 1, 4, PPQ) + body)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
