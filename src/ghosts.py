import random
from abc import ABC
from collections import deque

from src.config import Config
from src.definitions import (
    DOWN,
    EATEN_VEL,
    EATEN_WAIT,
    LEFT,
    RIGHT,
    STILL,
    UP,
    GhostState,
)
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
        vel: float,
    ) -> None:
        # Change the state of the Ghost, chase / scatter / frightened / eaten
        self.state = GhostState.CHASE
        self.state_timer: float = 0.0
        super().__init__(
            maze, config, x, y, color=color, sprite_path=sprite_path, vel=vel
        )
        self.flag_random = False
        self.base_vel = vel
        # Cheat (F2): a frozen ghost stays still in the same position
        self.frozen = False

    def set_state(self, state: GhostState, duration: float) -> None:
        self.state = state
        self.state_timer = duration

    def update_state(self, dt: float) -> None:
        if self.state_timer > 0:
            self.state_timer -= dt
            if self.state_timer <= 0:
                if self.state == GhostState.EATEN:
                    self.revive()
                else:
                    self.state = GhostState.CHASE
                    self.flag_random = False

    def get_eaten(self) -> None:
        """Turn into eyes that run back to the spawn corner."""
        self.set_state(GhostState.EATEN, 0)
        self.vel = EATEN_VEL
        # Go straight home, even if it was wandering randomly
        self.flag_random = False

    def wait_at_home(self) -> None:
        """Stay as eyes in the spawn corner for a while before reviving."""
        self.set_state(GhostState.EATEN, EATEN_WAIT)
        # Stand still in the corner: no sliding back to the previous cell
        self.prev = self.x, self.y
        self.direction = STILL

    def revive(self) -> None:
        """Back to normal once the eyes reach the spawn corner."""
        self.set_state(GhostState.CHASE, 0)
        self.vel = self.base_vel
        self.flag_random = False

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

    def _flee(self, target: tuple[int, int]) -> tuple[int, int] | None:
        """Return the neighbour cell farthest from `target`, if any."""
        distances = self._bfs(target)
        here = (self.x, self.y)
        options = [c for c in self.maze.neighbours[here] if c in distances]
        if not options:
            return None

        return max(options, key=lambda c: distances[c])

    def get_dir_flee(self, pacman: Pacman) -> tuple[int, int]:
        """Return the direction that takes the ghost away from pacman."""
        next_coord = self._flee((pacman.x, pacman.y))
        if next_coord is None:
            return STILL
        return next_coord[0] - self.x, next_coord[1] - self.y

    def get_dir(self, pacman: Pacman) -> tuple[int, int]:
        """Return the direction the ghost will take on its next step."""
        return self.random_move()

    def get_dir_spawn(self, spawn_pos: tuple[int, int]) -> tuple[int, int]:
        next_coord = self._chase(spawn_pos)
        if next_coord is None or self.flag_random:
            self.flag_random = True
            return self.random_move()
        return next_coord[0] - self.x, next_coord[1] - self.y

    def random_move(self) -> tuple[int, int]:
        """Keep going straight, pick a random open direction when blocked."""
        if self.direction != STILL and self.able_to_move(self.direction):
            return self.direction

        directions = [UP, DOWN, LEFT, RIGHT]
        valid_dir = [dir for dir in directions if self.able_to_move(dir)]
        if not valid_dir:
            return STILL
        return random.choice(valid_dir)

    def find_target(
        self, pacman: Pacman, tiles_away: int
    ) -> tuple[int, int] | None:
        """
        Compute a valid coord 4 or 8 tiles away
        from the ghost's position.
        """
        px, py = pacman.x, pacman.y
        distances = self._bfs((px, py))
        for key, value in distances.items():
            if tiles_away == 4 and value == 4:
                return key
            if tiles_away == 8 and value == 8:
                return key
        return None


class Inky(Ghost):
    """Random (uses Ghost.random_move)."""


# This one will target 4 spaces ahead of where the pac-man is located.
class Pinky(Ghost):
    """Random (uses Ghost.random_move)."""

    def get_dir(self, pacman: Pacman) -> tuple[int, int]:
        target = self.find_target(pacman, 4)
        if target is None:
            return STILL
        next_coord = self._chase(target)
        if next_coord is None:
            return STILL
        return next_coord[0] - self.x, next_coord[1] - self.y


# The Clyde will target 8 spaces ahead of the pac-man.
class Clyde(Ghost):
    """Random (uses Ghost.random_move)."""

    def get_dir(self, pacman: Pacman) -> tuple[int, int]:
        target = self.find_target(pacman, 8)
        if target is None:
            return STILL
        next_coord = self._chase(target)
        if next_coord is None:
            return STILL
        return next_coord[0] - self.x, next_coord[1] - self.y


class Blinky(Ghost):
    """Chase the pac-man directly, following the shortest path to him."""

    def get_dir(self, pacman: Pacman) -> tuple[int, int]:
        next_coord = self._chase((pacman.x, pacman.y))
        if next_coord is None:
            return STILL
        return next_coord[0] - self.x, next_coord[1] - self.y
