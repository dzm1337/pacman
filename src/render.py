import pygame
from pygame import Surface

from src.config import Config
from src.definitions import (
    BACKGROUND,
    CELL_SIZE,
    COLOR_42,
    FPS,
    GUM_COLOR,
    PACMAN_COLOR,
    WALL_COLOR,
    WALL_WIDTH,
    E,
    N,
    S,
    W,
)
from src.maze import Maze
from src.pacman import Pacman


class Render:
    def __init__(self, maze: Maze, config: Config) -> None:
        self.maze = maze.get_maze
        self.width, self.height = maze.get_shape
        self.pacman = Pacman(maze, config)
        self.running = True
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

    def draw_pacman(self, screen: Surface, dx: int, dy: int) -> None:
        px: int = dx * CELL_SIZE + CELL_SIZE // 2
        py: int = dy * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(screen, PACMAN_COLOR, (px, py), CELL_SIZE // 2 - 12)

    def display(self) -> None:
        screen: Surface = pygame.display.set_mode(
            (
                self.width * CELL_SIZE,
                self.height * CELL_SIZE,
            ),
            pygame.SCALED,
        )

        pygame.display.set_caption("PAC-MAN")
        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            keys = pygame.key.get_pressed()

            dx, dy = 0, 0

            if keys[pygame.K_UP]:
                dx, dy = 0, -1
            if keys[pygame.K_DOWN]:
                dx, dy = 0, 1
            if keys[pygame.K_LEFT]:
                dx, dy = -1, 0
            if keys[pygame.K_RIGHT]:
                dx, dy = 1, 0

            if (dx, dy) != (0, 0) and self.pacman.able_to_move(dx, dy):
                self.pacman.x += dx
                self.pacman.y += dy

            screen.fill(BACKGROUND)
            self.draw_maze(screen)
            self.draw_pacman(screen, self.pacman.x, self.pacman.y)

            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()
