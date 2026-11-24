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

# ---------------------------------------------------------------------------
# Edvard Grieg - In the Hall of the Mountain King (Peer Gynt), 1876
# The theme comes back faster every time.
# ---------------------------------------------------------------------------
MK_X = ("B4.2 C#5.2 D5.2 E5.2 | F#5.2 D5.2 F#5.4 | F5.2 C#5.2 F5.4 | E5.2 C5.2 E5.4",
        "Bm Bm F# C")
MK_Y = ("B4.2 C#5.2 D5.2 E5.2 | F#5.2 D5.2 F#5.2 B5.2 | A5.2 F#5.2 D5.2 F#5.2 | A5.8",
        "Bm Bm D D")
MK_X5 = ("F#5.2 G#5.2 A#5.2 B5.2 | C#6.2 A#5.2 C#6.4 | D6.2 A#5.2 D6.4 | C#6.2 A#5.2 C#6.4",
         "F# F# D F#")
MK_Y5 = ("F#5.2 G#5.2 A#5.2 B5.2 | C#6.2 A#5.2 C#6.4 | D6.2 A#5.2 D6.4 | C#6.8",
         "F# F# D F#")


def mk_round(n, bpm):
    return dict(("%s%d" % (k, n), v + (bpm,)) for k, v in
                (("X", MK_X), ("Y", MK_Y), ("X5", MK_X5), ("Y5", MK_Y5)))


MK_SECTIONS = {"intro": ("r.8", "Bm", 104), "end": ("B5.4 F#5.4 | B4.8", "Bm Bm", 184)}
for _n, _bpm in enumerate((104, 126, 152, 184)):
    MK_SECTIONS.update(mk_round(_n, _bpm))

MOUNTAIN_KING = {
    "id": "mountainking",
    "title": "Hall of the Mountain King",
    "composer": "Edvard Grieg",
    "year": 1876,
    "bpm": 104,
    "bass": "oompah",
    "drums": "march",
    "lead": 0.25,
    "sections": MK_SECTIONS,
    "form": ["intro"] + ["%s%d" % (k, n) for n in range(4) for k in ("X", "Y", "X5", "Y5")]
            + ["end"],
}

# ---------------------------------------------------------------------------
# Nikolai Rimsky-Korsakov - Flight of the Bumblebee (Tsar Saltan), 1900
# ---------------------------------------------------------------------------
BEE_DOWN = ("E6.1 D#6.1 D6.1 C#6.1 D6.1 C#6.1 C6.1 B5.1 | C6.1 B5.1 A#5.1 A5.1 G#5.1 G5.1 F#5.1 F5.1 |"
            "E5.1 D#5.1 D5.1 C#5.1 D5.1 C#5.1 C5.1 B4.1 | C5.1 B4.1 A#4.1 A4.1 G#4.1 G4.1 F#4.1 F4.1",
            "E7 E7 E7 E7")
BEE_BUZZ = ("E5.1 D#5.1 D5.1 C#5.1 C5.1 F5.1 E5.1 D#5.1 | E5.1 D#5.1 D5.1 C#5.1 C5.1 C#5.1 D5.1 D#5.1 |"
            "E5.1 D#5.1 D5.1 C#5.1 C5.1 F5.1 E5.1 D#5.1 | E5.1 D#5.1 D5.1 C#5.1 C5.1 C#5.1 D5.1 D#5.1",
            "Am E7 Am E7")
BEE_UP = ("A5.1 G#5.1 G5.1 F#5.1 F5.1 A#5.1 A5.1 G#5.1 | A5.1 G#5.1 G5.1 F#5.1 F5.1 F#5.1 G5.1 G#5.1 |"
          "A5.1 G#5.1 G5.1 F#5.1 F5.1 A#5.1 A5.1 G#5.1 | A5.1 G#5.1 G5.1 F#5.1 F5.1 F#5.1 G5.1 G#5.1",
          "Dm A7 Dm A7")

BUMBLEBEE = {
    "id": "bumblebee",
    "title": "Flight of the Bumblebee",
    "composer": "N. Rimsky-Korsakov",
    "year": 1900,
    "bpm": 132,
    "bass": "oompah",
    "drums": "galop",
    "lead": 0.22,
    "sections": {
        "intro": ("r.8", "E7"),
        "D": BEE_DOWN, "B": BEE_BUZZ, "U": BEE_UP,
        "end": ("A5.4 r.4 | A4.4 r.4", "Am Am"),
    },
    "form": ["intro", "D", "B", "B", "U", "U", "B", "B", "D", "D", "end"],
}

# ---------------------------------------------------------------------------
# Gioachino Rossini - William Tell Overture, finale, 1829
# ---------------------------------------------------------------------------
TELL_A = ("G4.1 G4.1 G4.2 G4.1 G4.1 G4.2 | G4.1 G4.1 C5.2 D5.2 E5.2 |"
          "G4.1 G4.1 G4.2 G4.1 G4.1 G4.2 | G4.1 G4.1 B4.2 C5.2 D5.2 |"
          "G4.1 G4.1 G4.2 G4.1 G4.1 G4.2 | G4.1 G4.1 C5.2 D5.2 E5.2 |"
          "C5.1 C5.1 E5.2 D5.1 D5.1 B4.2 | C5.4 r.4")
TELL_BRIDGE = ("C5.1 C5.1 C5.2 E5.1 E5.1 E5.2 | G5.1 G5.1 G5.2 E5.1 E5.1 E5.2 |"
               "C5.1 C5.1 C5.2 E5.1 E5.1 E5.2 | D5.8")

WILLIAM_TELL = {
    "id": "williamtell",
    "title": "William Tell Overture",
    "composer": "G. Rossini",
    "year": 1829,
    "bpm": 152,
    "bass": "oompah",
    "drums": "galop",
    "lead": 0.25,
    "sections": {
        "intro": ("r.8", "G7"),
        "A": (TELL_A, "C C C G C C G7 C"),
        "AH": (octave_up(TELL_A), "C C C G C C G7 C"),
        "B": (TELL_BRIDGE, "C C C G"),
        "end": ("C6.2 G5.2 E5.2 G5.2 | C5.8", "C C"),
    },
    "form": ["intro", "A", "A", "B", "AH", "AH", "B", "A", "end"],
}

# ---------------------------------------------------------------------------
# Ludwig van Beethoven - Fur Elise (Bagatelle WoO 59), about 1810. In 3/8.
# ---------------------------------------------------------------------------
ELISE_A = ("E5.1 D#5.1 E5.1 B4.1 D5.1 C5.1 | A4.2 r.1 C4.1 E4.1 A4.1 |"
           "B4.2 r.1 E4.1 G#4.1 B4.1 | C5.2 r.1 E4.1 E5.1 D#5.1 |"
           "E5.1 D#5.1 E5.1 B4.1 D5.1 C5.1 | A4.2 r.1 C4.1 E4.1 A4.1 |"
           "B4.2 r.1 E4.1 C5.1 B4.1 | ")
ELISE_CHORDS = "Am Am E Am Am Am E Am"

FUR_ELISE = {
    "id": "furelise",
    "title": "Fur Elise",
    "composer": "L. van Beethoven",
    "year": 1810,
    "bpm": 72,
    "bar": 6,
    "bass": "root",
    "drums": "none",
    "lead": 0.25,
    "sections": {
        "intro": ("r.4 E5.1 D#5.1", "Am"),
        "A": (ELISE_A + "A4.2 r.2 E5.1 D#5.1", ELISE_CHORDS),
        "A2": (ELISE_A + "A4.2 r.1 B4.1 C5.1 D5.1", ELISE_CHORDS),
        "B": ("E5.3 G4.1 F5.1 E5.1 | D5.3 F4.1 E5.1 D5.1 | C5.3 E4.1 D5.1 C5.1 |"
              "B4.2 r.1 E4.1 E5.1 D#5.1", "C G Am E"),
        "end": (ELISE_A + "A4.6", ELISE_CHORDS),
    },
    "form": ["intro", "A", "A2", "B", "A", "A2", "B", "end"],
}

SONGS = [FUR_ELISE, TURCA, ENTERTAINER, WILLIAM_TELL, CANCAN, MOUNTAIN_KING, BUMBLEBEE]
