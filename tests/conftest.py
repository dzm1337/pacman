import json
import os
import shutil
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

# No real window or sound card needed: must be set before pygame starts
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402
import pytest  # noqa: E402
from pygame import Surface  # noqa: E402

from src import database, draw, font  # noqa: E402
from src.config import Config  # noqa: E402
from src.definitions import CELL_SIZE, HUD_HEIGHT, ROOT  # noqa: E402
from src.parser import Parser  # noqa: E402

WriteConfig = Callable[[Any], Path]


@pytest.fixture(autouse=True)
def db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Every test uses its own database, never db/leaderboard.db
    """
    path = tmp_path / "db" / "leaderboard.db"
    monkeypatch.setattr(database, "DB_PATH", path)
    return path


@pytest.fixture
def write_config(tmp_path: Path) -> WriteConfig:
    """
    Write a config file and return its path: a str is written as is,
    anything else as JSON
    """

    def write(content: Any) -> Path:
        path = tmp_path / "config.json"
        if isinstance(content, bytes):
            path.write_bytes(content)
        elif isinstance(content, str):
            path.write_text(content, encoding="utf-8")
        else:
            path.write_text(json.dumps(content), encoding="utf-8")
        return path

    return write


@pytest.fixture
def make_config(write_config: WriteConfig) -> Callable[[Any], Config]:
    def make(content: Any) -> Config:
        return Config(**Parser(write_config(content)).parse_config())

    return make


@pytest.fixture
def screen() -> Iterator[Surface]:
    """
    A window as big as the biggest maze, needed to load the sprites
    """
    surface = pygame.display.set_mode(
        (25 * CELL_SIZE, 15 * CELL_SIZE + HUD_HEIGHT)
    )
    yield surface
    pygame.quit()


@pytest.fixture
def assets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    A copy of the assets that a test can break, used instead of the real ones
    """
    root = tmp_path / "project"
    shutil.copytree(ROOT / "assets", root / "assets")
    fonts = root / "assets" / "fonts"
    monkeypatch.setattr(draw, "ROOT", root)
    monkeypatch.setattr(font, "FONT_DIR", fonts)
    monkeypatch.setattr(font, "FONT_META", fonts / "pacman.json")
    return root / "assets"


@pytest.fixture
def chmod() -> Iterator[Callable[[Path, int], None]]:
    """
    Change permissions for one test, restored after it so tmp_path can be
    deleted. Skipped as root, who can read anything
    """
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        pytest.skip("permissions are not enforced for root")
    changed: list[tuple[Path, int]] = []

    def change(path: Path, mode: int) -> None:
        changed.append((path, path.stat().st_mode))
        path.chmod(mode)

    yield change
    for path, mode in reversed(changed):
        path.chmod(mode)
