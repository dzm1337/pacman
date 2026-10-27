from collections.abc import Callable
from copy import deepcopy
from json import JSONDecodeError, loads
from pathlib import Path
import sys
from typing import Any, NoReturn

DEFAULT_CFG_PARAMS: dict[str, Any] = {
    "level": [],
    "width": 14,
    "height": 14,
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


# Maze size limits (in cells): smaller mazes don't fit the menus and texts,
# bigger ones don't fit on a screen. Values outside are clamped.
SIZE_LIMITS: dict[str, tuple[int, int]] = {
    "width": (12, 25),
    "height": (12, 15),
}


Rule = tuple[Callable[[Any], bool], str]

DEFAULT_RULE: Rule = (is_positive, "a strictly positive integer")
RULES: dict[str, Rule] = {
    "level": (lambda v: isinstance(v, list), "a list"),
}


def fail(message: str) -> NoReturn:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(1)


def warn(message: str) -> None:
    print(f"Warning: {message}", file=sys.stderr)


class Parser:
    def __init__(self, path: Path) -> None:
        self.path = path

    def _load_file(self) -> str:
        try:
            # utf-8-sig also accepts files saved with a BOM by some editors
            raw = self.path.read_text(encoding="utf-8-sig")
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
        except RecursionError:
            fail(f"{self.path} is nested too deeply.")
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

    def _clamp_size(self, param: str, value: int, where: str = "") -> int:
        """
        Keep a width or height inside SIZE_LIMITS, warning when it changes
        """
        low, high = SIZE_LIMITS[param]
        clamped = min(max(value, low), high)
        if clamped != value:
            warn(
                f"{where}{param} must be between {low} and {high}, "
                f"got {value}, using {clamped}."
            )
        return clamped

    def _resolve_levels(
        self, levels: list[Any], width: int, height: int
    ) -> list[dict[str, int]]:
        """
        Check every level entry: each one needs a valid width and height,
        a missing or wrong value uses the global width or height instead
        """
        resolved = []
        for i, level in enumerate(levels, start=1):
            where = f"level {i}: "
            if not isinstance(level, dict):
                warn(f"{where}must be an object, got {level}, using defaults.")
                level = {}
            size = {}
            for param, default in (("width", width), ("height", height)):
                value = level.get(param, default)
                if not is_positive(value):
                    warn(
                        f"{where}{param} must be a strictly positive "
                        f"integer, got {value}, using {default}."
                    )
                    value = default
                size[param] = self._clamp_size(param, value, where)
            resolved.append(size)
        return resolved

    def parse_config(self) -> dict[str, Any]:
        raw = self.parse_json()
        for param in raw.keys() - DEFAULT_CFG_PARAMS.keys():
            warn(f"{param} is not a known parameter, ignoring it.")
        config = {
            param: self._resolve(raw, param, default)
            for param, default in DEFAULT_CFG_PARAMS.items()
        }
        for param in SIZE_LIMITS:
            config[param] = self._clamp_size(param, config[param])
        config["level"] = self._resolve_levels(
            config["level"], config["width"], config["height"]
        )
        return config


if __name__ == "__main__":
    path: Path = Path(__file__).parent.parent / "config" / "config.json"
    print(Parser(path).parse_config())
