import pygame
from pygame import Surface

from src.definitions import (
    BACKGROUND,
    BLINKY_COLOR,
    CELL_SIZE,
    CLYDE_COLOR,
    COLOR_42,
    FPS,
    GUM_COLOR,
    INKY_COLOR,
    PACMAN_COLOR,
    PINKY_COLOR,
    WALL_COLOR,
    WALL_WIDTH,
    E,
    N,
    S,
    W,
)
from src.ghosts import Blinky, Clyde, Inky, Pinky

GHOST_COLORS = {
    Blinky: BLINKY_COLOR,
    Pinky: PINKY_COLOR,
    Inky: INKY_COLOR,
    Clyde: CLYDE_COLOR,
}

from src.game import Game


class Render:
    def __init__(self, game: Game) -> None:
        self.running = True
        self.game = game

    # draw ghosts
    def draw_ghosts(self, screen: Surface) -> None:
        for ghost in self.game.ghosts:
            px: int = ghost.x * CELL_SIZE + CELL_SIZE // 2
            py: int = ghost.y * CELL_SIZE + CELL_SIZE // 2
            color = GHOST_COLORS[type(ghost)]
            pygame.draw.circle(screen, color, (px, py), CELL_SIZE // 2 - 12)

    def draw_maze(self, screen: Surface) -> None:
        maze = self.game.maze.get_maze
        for y in range(self.game.height):
            for x in range(self.game.width):
                cell = maze[y][x]
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
                self.game.width * CELL_SIZE,
                self.game.height * CELL_SIZE,
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

            dt: float = clock.tick(FPS) / 1000
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

            self.game.update(dx, dy, dt)

            screen.fill(BACKGROUND)
            self.draw_maze(screen)
            self.draw_ghosts(screen)
            self.draw_pacman(screen, self.game.pacman.x, self.game.pacman.y)
            pygame.display.flip()

        pygame.quit()
