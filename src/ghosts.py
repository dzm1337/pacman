from abc import ABC
from enum import Enum

from src.config import Config
from src.entity import Entity
from src.maze import Maze


class State(Enum):
    CHASE = 0
    SCATTER = 1
    FRIGHTENED = 2
    EATEN = 3


class Ghost(Entity, ABC):
    def __init__(self, maze: Maze, config: Config, x: int, y: int) -> None:
        super().__init__(maze, config, x, y)

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
