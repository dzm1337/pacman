from json import JSONDecodeError, loads
from pathlib import Path
from sys import exit, stderr
from typing import Any

DEFAULT_CFG_PARAMS = {
    "highscore_filename": "highscore.json",
    "level": [],
    "width": 10,
    "height": 10,
    "lives": 3,
    "pacgum": 42,
    "points_per_pacgum": 10,
    "point_per_superpacgum": 50,
    "points_per_ghost": 200,
    "seed": 42,
    "level_max_time": 90,
}


class Parser:
    def __init__(self, path: Path):
        self.path = path

    def _load_file(self) -> str:
        try:
            raw = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            print(f"Error: File not found in path {self.path}", file=stderr)
            exit(1)
        except PermissionError:
            print(
                f"Error: Permission Denied to open file in path {self.path},",
                file=stderr,
            )
            exit(1)
        except (UnicodeDecodeError, IsADirectoryError) as e:
            print(f"Error: {e}", file=stderr)
            exit(1)
        if not raw:
            print(f"Error: File in path {self.path} is empty.", file=stderr)
            exit(1)
        return raw

    def _remove_comments(self) -> list[str]:
        file = self._load_file().split("\n")
        without_comments: list[str] = []
        for line in file:
            if line.lstrip().startswith("#"):
                continue
            without_comments.append(line)
        return without_comments

    def parse_json(self) -> dict[str, Any]:
        cleaned = "\n".join(self._remove_comments())
        try:
            config = loads(cleaned)
            if not isinstance(ret, dict):
                print("Error: Not a valid dictionary")
                exit(1)
        except JSONDecodeError as e:
            print(f"Error failed to parse JSON: {e}", file=stderr)
            exit(1)
        return config

    @staticmethod
    def is_positive(label: str, value: Any) -> bool:
        if not isinstance(value, int):
            print(f"Error: {label} must be an integer.", file=stderr)
            return False
        if value < 0:
            print(f"Error: {label} must be strictly positive.", file=stderr)
            return False
        return True

    def validate_highscore_file(self, param: str) -> bool:
        if not isinstance(param, str):
            print(f"Error: {param} must be a string", file=stderr)
            return False
        if not param.endswith(".json"):
            print(f"Error: {param} must end with .json", file=stderr)
            return False
        return True

    def parse_config(self):
        cfg: dict[str, Any] = self.parse_json()

        missing_params = [
            param for param in cfg if param not in DEFAULT_CFG_PARAMS
        ]

        print(missing_params)


#        for param, value in cfg.items():
##            if param not in DEFAULT_CFG_PARAMS:
##                print(
##                    "Parameter does not belong to default parameters. Skipping it."
##                )
##                continue
##            if param not in [
##                "highscore_filename",
##                "level",
##            ] and not is_positive(param, cfg[param]):
##                cfg[param] = DEFAULT_CFG_PARAMS[param]
##                continue
##            if param == "highscore_filename":
##                self.validate_highscore_file(param[cfg])
##            if param == "level":
##                if not isinstance(level, list):
#                    print("Error: Level must be a list", file=stderr)


if __name__ == "__main__":
    path: Path = Path(__file__).parent.parent / "config" / "config.json"
    parser = Parser(path)
    print(parser.parse_json())
