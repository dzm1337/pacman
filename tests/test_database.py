import sqlite3
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from src.config import Config
from src.database import CREATE_TABLE, Database
from src.draw import Draw
from src.game import Game
from src.render import Render


def use(db: Database) -> list[Any]:
    """
    Every database operation of the game, in the order a save does them
    """
    db.initialize_database()
    return [
        db.insert_player("BOB", 10),
        db.check_score_player("BOB"),
        db.update_score("BOB", 20),
        db.top_scores(),
    ]


def create_table(path: Path, sql: str = CREATE_TABLE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as con:
        con.execute(sql)
    con.close()


def test_save_and_read(db_path: Path) -> None:
    assert use(Database()) == [1, [(10,)], 1, [("BOB", 20)]]


def test_creates_missing_folder(db_path: Path) -> None:
    Database().initialize_database()
    assert db_path.is_file()


@pytest.mark.parametrize(
    "damage",
    [
        lambda p: p.parent.write_text("not a folder"),
        lambda p: p.mkdir(parents=True),
        lambda p: (
            p.parent.mkdir(),
            p.write_bytes(b"not a database" * 100),
        ),
        lambda p: create_table(p, "CREATE TABLE highscore(x)"),
    ],
    ids=["db_folder_is_file", "db_is_folder", "garbage_file", "wrong_table"],
)
def test_broken_database(
    damage: Callable[[Path], Any],
    db_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    damage(db_path)
    assert use(Database()) == [0, [], 0, []]
    assert "Warning: cannot" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("target", "mode"),
    [("folder", 0o500), ("file", 0o444), ("file", 0o000)],
    ids=["folder_read_only", "file_read_only", "file_no_permission"],
)
def test_no_permission(
    target: str,
    mode: int,
    db_path: Path,
    chmod: Callable[[Path, int], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    create_table(db_path)
    chmod(db_path.parent if target == "folder" else db_path, mode)
    result = use(Database())
    assert result[0] == 0 and result[2] == 0
    assert "Warning: cannot" in capsys.readouterr().err


def test_locked(db_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    create_table(db_path)
    lock = sqlite3.connect(db_path, isolation_level=None)
    lock.execute("BEGIN EXCLUSIVE")
    # Don't wait the default 5 seconds for the lock
    connect = sqlite3.connect

    def connect_now(path: Path) -> sqlite3.Connection:
        return connect(path, timeout=0)

    monkeypatch.setattr(sqlite3, "connect", connect_now)
    try:
        assert use(Database()) == [0, [], 0, []]
    finally:
        lock.close()


def test_warns_once(
    db_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    db_path.mkdir(parents=True)
    db = Database()
    for _ in range(3):
        db.top_scores()
    assert capsys.readouterr().err.count("cannot read the highscores") == 1


@pytest.mark.parametrize("saved", [None, "abc", b"\x00", 1.5])
def test_save_over_score_that_is_not_a_number(
    saved: Any,
    db_path: Path,
    make_config: Callable[[Any], Config],
) -> None:
    create_table(db_path)
    with sqlite3.connect(db_path) as con:
        con.execute("INSERT INTO highscore VALUES ('BOB', ?)", (saved,))
    con.close()
    game = Game(make_config({}))
    game.score = 100
    render = Render(Draw(game), game)
    render.name = "BOB"
    render._save_score()
    assert game.db.check_score_player("BOB") == [(100,)]
