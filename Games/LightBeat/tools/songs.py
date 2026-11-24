# -*- coding: utf-8 -*-
"""
Song sheets for LightBeat, written as our own chiptune arrangements of
public-domain compositions.

Notation: space separated tokens "<note><octave>.<length>" where length is in
sixteenth notes, e.g. "C#5.2" (eighth note), "r.4" (quarter rest).
"|" is ignored and only helps reading. Every song is in 2/4: one bar = 8
sixteenths, and "chords" has one chord per bar (used for bass and harmony).

A section is (melody, chords). "form" lists the sections in playing order.
"""

# ---------------------------------------------------------------------------
# W. A. Mozart - Rondo alla Turca (Piano Sonata K. 331, 3rd mvt.), 1783
# ---------------------------------------------------------------------------
TURCA_PICKUP = "B4.1 A4.1 G#4.1 A4.1"

TURCA = {
    "id": "turca",
    "title": "Rondo alla Turca",
    "composer": "W. A. Mozart",
    "year": 1783,
    "bpm": 126,
    "bass": "alberti",
    "drums": "march",
    "lead": 0.25,
    "sections": {
        "intro": ("r.4 " + TURCA_PICKUP, "Am"),
        "A": (
            "C5.2 r.2 D5.1 C5.1 B4.1 C5.1 | E5.2 r.2 F5.1 E5.1 D#5.1 E5.1 |"
            "B5.1 A5.1 G#5.1 A5.1 B5.1 A5.1 G#5.1 A5.1 | C6.4 A5.2 C6.2 |"
            "B5.2 A5.2 G5.2 A5.2 | B5.2 A5.2 G5.2 A5.2 |"
            "B5.2 A5.2 G5.2 F#5.2 | E5.4 " + TURCA_PICKUP,
            "Am Am Am Am Em Am B7 E",
        ),
        "A_end": (
            "C5.2 r.2 D5.1 C5.1 B4.1 C5.1 | E5.2 r.2 F5.1 E5.1 D#5.1 E5.1 |"
            "B5.1 A5.1 G#5.1 A5.1 B5.1 A5.1 G#5.1 A5.1 | C6.4 A5.2 C6.2 |"
            "B5.2 A5.2 G#5.2 A5.2 | E5.2 F5.2 D5.2 B4.2 | A4.4 E4.4 | A4.4 r.4",
            "Am Am Am Am E Dm E Am",
        ),
        "B": (
            "E5.2 F5.2 G5.2 G5.2 | A5.2 G5.2 F5.2 E5.2 | D5.4 E5.2 F5.2 |"
            "G5.2 G5.2 A5.2 G5.2 | F5.2 E5.2 D5.4 | C5.2 D5.2 E5.2 E5.2 |"
            "F5.2 E5.2 D5.2 C5.2 | B4.4 " + TURCA_PICKUP,
            "C F G C G Am Dm E",
        ),
        "M": (
            "C#5.2 D5.2 E5.2 E5.2 | F#5.2 E5.2 D5.2 C#5.2 |"
            "B4.2 C#5.2 D5.2 D5.2 | E5.2 D5.2 C#5.2 B4.2 |"
            "A4.2 B4.2 C#5.2 C#5.2 | D5.2 C#5.2 B4.2 A4.2 |"
            "G#4.4 E4.4 | A4.4 r.4",
            "A D E E A D E A",
        ),
        "coda": ("C#6.2 A5.2 E5.2 C#5.2 | A4.8", "A A"),
    },
    "form": ["intro", "A", "A", "B", "A", "M", "M", "A_end", "coda"],
}

# ---------------------------------------------------------------------------
# Scott Joplin - The Entertainer, 1902
# ---------------------------------------------------------------------------
ENT_A1 = ("E5.1 C6.2 E5.1 C6.2 E5.1 C6.5 C6.1 D6.1 D#6.1 E6.1 "
          "C6.1 D6.1 E6.2 B5.1 D6.2 C6.5 r.2 D5.1 D#5.1")
ENT_A2 = ("E5.1 C6.2 E5.1 C6.2 E5.1 C6.5 A5.1 G5.1 F#5.1 A5.1 "
          "C6.1 E6.2 D6.1 C6.1 A5.1 D6.6 r.2 D5.1 D#5.1")
ENT_END = ("C6.1 D6.1 E6.1 C6.1 D6.1 E6.2 C6.1 | D6.1 C6.1 E6.1 C6.1 D6.1 E6.2 C6.1 |"
           "D6.1 C6.1 E6.1 C6.1 D6.1 E6.2 B5.1 | D6.2 C6.6")

ENTERTAINER = {
    "id": "entertainer",
    "title": "The Entertainer",
    "composer": "Scott Joplin",
    "year": 1902,
    "bpm": 84,
    "bass": "stride",
    "drums": "rag",
    "lead": 0.25,
    "sections": {
        "intro": ("r.6 D5.1 D#5.1", "G7"),
        "A1": (ENT_A1, "C C G7 C"),
        "A2": (ENT_A2, "C D7 D7 G7"),
        "END": (ENT_END, "C C7 G7 C"),
        "turn": ("r.6 D5.1 D#5.1", "G7"),
    },
    "form": ["intro", "A1", "A2", "A1", "END", "turn", "A1", "A2", "A1", "END"],
}

# ---------------------------------------------------------------------------
# Jacques Offenbach - Galop infernal ("Can-can"), Orphee aux enfers, 1858
# ---------------------------------------------------------------------------
CAN_1 = ("C5.8 | D5.2 F5.2 E5.2 D5.2 | G5.4 G5.4 | G5.2 A5.2 E5.2 F5.2 |"
         "D5.4 D5.4 | D5.2 F5.2 E5.2 D5.2 | C5.2 C6.2 B5.2 A5.2 | G5.2 F5.2 E5.2 D5.2")
CAN_2 = ("C5.8 | D5.2 F5.2 E5.2 D5.2 | G5.4 G5.4 | G5.2 A5.2 E5.2 F5.2 |"
         "D5.4 D5.4 | D5.2 F5.2 E5.2 D5.2 | C5.4 G4.4 | C5.4 r.4")


def octave_up(seq):
    out = []
    for tok in seq.split():
        if tok == "|" or tok.startswith("r."):
            out.append(tok)
            continue
        name, length = tok.split(".")
        out.append("%s%d.%s" % (name[:-1], int(name[-1]) + 1, length))
    return " ".join(out)


CANCAN = {
    "id": "cancan",
    "title": "Galop Infernal (Can-can)",
    "composer": "J. Offenbach",
    "year": 1858,
    "bpm": 150,
    "bass": "oompah",
    "drums": "galop",
    "lead": 0.22,
    "sections": {
        "intro": ("r.8 | r.8", "G7 G7"),
        "T1": (CAN_1, "C G7 C C G G7 C G7"),
        "T2": (CAN_2, "C G7 C C G G7 C C"),
        "H1": (octave_up(CAN_1), "C G7 C C G G7 C G7"),
        "H2": (octave_up(CAN_2), "C G7 C C G G7 C C"),
    },
    "form": ["intro", "T1", "T2", "H1", "H2", "T1", "T2"],
}

SONGS = [TURCA, ENTERTAINER, CANCAN]
