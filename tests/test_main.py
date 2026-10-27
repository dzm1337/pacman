import pytest

from src import __main__ as entry
from src.render import Render


def interrupt(*args: object) -> None:
    raise KeyboardInterrupt


@pytest.mark.parametrize("where", ["parse", "display"])
def test_ctrl_c_quits_without_traceback(
    where: str,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    Ctrl+C while reading the config or while playing ends the game cleanly
    """
    if where == "parse":
        monkeypatch.setattr(entry, "parse_args", interrupt)
    else:
        monkeypatch.setattr(Render, "display", interrupt)
    argv = ["pac-man.py", "config/config.json"]
    monkeypatch.setattr(entry.sys, "argv", argv)
    with pytest.raises(SystemExit) as exit_info:
        entry.main()
    assert exit_info.value.code == 130
    assert "Interrupted" in capsys.readouterr().err
