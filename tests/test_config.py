from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from src import __main__ as entry
from src.__main__ import parse_args
from src.config import Config
from src.parser import DEFAULT_CFG_PARAMS, Parser

from tests.conftest import WriteConfig


def error_of(path: Path, capsys: pytest.CaptureFixture[str]) -> str:
    """
    Parse a config that must be rejected, and return the error printed
    """
    with pytest.raises(SystemExit) as exit_info:
        Parser(path).parse_config()
    assert exit_info.value.code == 1
    return capsys.readouterr().err


@pytest.mark.parametrize(
    "argv",
    [["pac-man.py"], ["pac-man.py", "a.json", "b.json"]],
)
def test_wrong_number_of_arguments(
    argv: list[str], capsys: pytest.CaptureFixture[str]
) -> None:
    with pytest.raises(SystemExit):
        parse_args(argv)
    assert "expected exactly one argument" in capsys.readouterr().err


def test_not_a_json_file(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        parse_args(["pac-man.py", "README.md"])
    assert "is not a .json file" in capsys.readouterr().err


def test_packaged_game_without_argument(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Double click on the packaged game: config.json next to the executable
    monkeypatch.setattr(entry, "FROZEN", True)
    monkeypatch.setattr(entry, "APP_DIR", tmp_path)
    assert parse_args(["pacman"]) == tmp_path / "config.json"


def test_absolute_path_is_kept(tmp_path: Path) -> None:
    path = tmp_path / "config.json"
    assert parse_args(["pac-man.py", str(path)]) == path


def test_relative_path_from_current_folder(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A config outside the project, given relative to where the game runs
    (tmp_path / "mine").mkdir()
    (tmp_path / "mine" / "my.json").write_text('{"lives": 7}')
    monkeypatch.chdir(tmp_path)
    path = parse_args(["pac-man.py", "mine/my.json"])
    assert Parser(path).parse_config()["lives"] == 7


def test_missing_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    err = error_of(tmp_path / "nope.json", capsys)
    assert "cannot read" in err and "No such file" in err


def test_directory(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "dir.json"
    path.mkdir()
    assert "Is a directory" in error_of(path, capsys)


def test_broken_symlink(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "link.json"
    path.symlink_to(tmp_path / "nowhere.json")
    assert "cannot read" in error_of(path, capsys)


def test_no_read_permission(
    write_config: WriteConfig,
    chmod: Callable[[Path, int], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = write_config({})
    chmod(path, 0o000)
    assert "Permission denied" in error_of(path, capsys)


def test_no_permission_on_folder(
    write_config: WriteConfig,
    chmod: Callable[[Path, int], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    path = write_config({})
    chmod(path.parent, 0o000)
    assert "Permission denied" in error_of(path, capsys)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("", "is empty"),
        ("  \n\n", "is empty"),
        ('{"width": 14,', "is not valid JSON"),
        ("[1, 2]", "must contain a JSON object"),
        ("null", "must contain a JSON object"),
        ('"text"', "must contain a JSON object"),
        (b"\xff\xfe{}", "is not valid UTF-8"),
    ],
    ids=[
        "empty",
        "only_spaces",
        "invalid_json",
        "array",
        "null",
        "string",
        "not_utf8",
    ],
)
def test_rejected_files(
    content: str | bytes,
    message: str,
    write_config: WriteConfig,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert message in error_of(write_config(content), capsys)


@pytest.mark.parametrize("depth", [10_000, 100_000, 1_000_000])
@pytest.mark.parametrize("key", [None, "level", "lives", "unknown"])
def test_deep_nesting_never_crashes(
    depth: int,
    key: str | None,
    write_config: WriteConfig,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    How deep JSON can be parsed depends on the stack Python gets, so the
    file may be read or rejected, but nothing else may be raised
    """
    nested = "[" * depth + "]" * depth
    content = nested if key is None else '{"%s": [%s]}' % (key, nested)
    try:
        Parser(write_config(content)).parse_config()
    except SystemExit:
        err = capsys.readouterr().err
        assert "nested too deeply" in err or "must contain" in err


def test_utf8_bom_is_accepted(write_config: WriteConfig) -> None:
    path = write_config(b'\xef\xbb\xbf{"lives": 5}')
    assert Parser(path).parse_config()["lives"] == 5


def test_comments_are_ignored(write_config: WriteConfig) -> None:
    path = write_config('# a comment\n{"lives": 5}\n')
    assert Parser(path).parse_config()["lives"] == 5


def test_empty_object_uses_defaults(
    make_config: Callable[[Any], Config],
    capsys: pytest.CaptureFixture[str],
) -> None:
    config = make_config({})
    assert config.lives == DEFAULT_CFG_PARAMS["lives"]
    assert config.level == []
    assert "lives is missing" in capsys.readouterr().err


@pytest.mark.parametrize(
    "value",
    ['"3"', "true", "1.5", "-1", "0", "null", "[]", "{}", "NaN", "Infinity",
     "1e400"],
)
def test_invalid_values_use_defaults(
    value: str, write_config: WriteConfig
) -> None:
    path = write_config('{"lives": %s}' % value)
    assert Parser(path).parse_config()["lives"] == DEFAULT_CFG_PARAMS["lives"]


def test_unknown_parameter_is_ignored(
    make_config: Callable[[Any], Config],
    capsys: pytest.CaptureFixture[str],
) -> None:
    make_config({"speed": 3})
    assert "speed is not a known parameter" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("width", "height", "expected"),
    [(1, 1, (12, 12)), (99999, 99999, (25, 15)), (20, 13, (20, 13))],
)
def test_size_is_clamped(
    width: int,
    height: int,
    expected: tuple[int, int],
    make_config: Callable[[Any], Config],
) -> None:
    config = make_config({"width": width, "height": height})
    assert (config.width, config.height) == expected


def test_invalid_levels_use_global_size(
    make_config: Callable[[Any], Config],
) -> None:
    levels = [1, "x", None, [], {"width": -1}, {"height": 1e9}, {"width": 99}]
    config = make_config({"width": 14, "height": 14, "level": levels})
    assert config.level == [{"width": 14, "height": 14}] * 6 + [
        {"width": 25, "height": 14}
    ]


def test_level_not_a_list(make_config: Callable[[Any], Config]) -> None:
    assert make_config({"level": {"width": 14}}).level == []
