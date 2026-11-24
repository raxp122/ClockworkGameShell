# -*- coding: utf-8 -*-
"""
KeyTester - shows every key/joystick event the GameShell sends.

Made for the ClockworkPi GameShell (320x240). Works with Python 2 (stock
Clockwork OS) and Python 3 + pygame on a PC.

Hold MENU (Esc) for 1.5 seconds to quit.
"""
from __future__ import print_function, division

import os
import sys

import pygame

W, H = 320, 240
EXIT_HOLD_MS = 1500
LOG_FILE = "keylog.txt"

# Colours
BG = (24, 26, 33)
PANEL = (38, 41, 52)
LINE = (60, 64, 80)
TEXT = (220, 222, 230)
DIM = (120, 125, 140)
ACCENT = (255, 196, 0)
HOT = (255, 92, 92)
GOOD = (90, 220, 140)

# Known GameShell mapping (from clockworkpi/launcher sys.py/UI/keys_def.py).
# A/B/X/Y depend on the "snes"/"xbox" layout chosen in Settings, so both
# letters are shown for those buttons.
KNOWN = {
    pygame.K_UP: "Up",
    pygame.K_DOWN: "Down",
    pygame.K_LEFT: "Left",
    pygame.K_RIGHT: "Right",
    pygame.K_ESCAPE: "Menu",
    pygame.K_SPACE: "Select",
    pygame.K_RETURN: "Start",
    pygame.K_u: "X/Y (U)",
    pygame.K_i: "Y/X (I)",
    pygame.K_j: "B/A (J)",
    pygame.K_k: "A/B (K)",
    pygame.K_h: "LK1",
    pygame.K_l: "LK5",
}

# On-screen button widgets: name -> (rect, keys that light it)
BUTTONS = [
    # Lightkey bar (back side). Only LK1/LK5 are documented; the middle
    # three light up with whatever key they send (see "learned" below).
    ("LK1", (8, 30, 56, 18), [pygame.K_h]),
    ("LK2", (70, 30, 56, 18), []),
    ("LK3", (132, 30, 56, 18), []),
    ("LK4", (194, 30, 56, 18), []),
    ("LK5", (256, 30, 56, 18), [pygame.K_l]),
    # D-pad
    ("^", (40, 62, 22, 22), [pygame.K_UP]),
    ("v", (40, 106, 22, 22), [pygame.K_DOWN]),
    ("<", (18, 84, 22, 22), [pygame.K_LEFT]),
    (">", (62, 84, 22, 22), [pygame.K_RIGHT]),
    # Face buttons, SNES diamond: X(I) top, Y(U) left, A(K) right, B(J) bottom
    ("I", (240, 62, 22, 22), [pygame.K_i]),
    ("K", (262, 84, 22, 22), [pygame.K_k]),
    ("U", (218, 84, 22, 22), [pygame.K_u]),
    ("J", (240, 106, 22, 22), [pygame.K_j]),
    # Middle row
    ("MENU", (100, 66, 52, 16), [pygame.K_ESCAPE]),
    ("SHIFT", (160, 66, 52, 16), [pygame.K_LSHIFT, pygame.K_RSHIFT]),
    ("SELECT", (100, 104, 52, 16), [pygame.K_SPACE]),
    ("START", (160, 104, 52, 16), [pygame.K_RETURN]),
]


def key_label(key):
    name = pygame.key.name(key)
    return name if name else "?"


class App(object):
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 16)
        self.big = pygame.font.Font(None, 22)
        self.down = set()           # currently held keys
        self.log = []               # recent events (text, colour)
        self.lk_learned = {}        # "LK2" -> key code, assigned on the fly
        self.menu_down_at = None
        self.joy_buttons = set()
        self.joys = []
        self.running = True
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            j = pygame.joystick.Joystick(i)
            j.init()
            self.joys.append(j)
            self.add_log("joystick %d: %s" % (i, j.get_name()), DIM)
        try:
            self.logf = open(LOG_FILE, "a")
        except (IOError, OSError):
            self.logf = None

    # -- events ------------------------------------------------------------
    def add_log(self, text, colour=TEXT):
        self.log.append((text, colour))
        self.log = self.log[-6:]
        if getattr(self, "logf", None):
            self.logf.write(text + "\n")
            self.logf.flush()

    def learn_lightkey(self, key):
        """Unknown keys get assigned to the first free middle Lightkey slot
        so the on-screen bar shows what each back button sends."""
        if key in KNOWN or key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
            return
        if key in self.lk_learned.values():
            return
        for slot in ("LK2", "LK3", "LK4"):
            if slot not in self.lk_learned:
                self.lk_learned[slot] = key
                return

    def handle(self, ev):
        if ev.type == pygame.QUIT:
            self.running = False
        elif ev.type == pygame.KEYDOWN:
            self.down.add(ev.key)
            self.learn_lightkey(ev.key)
            meaning = KNOWN.get(ev.key, "NEW")
            mods = pygame.key.get_mods()
            mod_txt = " +shift" if mods & pygame.KMOD_SHIFT else ""
            self.add_log("DOWN %-8s code=%-4d %s%s" % (
                key_label(ev.key), ev.key, meaning, mod_txt),
                ACCENT if meaning == "NEW" else TEXT)
            if ev.key == pygame.K_ESCAPE:
                self.menu_down_at = pygame.time.get_ticks()
        elif ev.type == pygame.KEYUP:
            self.down.discard(ev.key)
            if ev.key == pygame.K_ESCAPE:
                self.menu_down_at = None
        elif ev.type == pygame.JOYBUTTONDOWN:
            self.joy_buttons.add(ev.button)
            self.add_log("JOY button %d down" % ev.button, GOOD)
        elif ev.type == pygame.JOYBUTTONUP:
            self.joy_buttons.discard(ev.button)
        elif ev.type == pygame.JOYAXISMOTION and abs(ev.value) > 0.5:
            self.add_log("JOY axis %d = %.1f" % (ev.axis, ev.value), GOOD)
        elif ev.type == pygame.JOYHATMOTION:
            self.add_log("JOY hat %d = %s" % (ev.hat, ev.value), GOOD)

    def update(self):
        if self.menu_down_at is not None:
            if pygame.time.get_ticks() - self.menu_down_at >= EXIT_HOLD_MS:
                self.running = False

    # -- drawing -----------------------------------------------------------
    def text(self, s, pos, colour=TEXT, font=None, center=False):
        surf = (font or self.font).render(s, True, colour)
        r = surf.get_rect()
        if center:
            r.center = pos
        else:
            r.topleft = pos
        self.screen.blit(surf, r)

    def draw_button(self, name, rect, keys):
        if name in self.lk_learned:
            keys = [self.lk_learned[name]]
        lit = any(k in self.down for k in keys)
        r = pygame.Rect(rect)
        pygame.draw.rect(self.screen, HOT if lit else PANEL, r)
        pygame.draw.rect(self.screen, ACCENT if lit else LINE, r, 1)
        label = name
        if name.startswith("LK"):
            label = "%s %s" % (name, key_label(keys[0]) if keys else "?")
        self.text(label, r.center, BG if lit else TEXT, center=True)

    def draw(self):
        s = self.screen
        s.fill(BG)
        self.text("KEY TESTER", (8, 7), ACCENT, self.big)
        self.text("hold MENU to exit", (312 - self.font.size(
            "hold MENU to exit")[0], 10), DIM)

        for name, rect, keys in BUTTONS:
            self.draw_button(name, rect, keys)

        # Exit progress bar while MENU is held
        if self.menu_down_at is not None:
            t = pygame.time.get_ticks() - self.menu_down_at
            w = int(min(1.0, t / float(EXIT_HOLD_MS)) * 304)
            pygame.draw.rect(s, HOT, (8, 134, w, 3))

        # Event log
        pygame.draw.rect(s, PANEL, (8, 140, 304, 92))
        y = 144
        for line, colour in self.log:
            self.text(line, (12, y), colour)
            y += 14
        if not self.log:
            self.text("press any button...", (12, y), DIM)

        pygame.display.flip()


def main():
    os.environ.setdefault("SDL_VIDEO_CENTERED", "1")
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("KeyTester")
    pygame.mouse.set_visible(False)

    app = App(screen)
    clock = pygame.time.Clock()

    shot = os.environ.get("KEYTESTER_SHOT")  # used to render the store shot
    if shot:
        for k in (pygame.K_h, pygame.K_UP, pygame.K_k, pygame.K_y):
            app.handle(pygame.event.Event(pygame.KEYDOWN, key=k, mod=0))
        app.draw()
        pygame.image.save(screen, shot)
        pygame.quit()
        return 0

    while app.running:
        for ev in pygame.event.get():
            app.handle(ev)
        app.update()
        app.draw()
        clock.tick(30)

    if app.logf:
        app.logf.close()
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
