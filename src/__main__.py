import sys
from pathlib import Path

from src.config import Config
from src.game import Game
from src.parser import Parser, fail
from src.render import Render


def parse_args(argv: list[str]) -> Path:
    args = argv[1:]

    if len(args) != 1:
        fail(
            "expected exactly one argument.\b usage: python3 -m src <config.json>"
        )

    path = Path(__file__).parent.parent / "config" / f"{args[0]}"

    if path.suffix != ".json":
        fail(f"{path} is not a .json file.")

    return path


def main() -> None:
    # Parse the config file properly, and pass all the data to Config class.

    path: Path = parse_args(sys.argv)
    config = Config(**Parser(path).parse_config())
    game = Game(config)
    Render(game).display()


if __name__ == "__main__":
    main()
