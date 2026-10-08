import random

from src.config import Config
from src.definitions import (
    BLINKY_COLOR,
    CLYDE_COLOR,
    DIRECTIONS,
    INKY_COLOR,
    PACMAN_COLOR,
    PINKY_COLOR,
    GameState,
)
from src.ghosts import Blinky, Clyde, Inky, Pinky
from src.maze import Maze
from src.pacman import Pacman


class Game:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.score = 0
        self.level = 1
        self.state = GameState.PLAYING
        self.lives = self.config.lives
        self.time_left = config.level_max_time
        self._setup_level()

    @property
    def is_level_won(self) -> bool:
        return not self.pacgums

    def _level_size(self) -> tuple[int, int]:
        i = self.level - 1
        if i < len(self.config.level):
            size = self.config.level[i]
            return size["width"], size["height"]
        return self.config.width, self.config.height

    def _level_seed(self) -> int:
        if self.level == 1:
            return self.config.seed
        return random.randint(0, 2**31)

    def _setup_level(self) -> None:
        self.state = GameState.PLAYING
        self.time_left = self.config.level_max_time
        self.width, self.height = self._level_size()
        self.maze = Maze(self.width, self.height, self._level_seed())

        self.ghosts = [
            Inky(
                self.maze,
                self.config,
                *self.maze.find_nearest_open_cell(0, 0),
                color=INKY_COLOR,
                sprite_path="assets/inky.png",
            ),
            Pinky(
                self.maze,
                self.config,
                *self.maze.find_nearest_open_cell(self.width - 1, 0),
                color=PINKY_COLOR,
                sprite_path="assets/pinky.png",
            ),
            Clyde(
                self.maze,
                self.config,
                *self.maze.find_nearest_open_cell(0, self.height - 1),
                color=CLYDE_COLOR,
                sprite_path="assets/clyde.png",
            ),
            Blinky(
                self.maze,
                self.config,
                *self.maze.find_nearest_open_cell(
                    self.width - 1, self.height - 1
                ),
                color=BLINKY_COLOR,
                sprite_path="assets/blinky.png",
            ),
        ]

        self.pacman = Pacman(
            self.maze, self.config, PACMAN_COLOR, "assets/pacman.png"
        )

        self.pacgums: set[tuple[int, int]] = {
            (y, x)
            for x in range(self.width)
            for y in range(self.height)
            if self.maze.get_maze[y][x] != 15
        }

        self.pacgums.discard((self.pacman.y, self.pacman.x))

    def next_level(self) -> None:
        self.level += 1
        self._setup_level()

    def reset_game(self) -> None:
        self.score = 0
        self.level = 1
        self.lives = self.config.lives
        self._setup_level()

    def _reset_positions(self) -> None:
        self.pacman.direction = (0, 0)
        self.pacman.x, self.pacman.y = self.pacman.spawn_pos
        for ghost in self.ghosts:
            ghost.x, ghost.y = ghost.spawn_pos

    def _check_collision(self) -> None:
        for ghost in self.ghosts:
            ghost_pos = ghost.x, ghost.y
            pacman_pos = self.pacman.x, self.pacman.y
            if pacman_pos == ghost_pos:
                self.lives -= 1
                self._reset_positions()

    @property
    def is_alive(self) -> bool:
        return self.lives > 0 and self.time_left > 0

    def change_direction(self, key: int) -> None:
        if key in DIRECTIONS:
            self.pacman.direction = DIRECTIONS[key]

    def _decide_state(self) -> None:
        if self.is_level_won:
            self.state = GameState.WON
        elif not self.is_alive:
            self.state = GameState.LOST

    def update(self, dt: float) -> None:
        """
        Advance the game by one frame
        """

        if self.state != GameState.PLAYING:
            return

        if self.pacman.tick(dt):
            self.pacman.move(*self.pacman.direction)
            self.eat_gum()

        self._decide_state()
        self.time_left -= dt
        self._check_collision()

    def eat_gum(self) -> None:
        """
        Remove the pacgum at pacman's position, if any,
        and add its points to the score.
        """
        pos = (self.pacman.y, self.pacman.x)
        if pos in self.pacgums:
            self.pacgums.remove(pos)
            self.score += self.config.points_per_pacgum
