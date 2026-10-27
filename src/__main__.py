import sys
from pathlib import Path

import pygame

from src.config import Config
from src.definitions import APP_DIR, FROZEN
from src.draw import Draw
from src.game import Game
from src.parser import Parser, fail
from src.render import Render


def parse_args(argv: list[str]) -> Path:
    """Return the config path given on the command line, or exit."""
    args = argv[1:]
    # The packaged game is started by a double click, without arguments:
    # it then uses the config.json shipped next to the executable
    if not args and FROZEN:
        args = [str(APP_DIR / "config.json")]

    if len(args) != 1:
        fail(
            "expected exactly one argument.\n"
            " usage: python3 pac-man.py <config.json>"
        )

    # Relative to the folder the game is run from, like any command
    path = Path(args[0])

    if path.suffix != ".json":
        fail(f"{path} is not a .json file.")

    return path


def main() -> None:
    """Load the config and run the game."""
    # Parse the config file properly, and pass all the data to Config class.

    try:
        path: Path = parse_args(sys.argv)
        config = Config(**Parser(path).parse_config())
        game = Game(config)
        draw = Draw(game)
        Render(draw, game).display()
    except KeyboardInterrupt:
        # Ctrl+C in the terminal: close the window, no traceback
        pygame.quit()
        print("\nInterrupted, quitting.", file=sys.stderr)
        raise SystemExit(130)


if __name__ == "__main__":
    main()
