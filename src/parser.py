from collections.abc import Callable
from copy import deepcopy
from json import JSONDecodeError, loads
from pathlib import Path
from sys import stderr
from typing import Any, NoReturn

DEFAULT_CFG_PARAMS: dict[str, Any] = {
    "highscore_filename": "highscore.json",
    "level": [],
    "width": 12,
    "height": 10,
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "point_per_superpacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
}


def is_positive(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def is_highscore_filename(value: Any) -> bool:
    return isinstance(value, str) and value.endswith(".json")


Rule = tuple[Callable[[Any], bool], str]

DEFAULT_RULE: Rule = (is_positive, "a strictly positive integer")
RULES: dict[str, Rule] = {
    "highscore_filename": (is_highscore_filename, "a .json filename"),
    "level": (lambda v: isinstance(v, list), "a list"),
}


def fail(message: str) -> NoReturn:
    print(f"Error: {message}", file=stderr)
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"Warning: {message}", file=stderr)


class Parser:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _load_file(self) -> str:
        try:
            raw = self.path.read_text(encoding="utf-8")
        except OSError as e:
            fail(f"cannot read {self.path}: {e.strerror}")
        except UnicodeDecodeError:
            fail(f"{self.path} is not valid UTF-8.")
        if not raw.strip():
            fail(f"{self.path} is empty.")
        return raw

    def _remove_comments(self, text: str) -> str:
        return "\n".join(
            line
            for line in text.splitlines()
            if not line.lstrip().startswith("#")
        )

    def parse_json(self) -> dict[str, Any]:
        try:
            config = loads(self._remove_comments(self._load_file()))
        except JSONDecodeError as e:
            fail(f"{self.path} is not valid JSON: {e}")
        if not isinstance(config, dict):
            fail(f"{self.path} must contain a JSON object.")
        return config

    def _resolve(self, raw: dict[str, Any], param: str, default: Any) -> Any:
        check, expected = RULES.get(param, DEFAULT_RULE)
        if param not in raw:
            warn(f"{param} is missing, using default {default}.")
        elif not check(raw[param]):
            warn(
                f"{param} must be {expected}, got {raw[param]}, "
                f"using default {default}."
            )
        else:
            return raw[param]
        return deepcopy(default)

    def parse_config(self) -> dict[str, Any]:
        raw = self.parse_json()
        for param in raw.keys() - DEFAULT_CFG_PARAMS.keys():
            warn(f"{param} is not a known parameter, ignoring it.")
        return {
            param: self._resolve(raw, param, default)
            for param, default in DEFAULT_CFG_PARAMS.items()
        }


if __name__ == "__main__":
    path: Path = Path(__file__).parent.parent / "config" / "config.json"
    print(Parser(path).parse_config())
