from abc import ABC

from src.definitions import GhostState
from src.config import Config
from src.entity import Entity
from src.maze import Maze


class Ghost(Entity, ABC):
    def __init__(
        self,
        maze: Maze,
        config: Config,
        x: int,
        y: int,
        color: tuple[int, int, int],
    ) -> None:
        super().__init__(maze, config, x, y, color=color)

    # @abstractmethod 0, 0 just for tests
    def target(self):
        return 0, 0

    # Change the state of the Ghost, chase / scatter / frightened / eaten
    def change_state(self): ...


class Inky(Ghost):
    pass


class Pinky(Ghost):
    pass


class Clyde(Ghost):
    pass


class Blinky(Ghost):
    pass
