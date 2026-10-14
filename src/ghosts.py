import random
from abc import ABC
from collections import deque

from src.config import Config
from src.definitions import DOWN, LEFT, RIGHT, UP, PACMAN_COLOR
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
        self.last_move = None

        super().__init__(
            maze, config, x, y, color=color, sprite_path=sprite_path
        )

    # @abstractmethod 0, 0 just for tests
    def target(self):
        return 0, 0

    # Change the state of the Ghost, chase / scatter / frightened / eaten
    def change_state(self): ...


    def _bfs(self, entry: tuple[int, int]):
        """Return the distances between the target and the ghost."""
        distances = {entry: 0}
        q = deque()
        q.append(entry)
        while q:
            curr = q.popleft()
            for x in self.maze.neighbours[curr]:
                if x not in distances:
                    q.append(x)
                    distances[x] = distances[curr] + 1
        return distances

    def _chase(self, target: tuple[int, int]) -> tuple[int, int] | None:
        """Return the direction of the neighbour closest to `target`."""
        here = (self.x, self.y)
        if here == target:
           return None

        distances = self._bfs(target)
        #print(f"DISTANCES: {distances}")
        options = [c for c in self.maze.neighbours[here] if c in distances]
        #print(f"OPTIONS: {options}")
        if not options:
            return None

        return min(options, key=lambda c: distances[c])
        

    def move(self, pacman: Pacman) -> None:
        """Actually move the ghost cell by cell."""
        direction = self.get_dir(pacman)
        if direction is None:
            return
        self.last_move = direction
        dx, dy = direction
        self.x += dx
        self.y += dy


# The Inky will have a random moviment behaviour.
class Inky(Ghost):

    def get_dir(self, pacman):
        return self.random_move()

    def random_move(self) -> str:
        if self.last_move is not None:
            if self.able_to_move(self.last_move):
                return self.last_move

        directions = [UP, DOWN, LEFT, RIGHT]
        valid_dir = [dir for dir in directions if self.able_to_move(dir)]
        choice = random.choice(valid_dir)
        return choice


# This one will follow the pac-man directly where he is located.
class Blinky(Ghost):

    def get_dir(self, pacman):
        next_coord = self._chase((pacman.x, pacman.y))
        print(f"NEXT_COORD: {next_coord}")
        if next_coord is None:
            return None
        return next_coord[0] - self.x, next_coord[1] - self.y


       
# This one will target 4 spaces ahead of where the pac-man is located.
class Pinky(Ghost):

    def get_dir(self, pacman):
        return self.random_move()

    def random_move(self) -> str:
        if self.last_move is not None:
            if self.able_to_move(self.last_move):
                return self.last_move

        directions = [UP, DOWN, LEFT, RIGHT]
        valid_dir = [dir for dir in directions if self.able_to_move(dir)]
        choice = random.choice(valid_dir)
        return choice


# The Clyde will target 8 spaces ahead of the pac-man.
class Clyde(Ghost):

    def get_dir(self, pacman):
        return self.random_move()

    def random_move(self) -> str:
        if self.last_move is not None:
            if self.able_to_move(self.last_move):
                return self.last_move

        directions = [UP, DOWN, LEFT, RIGHT]
        valid_dir = [dir for dir in directions if self.able_to_move(dir)]
        choice = random.choice(valid_dir)
        return choice



