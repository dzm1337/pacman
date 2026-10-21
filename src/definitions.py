from enum import Enum, auto

import pygame

N, E, S, W = 1, 2, 4, 8
CELL_SIZE = 56
WALL_WIDTH = 10
HUD_HEIGHT = 28
BACKGROUND = (0, 0, 0)
WALL_COLOR = (30, 100, 255)
GUM_COLOR = (255, 220, 100)
MAX_LEVEL = 10
# Highscore names: up to 10 letters, numbers and spaces
MAX_NAME_LENGTH = 10
PACMAN_COLOR = (255, 220, 0)
COLOR_42 = (128, 128, 128)
WHITE = (255, 255, 255)
FPS = 30
EATEN_VEL = 5.5
EATEN_WAIT = 2.5
# Seconds the ghosts stay edible after a super pacgum
FRIGHTENED_TIME = 7
# Last seconds of FRIGHTENED_TIME where the ghosts blink white,
# and how long each blink (blue or white) lasts
FRIGHTENED_BLINK_TIME = 2
BLINK_PERIOD = 0.2
WALLS = {(0, -1): N, (1, 0): E, (0, 1): S, (-1, 0): W}
BLINKY_COLOR = (255, 0, 0)
PINKY_COLOR = (255, 184, 255)
INKY_COLOR = (0, 255, 255)
CLYDE_COLOR = (255, 184, 82)
FRIGHTENED_COLOR = (33, 33, 255)
SUPER_PACGUM_COLOR = (255, 183, 174)

UP = 0, -1
DOWN = 0, 1
LEFT = -1, 0
RIGHT = 1, 0
STILL = 0, 0


DIRECTIONS = {
    pygame.K_UP: UP,
    pygame.K_w: UP,
    pygame.K_DOWN: DOWN,
    pygame.K_s: DOWN,
    pygame.K_LEFT: LEFT,
    pygame.K_a: LEFT,
    pygame.K_RIGHT: RIGHT,
    pygame.K_d: RIGHT,
}


class GameState(Enum):
    PLAYING = auto()
    WON = auto()
    LOST = auto()


class GhostState(Enum):
    CHASE = auto()
    SCATTER = auto()
    FRIGHTENED = auto()
    EATEN = auto()


class Screen(Enum):
    PLAYING = auto()
    MENU = auto()
    GAME_OVER = auto()
    WON = auto()
    LEADERBOARD = auto()
    SAVE = auto()
    PAUSED = auto()
    INSTRUCTIONS = auto()
