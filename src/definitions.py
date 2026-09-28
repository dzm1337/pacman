from enum import Enum, auto

import pygame

N, E, S, W = 1, 2, 4, 8
CELL_SIZE = 40
WALL_WIDTH = 10
BACKGROUND = (0, 0, 0)
WALL_COLOR = (30, 100, 255)
GUM_COLOR = (255, 220, 100)
PACMAN_COLOR = (255, 220, 0)
COLOR_42 = (128, 128, 128)
FPS = 60
WALLS = {(0, -1): N, (1, 0): E, (0, 1): S, (-1, 0): W}
BLINKY_COLOR = (255, 0, 0)
PINKY_COLOR = (255, 184, 255)
INKY_COLOR = (0, 255, 255)
CLYDE_COLOR = (255, 184, 82)
FRIGHTENED_COLOR = (33, 33, 255)

DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
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
