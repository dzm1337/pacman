from collections.abc import Callable
from typing import Any

import pygame
import pytest
from pygame import Surface

from src.config import Config
from src.definitions import CELL_SIZE, HUD_HEIGHT, MAX_LEVEL
from src.draw import Draw
from src.game import Game

HUGE = 10**30


@pytest.mark.parametrize(
    "content",
    [
        {},
        {"lives": HUGE},
        {"level_max_time": HUGE},
        {"points_per_pacgum": HUGE, "point_per_superpacgum": HUGE},
        {"seed": HUGE},
        {"pacgum": HUGE},
        {"pacgum": 1},
        {"lives": 1, "level_max_time": 1},
        {"width": 12, "height": 12},
        {"width": 25, "height": 15},
        {
            "level": [
                {"width": 12, "height": 15},
                {"width": 25, "height": 12},
                {},
            ]
        },
    ],
    ids=[
        "default",
        "huge_lives",
        "huge_time",
        "huge_points",
        "huge_seed",
        "huge_pacgum",
        "one_pacgum",
        "tiny",
        "min_size",
        "max_size",
        "mixed_levels",
    ],
)
def test_every_screen_and_level(
    content: dict[str, Any],
    make_config: Callable[[Any], Config],
    screen: Surface,
) -> None:
    """
    Draw every screen, then play a few frames of every level: nothing
    may raise, whatever the config
    """
    game = Game(make_config(content))
    draw = Draw(game)
    draw.load_assets()

    def play(frames: int) -> None:
        surface = pygame.display.set_mode(
            (game.width * CELL_SIZE, game.height * CELL_SIZE + HUD_HEIGHT)
        )
        for _ in range(frames):
            game.update(1 / 60)
            draw.game_screen(surface)
            game.move_ghost(1 / 60)

    for name in (
        "menu",
        "instructions",
        "leaderboard",
        "pause",
        "victory",
        "game_over",
    ):
        getattr(draw, name)(screen)
    draw.save(screen, "A" * 50, "x" * 200)

    play(120)
    for _ in range(MAX_LEVEL - 1):
        game.next_level()
        play(10)
    for _ in range(3):
        game._lose_life()
    game.reset_game()
    play(10)
