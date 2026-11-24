# -*- coding: utf-8 -*-
"""
LightBeat - a 4-lane rhythm game for the ClockworkPi GameShell (320x240).

Play the lanes with the back Lightkey (LK1 LK2 LK4 LK5), the D-pad
(Left Down Up Right) or the face buttons (Y B X A).

Runs on the stock Clockwork OS (Python 2 + pygame 1.9) and on a PC with
Python 3 + pygame 2.
"""
from __future__ import print_function, division

import json
import math
import os
import sys

import pygame

W, H = 320, 240
HERE = os.path.dirname(os.path.abspath(__file__))
SONG_DIR = os.path.join(HERE, "songs")
SETTINGS_FILE = os.path.join(HERE, "settings.json")
SCORES_FILE = os.path.join(HERE, "scores.json")
BUTTONS_LAYOUT_FILE = "/home/cpi/launcher/.buttonslayout"

DIFFS = ["easy", "normal", "hard"]
SPEEDS = [2.2, 1.9, 1.6, 1.35, 1.1]          # seconds a note takes to fall
PERFECT, GOOD, MISS_LATE = 0.055, 0.115, 0.16  # hit windows (seconds)

# Colours
BG = (14, 15, 22)
PANEL = (30, 32, 44)
LINE = (58, 62, 80)
TEXT = (226, 228, 236)
DIM = (120, 126, 146)
GOLD = (255, 200, 40)
RED = (255, 84, 96)
GREEN = (90, 230, 150)
LANE_COL = [(255, 84, 120), (80, 200, 255), (120, 240, 120), (255, 190, 60)]

# Keys -------------------------------------------------------------------
K = pygame
LANE_KEYS = {
    # Lightkey: LK1 LK2 LK4 LK5 (LK3 is a hardware SHIFT, sends nothing)
    K.K_h: 0, K.K_y: 1, K.K_o: 2, K.K_l: 3,
    # D-pad, dance-game style
    K.K_LEFT: 0, K.K_DOWN: 1, K.K_UP: 2, K.K_RIGHT: 3,
    # Face buttons as a diamond: Y(left) B(bottom) X(top) A(right)
    K.K_u: 0, K.K_j: 1, K.K_i: 2, K.K_k: 3,
}


def confirm_back_keys():
    """A/B follow the layout chosen in the GameShell settings."""
    layout = "snes"
    try:
        with open(BUTTONS_LAYOUT_FILE) as f:
            layout = f.read().strip() or "snes"
    except (IOError, OSError):
        pass
    if layout == "xbox":
        return (K.K_j, K.K_RETURN), (K.K_k, K.K_ESCAPE)
    return (K.K_k, K.K_RETURN), (K.K_j, K.K_ESCAPE)


CONFIRM, BACK = confirm_back_keys()


# Persistence ------------------------------------------------------------
def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except (IOError, OSError, ValueError):
        return default


def save_json(path, data):
    try:
        with open(path, "w") as f:
            json.dump(data, f)
    except (IOError, OSError):
        pass


def load_songs():
    songs = []
    for sid in load_json(os.path.join(SONG_DIR, "index.json"), []):
        s = load_json(os.path.join(SONG_DIR, sid + ".json"), None)
        if s:
            songs.append(s)
    return songs


# Clock ------------------------------------------------------------------
class Clock(object):
    """Wall clock in seconds. In test mode it advances one frame per tick."""
    def __init__(self, simulated=False):
        self.simulated = simulated
        self.t = 0.0

    def now(self):
        if self.simulated:
            return self.t
        return pygame.time.get_ticks() / 1000.0

    def advance(self, dt):
        self.t += dt


# Audio ------------------------------------------------------------------
class Audio(object):
    def __init__(self):
        self.ok = True
        try:
            pygame.mixer.init()
        except pygame.error:
            self.ok = False

    def play(self, path):
        if not self.ok:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
        except pygame.error:
            pass

    def stop(self):
        if self.ok:
            pygame.mixer.music.stop()

    def pause(self):
        if self.ok:
            pygame.mixer.music.pause()

    def resume(self):
        if self.ok:
            pygame.mixer.music.unpause()


# Text helper ------------------------------------------------------------
class Fonts(object):
    def __init__(self):
        self.sizes = {}
        self.cache = {}

    def render(self, text, size, colour):
        key = (text, size, colour)
        surf = self.cache.get(key)
        if surf is None:
            if size not in self.sizes:
                self.sizes[size] = pygame.font.Font(None, size)
            surf = self.sizes[size].render(text, True, colour)
            if len(self.cache) > 400:
                self.cache.clear()
            self.cache[key] = surf
        return surf

    def draw(self, screen, text, size, colour, pos, align="left"):
        surf = self.render(text, size, colour)
        r = surf.get_rect()
        if align == "center":
            r.midtop = pos
        elif align == "right":
            r.topright = pos
        else:
            r.topleft = pos
        screen.blit(surf, r)
        return r


def grade_for(acc):
    for g, need in (("S", 0.95), ("A", 0.90), ("B", 0.80), ("C", 0.70)):
        if acc >= need:
            return g
    return "D"


# Scenes -----------------------------------------------------------------
class Scene(object):
    def __init__(self, game):
        self.game = game

    def key(self, key):
        pass

    def keyup(self, key):
        pass

    def update(self):
        pass

    def draw(self, s):
        pass


def draw_footer(game, s, text):
    pygame.draw.rect(s, PANEL, (0, H - 16, W, 16))
    game.fonts.draw(s, text, 15, DIM, (W // 2, H - 13), "center")


class Title(Scene):
    ITEMS = ["Play", "Options", "Exit"]

    def __init__(self, game):
        Scene.__init__(self, game)
        self.sel = 0

    def key(self, key):
        if key == K.K_UP:
            self.sel = (self.sel - 1) % len(self.ITEMS)
        elif key == K.K_DOWN:
            self.sel = (self.sel + 1) % len(self.ITEMS)
        elif key in CONFIRM:
            item = self.ITEMS[self.sel]
            if item == "Play":
                self.game.go(SongSelect(self.game))
            elif item == "Options":
                self.game.go(Options(self.game))
            else:
                self.game.running = False
        elif key in BACK:
            self.game.running = False

    def draw(self, s):
        g = self.game
        s.fill(BG)
        t = g.clock.now()
        # Pulsing lane bars
        for i in range(4):
            h = 8 + 26 * (0.5 + 0.5 * math.sin(t * 3.2 + i * 1.3))
            pygame.draw.rect(s, LANE_COL[i], (40 + i * 64, 116 - int(h), 48, int(h)))
        g.fonts.draw(s, "LIGHTBEAT", 52, TEXT, (W // 2, 20), "center")
        g.fonts.draw(s, "a Lightkey rhythm game", 16, DIM, (W // 2, 60), "center")
        for i, item in enumerate(self.ITEMS):
            y = 128 + i * 26
            if i == self.sel:
                pygame.draw.rect(s, PANEL, (100, y - 3, 120, 22))
                pygame.draw.rect(s, GOLD, (100, y - 3, 120, 22), 1)
            g.fonts.draw(s, item, 22, GOLD if i == self.sel else TEXT, (W // 2, y), "center")
        draw_footer(g, s, "Up/Down: choose    A: ok    B: exit")


class SongSelect(Scene):
    def __init__(self, game):
        Scene.__init__(self, game)
        self.sel = game.last_song
        self.diff = game.last_diff

    def key(self, key):
        n = len(self.game.songs)
        if key == K.K_UP:
            self.sel = (self.sel - 1) % n
        elif key == K.K_DOWN:
            self.sel = (self.sel + 1) % n
        elif key == K.K_LEFT:
            self.diff = max(0, self.diff - 1)
        elif key == K.K_RIGHT:
            self.diff = min(len(DIFFS) - 1, self.diff + 1)
        elif key in CONFIRM:
            self.game.last_song, self.game.last_diff = self.sel, self.diff
            self.game.go(Play(self.game, self.game.songs[self.sel], DIFFS[self.diff]))
        elif key in BACK:
            self.game.go(Title(self.game))

    def draw(self, s):
        g = self.game
        s.fill(BG)
        g.fonts.draw(s, "SELECT SONG", 22, GOLD, (8, 6))
        for i, song in enumerate(g.songs):
            y = 30 + i * 34
            on = i == self.sel
            pygame.draw.rect(s, PANEL if on else BG, (6, y, 308, 30))
            if on:
                pygame.draw.rect(s, GOLD, (6, y, 308, 30), 1)
            g.fonts.draw(s, song["title"], 19, TEXT if on else DIM, (12, y + 3))
            g.fonts.draw(s, "%s, %d" % (song["composer"], song["year"]), 15, DIM,
                         (12, y + 17))
            best = g.scores.get("%s/%s" % (song["id"], DIFFS[self.diff]))
            if best:
                g.fonts.draw(s, best["grade"], 26, GOLD, (306, y + 5), "right")

        song = g.songs[self.sel]
        diff = DIFFS[self.diff]
        y = 30 + len(g.songs) * 34 + 6
        pygame.draw.line(s, LINE, (6, y), (314, y))
        # Difficulty selector
        for i, d in enumerate(DIFFS):
            x = 12 + i * 70
            on = i == self.diff
            col = (GREEN, GOLD, RED)[i]
            pygame.draw.rect(s, col if on else PANEL, (x, y + 8, 64, 18))
            g.fonts.draw(s, d.upper(), 16, BG if on else DIM, (x + 32, y + 11), "center")
        n_notes = len(song["charts"][diff])
        g.fonts.draw(s, "%d notes" % n_notes, 16, TEXT, (306, y + 6), "right")
        g.fonts.draw(s, "%d BPM  %ds" % (song["bpm"], int(song["length"])), 15, DIM,
                     (306, y + 19), "right")
        best = g.scores.get("%s/%s" % (song["id"], diff))
        if best:
            g.fonts.draw(s, "Best: %d  (%d%%)%s" % (
                best["score"], int(best["acc"] * 100), "  FC" if best.get("fc") else ""),
                16, TEXT, (12, y + 32))
        else:
            g.fonts.draw(s, "Not played yet", 16, DIM, (12, y + 32))
        draw_footer(g, s, "Up/Down: song   Left/Right: level   A: play")


class Options(Scene):
    def __init__(self, game):
        Scene.__init__(self, game)
        self.sel = 0

    def key(self, key):
        st = self.game.settings
        if key == K.K_UP or key == K.K_DOWN:
            self.sel = 1 - self.sel
        elif key in (K.K_LEFT, K.K_RIGHT):
            d = -1 if key == K.K_LEFT else 1
            if self.sel == 0:
                st["offset_ms"] = max(-300, min(300, st["offset_ms"] + 10 * d))
            else:
                st["speed"] = max(0, min(len(SPEEDS) - 1, st["speed"] + d))
        elif key in BACK or key in CONFIRM:
            save_json(SETTINGS_FILE, st)
            self.game.go(Title(self.game))

    def draw(self, s):
        g = self.game
        st = g.settings
        s.fill(BG)
        g.fonts.draw(s, "OPTIONS", 22, GOLD, (8, 6))
        rows = [("Audio offset", "%+d ms" % st["offset_ms"]),
                ("Note speed", "%d" % (st["speed"] + 1))]
        for i, (name, val) in enumerate(rows):
            y = 44 + i * 34
            on = i == self.sel
            pygame.draw.rect(s, PANEL if on else BG, (10, y, 300, 26))
            if on:
                pygame.draw.rect(s, GOLD, (10, y, 300, 26), 1)
            g.fonts.draw(s, name, 20, TEXT, (18, y + 5))
            g.fonts.draw(s, "<  %s  >" % val, 20, GOLD if on else TEXT, (300, y + 5), "right")
        tips = ["Hits often marked 'late'? Raise the offset.",
                "Often marked 'early'? Lower it.",
                "Note speed: 1 = slow ... 5 = fast."]
        for i, line in enumerate(tips):
            g.fonts.draw(s, line, 16, DIM, (18, 130 + i * 16))
        draw_footer(g, s, "Left/Right: change    B: save and back")


class Play(Scene):
    def __init__(self, game, song, diff):
        Scene.__init__(self, game)
        self.song, self.diff = song, diff
        self.notes = [[t, lane, None] for t, lane in song["charts"][diff]]  # state
        self.fall = SPEEDS[game.settings["speed"]]
        self.offset = game.settings["offset_ms"] / 1000.0
        self.lane_x = [16 + i * 44 for i in range(4)]
        self.hit_y = 204
        self.held = [False] * 4
        self.flash = [0.0] * 4
        self.score = self.combo = self.max_combo = 0
        self.counts = {"perfect": 0, "good": 0, "miss": 0}
        self.judge = ("", 0.0)
        self.timing = ""                # "early" / "late" for the last GOOD
        self.next_idx = 0               # first note not yet judged
        self.paused = False
        self.pause_sel = 0
        self.ended = False
        self.bg = self.make_bg()
        self.start()

    def make_bg(self):
        bg = pygame.Surface((W, H))
        bg.fill(BG)
        for i, x in enumerate(self.lane_x):
            col = tuple(c // 7 for c in LANE_COL[i])
            pygame.draw.rect(bg, col, (x, 0, 42, H))
            pygame.draw.line(bg, LINE, (x - 1, 0), (x - 1, H))
        pygame.draw.line(bg, LINE, (16 + 4 * 44 - 1, 0), (16 + 4 * 44 - 1, H))
        pygame.draw.rect(bg, PANEL, (200, 0, 120, H))
        return bg

    # timing --------------------------------------------------------------
    def start(self):
        self.t0 = self.last_frame = self.game.clock.now()
        self.pause_t = None
        self.game.audio.play(os.path.join(SONG_DIR, self.song["audio"]))

    def song_time(self):
        now = self.pause_t if self.paused else self.game.clock.now()
        return now - self.t0 - self.offset

    # input ---------------------------------------------------------------
    def key(self, key):
        if self.paused:
            self.pause_key(key)
            return
        if key == K.K_ESCAPE or key == K.K_RETURN:
            self.paused = True
            self.pause_sel = 0
            self.pause_t = self.game.clock.now()
            self.game.audio.pause()
            return
        lane = LANE_KEYS.get(key)
        if lane is not None:
            self.held[lane] = True
            self.hit(lane, self.song_time())

    def keyup(self, key):
        lane = LANE_KEYS.get(key)
        if lane is not None:
            self.held[lane] = False

    def pause_key(self, key):
        if key == K.K_UP or key == K.K_DOWN:
            self.pause_sel = (self.pause_sel + (1 if key == K.K_DOWN else -1)) % 3
        elif key in BACK:
            self.resume()
        elif key in CONFIRM:
            if self.pause_sel == 0:
                self.resume()
            elif self.pause_sel == 1:
                self.game.go(Play(self.game, self.song, self.diff))
            else:
                self.game.audio.stop()
                self.game.go(SongSelect(self.game))

    def resume(self):
        self.t0 += self.game.clock.now() - self.pause_t
        self.paused = False
        self.last_frame = self.game.clock.now()
        self.game.audio.resume()

    def hit(self, lane, t):
        best, best_dt = None, None
        for n in self.notes[self.next_idx:]:
            if n[0] - t > GOOD:
                break
            if n[1] != lane or n[2] is not None:
                continue
            dt = abs(n[0] - t)
            if dt <= GOOD and (best is None or dt < best_dt):
                best, best_dt = n, dt
        if best is None:
            return  # pressing with no note nearby is not punished
        self.flash[lane] = 0.15
        result = "perfect" if best_dt <= PERFECT else "good"
        self.timing = "" if result == "perfect" else ("late" if t > best[0] else "early")
        self.register(best, result)

    def register(self, note, result):
        note[2] = result
        self.counts[result] += 1
        if result == "miss":
            self.combo = 0
            self.timing = ""
        else:
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            mult = min(4, 1 + self.combo // 10)
            self.score += (300 if result == "perfect" else 100) * mult
        self.judge = (result, 0.45)

    # update --------------------------------------------------------------
    def update(self):
        if self.paused:
            return
        t = self.song_time()
        now = self.game.clock.now()
        dt = min(0.1, now - self.last_frame)
        self.last_frame = now
        self.flash = [max(0.0, f - dt) for f in self.flash]
        self.judge = (self.judge[0], max(0.0, self.judge[1] - dt))

        if self.game.autoplay:
            for n in self.notes[self.next_idx:]:
                if n[0] > t:
                    break
                if n[2] is None:
                    self.flash[n[1]] = 0.15
                    self.register(n, "perfect")

        while self.next_idx < len(self.notes):
            n = self.notes[self.next_idx]
            if n[2] is None and t - n[0] > MISS_LATE:
                self.register(n, "miss")
            if n[2] is None:
                break
            self.next_idx += 1

        if not self.ended and self.next_idx >= len(self.notes) and t > self.song["length"] - 1.0:
            self.ended = True
            self.game.audio.stop()
            self.game.go(Results(self.game, self))

    # draw ----------------------------------------------------------------
    def draw(self, s):
        g = self.game
        s.blit(self.bg, (0, 0))
        t = self.song_time()
        pix_per_s = (self.hit_y + 12) / self.fall

        # receptors
        for i, x in enumerate(self.lane_x):
            col = LANE_COL[i]
            lit = self.held[i] or self.flash[i] > 0
            pygame.draw.rect(s, col if lit else LINE, (x + 1, self.hit_y - 4, 40, 9),
                             0 if lit else 2)
            if self.flash[i] > 0:
                r = int(26 - self.flash[i] * 60)
                pygame.draw.circle(s, col, (x + 21, self.hit_y), max(4, r), 2)

        # notes
        for n in self.notes[self.next_idx:]:
            dt = n[0] - t
            if dt > self.fall:
                break
            if n[2] is not None:
                continue
            y = int(self.hit_y - dt * pix_per_s)
            if y > H:
                continue
            x = self.lane_x[n[1]]
            pygame.draw.rect(s, LANE_COL[n[1]], (x + 3, y - 4, 36, 9))
            pygame.draw.rect(s, (255, 255, 255), (x + 3, y - 4, 36, 2))

        # judgement
        name, left = self.judge
        if left > 0 and name:
            col = {"perfect": GOLD, "good": GREEN, "miss": RED}[name]
            y = 120 - int((0.45 - left) * 30)
            g.fonts.draw(s, name.upper(), 26, col, (104, y), "center")
            if self.timing:
                g.fonts.draw(s, self.timing, 16, DIM, (104, y + 20), "center")
        if self.combo >= 5:
            g.fonts.draw(s, "%d" % self.combo, 34, TEXT, (104, 70), "center")

        # side panel
        g.fonts.draw(s, self.song["title"][:16], 16, TEXT, (206, 8))
        g.fonts.draw(s, self.diff.upper(), 15, (GREEN, GOLD, RED)[DIFFS.index(self.diff)],
                     (206, 22))
        g.fonts.draw(s, "SCORE", 14, DIM, (206, 46))
        g.fonts.draw(s, "%07d" % self.score, 24, TEXT, (206, 58))
        g.fonts.draw(s, "COMBO", 14, DIM, (206, 86))
        g.fonts.draw(s, "%d" % self.combo, 24, TEXT, (206, 98))
        g.fonts.draw(s, "x%d" % min(4, 1 + self.combo // 10), 20, GOLD, (312, 100), "right")
        g.fonts.draw(s, "P %d  G %d  M %d" % (
            self.counts["perfect"], self.counts["good"], self.counts["miss"]),
            15, DIM, (206, 128))
        # progress bar
        prog = max(0.0, min(1.0, t / self.song["length"]))
        pygame.draw.rect(s, LINE, (206, 146, 106, 4))
        pygame.draw.rect(s, GOLD, (206, 146, int(106 * prog), 4))
        # key legend
        for i, lbl in enumerate(("LK1", "LK2", "LK4", "LK5")):
            g.fonts.draw(s, lbl, 14, LANE_COL[i], (16 + i * 44 + 21, H - 14), "center")
        g.fonts.draw(s, "MENU: pause", 14, DIM, (206, H - 14))

        if self.paused:
            self.draw_pause(s)

    def draw_pause(self, s):
        g = self.game
        shade = pygame.Surface((W, H))
        shade.set_alpha(170)
        shade.fill((0, 0, 0))
        s.blit(shade, (0, 0))
        g.fonts.draw(s, "PAUSED", 32, GOLD, (W // 2, 50), "center")
        for i, item in enumerate(("Resume", "Restart", "Quit")):
            y = 100 + i * 28
            on = i == self.pause_sel
            if on:
                pygame.draw.rect(s, GOLD, (110, y - 3, 100, 22), 1)
            g.fonts.draw(s, item, 22, GOLD if on else TEXT, (W // 2, y), "center")


class Results(Scene):
    def __init__(self, game, play):
        Scene.__init__(self, game)
        self.song, self.diff = play.song, play.diff
        self.counts = play.counts
        total = max(1, len(play.notes))
        self.acc = (play.counts["perfect"] + 0.5 * play.counts["good"]) / total
        self.grade = grade_for(self.acc)
        self.score = play.score
        self.max_combo = play.max_combo
        self.fc = play.counts["miss"] == 0
        key = "%s/%s" % (self.song["id"], self.diff)
        old = game.scores.get(key)
        self.new_best = old is None or self.score > old["score"]
        if self.new_best:
            game.scores[key] = {"score": self.score, "acc": round(self.acc, 4),
                                "grade": self.grade, "fc": self.fc}
            if not game.clock.simulated:  # the headless test must not save
                save_json(SCORES_FILE, game.scores)

    def key(self, key):
        if key in CONFIRM or key in BACK:
            self.game.go(SongSelect(self.game))
        elif key == K.K_SPACE:
            self.game.go(Play(self.game, self.song, self.diff))

    def draw(self, s):
        g = self.game
        s.fill(BG)
        g.fonts.draw(s, self.song["title"], 20, TEXT, (W // 2, 8), "center")
        g.fonts.draw(s, self.diff.upper(), 16, DIM, (W // 2, 26), "center")
        g.fonts.draw(s, self.grade, 96, GOLD, (76, 50), "center")
        if self.fc:
            g.fonts.draw(s, "FULL COMBO", 18, GREEN, (76, 128), "center")
        rows = [("Score", "%d" % self.score), ("Accuracy", "%.1f%%" % (self.acc * 100)),
                ("Max combo", "%d" % self.max_combo),
                ("Perfect", "%d" % self.counts["perfect"]),
                ("Good", "%d" % self.counts["good"]), ("Miss", "%d" % self.counts["miss"])]
        for i, (k, v) in enumerate(rows):
            y = 52 + i * 20
            g.fonts.draw(s, k, 18, DIM, (160, y))
            g.fonts.draw(s, v, 18, TEXT, (308, y), "right")
        if self.new_best:
            g.fonts.draw(s, "NEW BEST!", 22, RED, (W // 2, 180), "center")
        draw_footer(g, s, "A: continue    SELECT: retry")


# Game -------------------------------------------------------------------
class Game(object):
    def __init__(self, screen, simulated=False):
        self.screen = screen
        self.clock = Clock(simulated)
        self.fonts = Fonts()
        self.audio = Audio()
        self.songs = load_songs()
        self.settings = {"offset_ms": 0, "speed": 2}
        self.settings.update(load_json(SETTINGS_FILE, {}))
        self.scores = load_json(SCORES_FILE, {})
        self.autoplay = bool(os.environ.get("LIGHTBEAT_AUTOPLAY"))
        self.last_song = 0
        self.last_diff = 1
        self.running = True
        self.scene = Title(self)

    def go(self, scene):
        self.scene = scene

    def handle(self, ev):
        if ev.type == pygame.QUIT:
            self.running = False
        elif ev.type == pygame.KEYDOWN:
            self.scene.key(ev.key)
        elif ev.type == pygame.KEYUP:
            self.scene.keyup(ev.key)

    def frame(self):
        self.scene.update()
        self.scene.draw(self.screen)


def press(game, key):
    game.handle(pygame.event.Event(pygame.KEYDOWN, key=key, mod=0))
    game.handle(pygame.event.Event(pygame.KEYUP, key=key, mod=0))


def run_test(screen, shot_prefix):
    """Headless run: plays every song on every difficulty with autoplay and
    saves screenshots. Used to check the game and to make store shots."""
    os.environ["LIGHTBEAT_AUTOPLAY"] = "1"
    game = Game(screen, simulated=True)
    game.scores, game.settings = {}, {"offset_ms": 0, "speed": 2}
    save = lambda name: pygame.image.save(screen, "%s_%s.png" % (shot_prefix, name))  # noqa
    game.frame()
    save("title")
    press(game, CONFIRM[0])
    game.frame()
    save("select")
    for si, song in enumerate(game.songs):
        for diff in DIFFS:
            game.go(Play(game, song, diff))
            shot_at = song["charts"][diff][len(song["charts"][diff]) // 3][0] - 0.05
            took = False
            while isinstance(game.scene, Play):
                game.clock.advance(1.0 / 30)
                game.frame()
                if not took and si == 0 and diff == "normal" \
                        and game.scene.song_time() >= shot_at:
                    save("play")
                    took = True
            res = game.scene
            assert isinstance(res, Results), res
            assert res.counts["miss"] == 0 and res.grade == "S", (song["id"], diff, res.counts)
            print("ok %-12s %-6s notes=%-4d score=%d" % (
                song["id"], diff, len(song["charts"][diff]), res.score))
            if si == 0 and diff == "normal":
                save("results")
    game.go(SongSelect(game))
    game.frame()
    save("select")
    return 0


def main():
    os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    try:
        pygame.mixer.pre_init(44100, -16, 2, 1024)
    except pygame.error:
        pass
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("LightBeat")
    pygame.mouse.set_visible(False)

    shot = os.environ.get("LIGHTBEAT_TEST")
    if shot:
        return run_test(screen, shot)

    game = Game(screen)
    if not game.songs:
        print("No songs found in", SONG_DIR)
        return 1
    tick = pygame.time.Clock()
    while game.running:
        for ev in pygame.event.get():
            game.handle(ev)
        game.frame()
        pygame.display.flip()
        tick.tick(60)
    game.audio.stop()
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
