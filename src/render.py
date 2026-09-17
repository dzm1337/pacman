import pygame
from pygame import Surface

from src.config import Config
from src.maze import Maze
from src.pacman import Pacman

N, E, S, W = 1, 2, 4, 8
CELL_SIZE = 40
WALL_WIDTH = 10

BACKGROUND = (0, 0, 0)
WALL_COLOR = (30, 100, 255)
GUM_COLOR = (255, 220, 100)
PACMAN_COLOR = (255, 220, 0)
COLOR_42 = (128, 128, 128)

FPS = 30


class Render:
    def __init__(self, maze: Maze, config: Config) -> None:
        self.maze = maze.get_maze
        self.width, self.height = maze.get_shape
        self.center_x, self.center_y = maze.find_center_position()
        self.pacman = Pacman(maze, config)
        self.seed = config.seed

    def draw_maze(self, screen: Surface) -> None:
        for y in range(self.height):
            for x in range(self.width):
                cell = self.maze[y][x]
                left = x * CELL_SIZE
                top = y * CELL_SIZE
                right = left + CELL_SIZE
                bottom = top + CELL_SIZE

                if cell == 15:
                    pygame.draw.rect(
                        screen, COLOR_42, (left, top, CELL_SIZE, CELL_SIZE)
                    )
                    continue

                if cell != 15:
                    pygame.draw.circle(
                        screen,
                        GUM_COLOR,
                        (
                            left + CELL_SIZE // 2,
                            top + CELL_SIZE // 2,
                        ),
                        4,
                    )

                if cell & N:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (left, top),
                        (right, top),
                        WALL_WIDTH,
                    )

                # East
                if cell & E:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (right, top),
                        (right, bottom),
                        WALL_WIDTH,
                    )

                # South
                if cell & S:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (left, bottom),
                        (right, bottom),
                        WALL_WIDTH,
                    )

                # West
                if cell & W:
                    pygame.draw.line(
                        screen,
                        WALL_COLOR,
                        (left, top),
                        (left, bottom),
                        WALL_WIDTH,
                    )

    def draw_pacman(self, screen: Surface) -> None:
        px: int = self.center_x * CELL_SIZE + CELL_SIZE // 2
        py: int = self.center_y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(
            screen, PACMAN_COLOR, (px, py), CELL_SIZE // 2 - 7.5
        )

    def display(self) -> None:

        pygame.init()

        screen: Surface = pygame.display.set_mode(
            (
                self.width * CELL_SIZE,
                self.height * CELL_SIZE,
            )
        )

        pygame.display.set_caption("PAC-MAN")
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill(BACKGROUND)
            self.draw_maze(screen)
            self.draw_pacman(screen)

            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()
