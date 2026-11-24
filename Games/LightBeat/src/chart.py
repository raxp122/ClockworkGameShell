# -*- coding: utf-8 -*-
"""
Chart generation shared by the song tools (Python 3) and the game
(Python 2 on the GameShell, for MIDI files).

notes: list of (time_seconds, midi_pitch, beat_position) sorted by time.
"""
from __future__ import division

# name: (grid in beats a note must start on, min seconds between notes)
DIFFICULTY = [
    ("easy", 1.0, 0.38),
    ("normal", 0.5, 0.19),
    ("hard", 0.0, 0.095),
]
GRID_TOLERANCE = 0.08   # beats: how far from the grid a note may start
CHORD_WINDOW = 0.03     # seconds: notes this close are one chord (keep the top)


def on_grid(beat, grid):
    if not grid or beat is None:
        return True
    return abs(beat - round(beat / grid) * grid) <= GRID_TOLERANCE


def top_notes(notes):
    """Collapse chords to their highest note."""
    out = []
    for t, p, b in notes:
        if out and t - out[-1][0] < CHORD_WINDOW:
            if p > out[-1][1]:
                out[-1] = (out[-1][0], p, out[-1][2])
            continue
        out.append((t, p, b))
    return out


def make_chart(notes, grid, min_gap):
    kept, last_t = [], -9.0
    for t, p, b in top_notes(notes):
        if not on_grid(b, grid) or t - last_t < min_gap - 1e-6:
            continue
        kept.append((t, p))
        last_t = t

    # Lanes follow the melody's contour inside a small window
    lanes, prev_lane, prev_pitch = [], 1, None
    for i, (_t, p) in enumerate(kept):
        win = [q for _, q in kept[max(0, i - 3):i + 4]]
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
    return [[round(t, 4), l] for (t, _), l in zip(kept, lanes)]


def make_charts(notes):
    return dict((name, make_chart(notes, grid, gap)) for name, grid, gap in DIFFICULTY)
