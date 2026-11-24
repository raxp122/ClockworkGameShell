#!/usr/bin/env python3
"""
Build the GameShell warehouse: packages every game and regenerates all
index.json files, in the same layout as github.com/clockworkpi/warehouse.

Layout:
    <Category>/<Title>/.game            type: launcher | pico8 | tic80
    <Category>/<Title>/src/             sources (launcher type only)
    <Category>/<Title>/file/<file>      built package / cart
    <Category>/<Title>/shots/<img>.png  preview shown in the Warehouse

For "launcher" games src/ must contain <Title>.sh; it gets packed as
file/<Title>.tar.gz with a top folder named <Title>/ (the launcher runs
<Title>/<Title>.sh from there). For pico8/tic80, put the .p8.png / .tic
cart directly in file/.

Usage:  python3 scripts/build.py
"""
import gzip
import io
import json
import os
import sys
import tarfile
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OWNER_REPO = "raxp122/ClockworkGameShell"
# The GameShell launcher hard-codes the "master" branch when it reads a
# warehouse (21_Warehouse/__init__.py -> raw_github_com), so all URLs use it.
BRANCH = "master"
RAW = "https://raw.githubusercontent.com/%s/%s/" % (OWNER_REPO, BRANCH)
TYPES = ("launcher", "pico8", "tic80")
SKIP_DIRS = {".git", ".github", "scripts"}
# Characters that break the launcher (it builds SQL and shell strings).
BAD_CHARS = set("'\"`$\\;&|<>")


def url(*parts):
    return RAW + "/".join(quote(p) for p in parts)


def fail(msg):
    print("ERROR: " + msg)
    sys.exit(1)


def pack(src_dir, title, out_path):
    """Deterministic tar.gz with top folder <title>/ (no mtimes/owners)."""
    def reset(ti):
        ti.uid = ti.gid = 1000
        ti.uname = ti.gname = "cpi"
        ti.mtime = 0
        if ti.isdir() or ti.name.endswith(".sh") or os.access(
                os.path.join(src_dir, os.path.relpath(ti.name, title)), os.X_OK):
            ti.mode = 0o755
        else:
            ti.mode = 0o644
        return ti

    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w", format=tarfile.GNU_FORMAT) as tar:
        tar.add(src_dir, arcname=title, recursive=False, filter=reset)
        for dirpath, dirnames, filenames in os.walk(src_dir):
            dirnames[:] = sorted(d for d in dirnames
                                 if d != "__pycache__" and not d.startswith("."))
            for name in sorted(dirnames) + sorted(filenames):
                if name.startswith("._") or name in (".DS_Store", "keylog.txt", "settings.json", "scores.json") \
                        or name.endswith(".pyc"):
                    continue
                full = os.path.join(dirpath, name)
                arc = os.path.join(title, os.path.relpath(full, src_dir))
                tar.add(full, arcname=arc, recursive=False, filter=reset)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as gz:
            gz.write(buf.getvalue())


def build_game(cat, title):
    gdir = os.path.join(ROOT, cat, title)
    if BAD_CHARS & set(title):
        fail("%s/%s: title contains forbidden characters %s" % (cat, title, BAD_CHARS))
    with open(os.path.join(gdir, ".game")) as f:
        gtype = f.read().strip()
    if gtype not in TYPES:
        fail("%s/%s: unknown type %r in .game" % (cat, title, gtype))

    if gtype == "launcher":
        src = os.path.join(gdir, "src")
        if not os.path.isfile(os.path.join(src, title + ".sh")):
            fail("%s/%s: missing src/%s.sh" % (cat, title, title))
        fname = title + ".tar.gz"
        pack(src, title, os.path.join(gdir, "file", fname))
    else:
        ext = ".p8.png" if gtype == "pico8" else ".tic"
        fdir = os.path.join(gdir, "file")
        carts = sorted(f for f in os.listdir(fdir) if f.endswith(ext)) \
            if os.path.isdir(fdir) else []
        if len(carts) != 1:
            fail("%s/%s: file/ must contain exactly one *%s" % (cat, title, ext))
        fname = carts[0]

    entry = {"type": gtype, "title": title, "file": url(cat, title, "file", fname)}
    sdir = os.path.join(gdir, "shots")
    shots = sorted(f for f in os.listdir(sdir) if f.lower().endswith(".png")) \
        if os.path.isdir(sdir) else []
    if shots:
        entry["shots"] = url(cat, title, "shots", shots[0])
    else:
        print("warning: %s/%s has no screenshot in shots/" % (cat, title))
    return entry


def write_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


def main():
    categories = []
    for cat in sorted(os.listdir(ROOT)):
        cdir = os.path.join(ROOT, cat)
        if cat in SKIP_DIRS or cat.startswith(".") or not os.path.isdir(cdir):
            continue
        games = sorted(g for g in os.listdir(cdir)
                       if os.path.isfile(os.path.join(cdir, g, ".game")))
        if not games:
            continue
        if BAD_CHARS & set(cat):
            fail("category %r contains forbidden characters" % cat)
        entries = [build_game(cat, g) for g in games]
        write_json(os.path.join(cdir, "index.json"), {"list": entries})
        categories.append({"title": cat, "file": url(cat, "index.json"), "type": "dir"})
        print("%-12s %d game(s): %s" % (cat, len(entries), ", ".join(games)))
    write_json(os.path.join(ROOT, "index.json"), {"list": categories})
    print("index.json  %d categor%s" % (len(categories), "y" if len(categories) == 1 else "ies"))


if __name__ == "__main__":
    main()
