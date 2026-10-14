import random
from abc import ABC
from collections import deque

from src.config import Config
from src.definitions import DOWN, LEFT, RIGHT, STILL, UP
from src.entity import Entity
from src.maze import Maze
from src.pacman import Pacman


class Ghost(Entity, ABC):
    def __init__(
        self,
        maze: Maze,
        config: Config,
        x: int,
        y: int,
        color: tuple[int, int, int],
        sprite_path: str,
    ) -> None:
        super().__init__(
            maze, config, x, y, color=color, sprite_path=sprite_path
        )

    # Change the state of the Ghost, chase / scatter / frightened / eaten
    def change_state(self) -> None: ...

    def _bfs(self, entry: tuple[int, int]) -> dict[tuple[int, int], int]:
        """Return the distance from `entry` to every reachable cell."""
        distances = {entry: 0}
        q: deque[tuple[int, int]] = deque([entry])
        while q:
            curr = q.popleft()
            for x in self.maze.neighbours[curr]:
                if x not in distances:
                    q.append(x)
                    distances[x] = distances[curr] + 1
        return distances

    def _chase(self, target: tuple[int, int]) -> tuple[int, int] | None:
        """Return the neighbour cell closest to `target`, if any."""
        here = (self.x, self.y)
        if here == target:
            return None

        distances = self._bfs(target)
        options = [c for c in self.maze.neighbours[here] if c in distances]
        if not options:
            return None

        return min(options, key=lambda c: distances[c])

    def get_dir(self, pacman: Pacman) -> tuple[int, int]:
        """Return the direction the ghost will take on its next step."""
        return self.random_move()

    def random_move(self) -> tuple[int, int]:
        """Keep going straight, pick a random open direction when blocked."""
        if self.direction != STILL and self.able_to_move(self.direction):
            return self.direction

        directions = [UP, DOWN, LEFT, RIGHT]
        valid_dir = [dir for dir in directions if self.able_to_move(dir)]
        if not valid_dir:
            return STILL
        return random.choice(valid_dir)


class Inky(Ghost):
    """Random (uses Ghost.random_move)."""


class Pinky(Ghost):
    """Random (uses Ghost.random_move)."""


class Clyde(Ghost):
    """Random (uses Ghost.random_move)."""


class Blinky(Ghost):
    """Chase the pac-man directly, following the shortest path to him."""

    def get_dir(self, pacman: Pacman) -> tuple[int, int]:
        next_coord = self._chase((pacman.x, pacman.y))
        if next_coord is None:
            return STILL
        return next_coord[0] - self.x, next_coord[1] - self.y
