# PyInstaller spec of the packaged game, built by `make package`.
#
# Output:
#   dist/pacman/                the game folder: executable, config.json,
#                               README.txt and _internal/ (Python, pygame,
#                               assets)
#   dist/pacman-<platform>.zip  that folder zipped, ready for itch.io
#
# PyInstaller doesn't cross-compile: build on the system the package is for.
import shutil
import sys
from pathlib import Path

a = Analysis(
    ["pac-man.py"],
    pathex=["."],
    # Sprites and bitmap fonts, read from ROOT / "assets" in the game
    datas=[("assets", "assets")],
    # Only used to develop and test
    excludes=["tkinter", "pytest", "mypy", "flake8"],
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="pacman",
    # Keep the terminal: config errors and warnings are printed there
    console=True,
)
coll = COLLECT(exe, a.binaries, a.datas, name="pacman")

# Files the player reads or edits, next to the executable
out = Path(DISTPATH) / "pacman"
shutil.copy("config/config.json", out / "config.json")
shutil.copy("packaging/README.txt", out / "README.txt")

shutil.make_archive(
    str(Path(DISTPATH) / f"pacman-{sys.platform}"),
    "zip",
    root_dir=DISTPATH,
    base_dir="pacman",
)
