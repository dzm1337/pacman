import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from pygame import Surface

from src.config import Config
from src.draw import Draw
from src.game import Game
from src.render import Render


@pytest.fixture
def game(make_config: Callable[[Any], Config]) -> Game:
    return Game(make_config({}))


def edit_font_meta(
    assets: Path, change: Callable[[dict[str, Any]], None]
) -> None:
    path = assets / "fonts" / "pacman.json"
    meta = json.loads(path.read_text(encoding="utf-8"))
    change(meta)
    path.write_text(json.dumps(meta), encoding="utf-8")


def load_error(game: Game, capsys: pytest.CaptureFixture[str]) -> str:
    """
    Start the game, which must stop while loading the assets, and return
    the error printed
    """
    with pytest.raises(SystemExit) as exit_info:
        Render(Draw(game), game).display()
    assert exit_info.value.code == 1
    err = capsys.readouterr().err
    assert "Traceback" not in err
    return err


def test_assets_load(assets: Path, game: Game, screen: Surface) -> None:
    Draw(game).load_assets()


def test_runs_from_another_folder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    game: Game,
    screen: Surface,
) -> None:
    # Real assets, found from the project folder, not the current one
    monkeypatch.chdir(tmp_path)
    Draw(game).load_assets()


def break_missing_folder(assets: Path) -> None:
    for file in sorted(assets.rglob("*"), reverse=True):
        file.unlink() if file.is_file() else file.rmdir()
    assets.rmdir()


@pytest.mark.parametrize(
    ("damage", "message"),
    [
        (break_missing_folder, "No such file"),
        (lambda a: (a / "game" / "pacgum.png").unlink(), "No such file"),
        (lambda a: (a / "menu" / "pacman.png").unlink(), "No such file"),
        (lambda a: (a / "fonts" / "pacman_24.png").unlink(), "No such file"),
        (lambda a: (a / "fonts" / "pacman.json").unlink(), "No such file"),
        (
            lambda a: (a / "game" / "pacgum.png").write_text("junk"),
            "pacgum.png is not a valid image",
        ),
        (
            lambda a: (a / "fonts" / "pacman_8.png").write_text("junk"),
            "pacman_8.png is not a valid image",
        ),
        (
            lambda a: (
                (a / "game" / "pacgum.png").unlink(),
                (a / "game" / "pacgum.png").mkdir(),
            ),
            "Is a directory",
        ),
        (
            lambda a: (a / "fonts" / "pacman.json").write_text("{"),
            "pacman.json is not valid JSON",
        ),
        (
            lambda a: (a / "fonts" / "pacman.json").write_bytes(b"\xff"),
            "pacman.json is not valid JSON",
        ),
        (
            lambda a: (a / "fonts" / "pacman.json").write_text("[]"),
            "must contain a JSON object",
        ),
        (
            lambda a: (a / "fonts" / "pacman.json").write_text("{}"),
            "size 64: missing or not an object",
        ),
        (
            lambda a: edit_font_meta(a, lambda m: m.pop("8")),
            "size 8: missing or not an object",
        ),
        (
            lambda a: edit_font_meta(a, lambda m: m["24"].pop("height")),
            "height must be a positive integer",
        ),
        (
            lambda a: edit_font_meta(
                a, lambda m: m["24"].update(image_height=9999)
            ),
            "image_height is taller than the sheet",
        ),
        (
            lambda a: edit_font_meta(a, lambda m: m["24"]["glyphs"].clear()),
            "glyphs must be an object with '?'",
        ),
        (
            lambda a: edit_font_meta(
                a, lambda m: m["24"]["glyphs"].update(A=[99999, 5])
            ),
            "glyph 'A' is outside the sheet",
        ),
        (
            lambda a: edit_font_meta(
                a, lambda m: m["24"]["glyphs"].update(A="x")
            ),
            "glyph 'A' is outside the sheet",
        ),
    ],
    ids=[
        "no_assets_folder",
        "missing_sprite",
        "missing_menu_sprite",
        "missing_font_sheet",
        "missing_font_meta",
        "corrupt_sprite",
        "corrupt_font_sheet",
        "sprite_is_folder",
        "font_meta_invalid_json",
        "font_meta_not_utf8",
        "font_meta_array",
        "font_meta_empty",
        "font_meta_missing_size",
        "font_meta_missing_height",
        "font_meta_image_too_tall",
        "font_meta_no_question_mark",
        "font_meta_glyph_outside",
        "font_meta_glyph_not_a_box",
    ],
)
def test_broken_assets(
    damage: Callable[[Path], Any],
    message: str,
    assets: Path,
    game: Game,
    capsys: pytest.CaptureFixture[str],
) -> None:
    damage(assets)
    err = load_error(game, capsys)
    assert "cannot load the assets" in err and message in err


@pytest.mark.parametrize(
    "file",
    ["game/pacgum.png", "fonts/pacman.json", "fonts/pacman_16.png", "game"],
)
def test_no_permission(
    file: str,
    assets: Path,
    game: Game,
    chmod: Callable[[Path, int], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    chmod(assets / file, 0o000)
    assert "Permission denied" in load_error(game, capsys)
