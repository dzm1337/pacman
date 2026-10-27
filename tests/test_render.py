from collections.abc import Callable, Iterator
from typing import Any

import pygame
import pytest

from src.config import Config
from src.draw import Draw
from src.game import Game
from src.render import Render


def key(code: int) -> pygame.event.Event:
    return pygame.event.Event(pygame.KEYDOWN, key=code, unicode="")


def test_menu_resets_the_game_once(
    make_config: Callable[[Any], Config], monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    The menu resets the game when it is shown, not every frame: each reset
    generates a new maze (and its warnings for small mazes)
    """
    frames: Iterator[list[pygame.event.Event]] = iter(
        [[]] * 30  # stay on the menu
        + [[key(pygame.K_DOWN), key(pygame.K_RETURN)]]  # open Leaderboard
        + [[]] * 5
        + [[key(pygame.K_ESCAPE)]]  # back to the menu
        + [[]] * 30
        + [[pygame.event.Event(pygame.QUIT)]]
    )
    monkeypatch.setattr(pygame.event, "get", lambda: next(frames))
    game = Game(make_config({"width": 12, "height": 12}))
    resets = 0
    reset_game = game.reset_game

    def counted_reset() -> None:
        nonlocal resets
        resets += 1
        reset_game()

    monkeypatch.setattr(game, "reset_game", counted_reset)
    Render(Draw(game), game).display()
    assert resets == 1
