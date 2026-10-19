import random

from src.config import Config
from src.database import Database
from src.definitions import (
    BLINKY_COLOR,
    CLYDE_COLOR,
    DIRECTIONS,
    INKY_COLOR,
    PACMAN_COLOR,
    PINKY_COLOR,
    GameState,
    GhostState,
)
from src.ghosts import Blinky, Clyde, Inky, Pinky
from src.maze import Maze
from src.pacman import Pacman


class Game:
    def __init__(self, config: Config) -> None:
        self.db = Database()
        self.db.initialize_database()
        self.config = config
        self.score = 0
        self.level = 1
        self.state = GameState.PLAYING
        self.lives = self.config.lives
        self.time_left = config.level_max_time
        self.menu_options = [
            "Start",
            "Leaderboard",
            "Quit",
        ]
        self.options = [
            "Save Score",
            "Play Again",
            "Menu",
            "Quit",
        ]
        self.options_index = 0
        self.menu_index = 0
        self._setup_level()

    def valid_player_name(self, name: str) -> bool:
        return name.isalnum() and len(name) <= 12

    @property
    def is_level_won(self) -> bool:
        return not self.pacgums and not self.super_pacgums_pos

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
        # Open cell closest to each corner (x, y), in case a corner is a wall:
        # top-left, top-right, bottom-left, bottom-right
        self.corners: list[tuple[int, int]] = [
            self.maze.find_nearest_open_cell(x, y)
            for x, y in (
                (0, 0),
                (self.width - 1, 0),
                (0, self.height - 1),
                (self.width - 1, self.height - 1),
            )
        ]
        self.ghosts = [
            Inky(
                self.maze,
                self.config,
                *self.corners[0],
                color=INKY_COLOR,
                sprite_path="assets/game/inky.png",
                vel=2.7,
            ),
            Pinky(
                self.maze,
                self.config,
                *self.corners[1],
                color=PINKY_COLOR,
                sprite_path="assets/game/pinky.png",
                vel=2.5,
            ),
            Clyde(
                self.maze,
                self.config,
                *self.corners[2],
                color=CLYDE_COLOR,
                sprite_path="assets/game/clyde.png",
                vel=2.5,
            ),
            Blinky(
                self.maze,
                self.config,
                *self.corners[3],
                color=BLINKY_COLOR,
                sprite_path="assets/game/blinky.png",
                vel=2.2,
            ),
        ]
        self.pacman = Pacman(
            self.maze, self.config, PACMAN_COLOR, "assets/game/pacman.png", 4
        )
        self.pacgums: set[tuple[int, int]] = {
            (y, x)
            for x in range(self.width)
            for y in range(self.height)
            if self.maze.get_maze[y][x] != 15
        }
        self.super_pacgums_pos: set[tuple[int, int]] = set(self.corners)
        self.pacgums.discard((self.pacman.y, self.pacman.x))
        # Corners hold a super pacgum instead of a normal one
        for x, y in self.corners:
            self.pacgums.discard((y, x))

    def next_level(self) -> None:
        self.level += 1
        self._setup_level()

    def reset_game(self) -> None:
        self.score = 0
        self.level = 1
        self.lives = self.config.lives
        self._setup_level()

    def _lose_life(self) -> None:
        self.lives -= 1
        self.pacman.reset()
        for ghost in self.ghosts:
            ghost.reset()

    def _check_collision(self) -> None:
        for ghost in self.ghosts:
            ghost_pos = ghost.x, ghost.y
            pacman_pos = self.pacman.x, self.pacman.y
            if pacman_pos == ghost_pos or (
                self.pacman.prev == ghost_pos and ghost.prev == pacman_pos
            ):
                self._lose_life()
                return

    @property
    def is_alive(self) -> bool:
        return self.lives > 0 and self.time_left > 0

    def move_pacman(self, key: int) -> None:
        if key in DIRECTIONS:
            self.pacman.wanted_direction = DIRECTIONS[key]

    def move_ghost(self, dt: float) -> None:
        for ghost in self.ghosts:
            ghost.update_state(dt)
            if ghost.tick(dt):
                ghost.direction = ghost.get_dir(self.pacman)
                ghost.move(ghost.direction)

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
            if self.pacman.able_to_move(self.pacman.wanted_direction):
                self.pacman.direction = self.pacman.wanted_direction
            self.pacman.move(self.pacman.direction)
            self.eat_super_gum()
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

    def eat_super_gum(self) -> None:
        """
        Remove the super pacgum at pacman's position
        """
        pos = (self.pacman.x, self.pacman.y)
        if pos in self.super_pacgums_pos:
            self.super_pacgums_pos.remove(pos)
            self.score += self.config.point_per_superpacgum
            for ghost in self.ghosts:
                ghost.set_state(GhostState.FRIGHTENED, 7)
