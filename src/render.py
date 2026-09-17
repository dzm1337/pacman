import sys
from pathlib import Path
import pygame
from maze.mazegenerator.mazegenerator import MazeGenerator
from src.config import Config
from src.pacman import Pacman


N, E, S, W = 1, 2, 4, 8
CELL_SIZE = 40
WALL_WIDTH = 10

BACKGROUND = (0, 0, 0)
WALL_COLOR = (30, 100, 255)
GUM_COLOR = (255, 220, 100)
PACMAN_COLOR = (255, 220, 0)

FPS = 30

class Render:

    def __init__(self, config: Config):
        self.width = config.width
        self.height = config.height
        self.seed = config.seed
        self.running = True
        self.pacman = Pacman(config)


    def draw_maze(self, screen, maze):
        
        for y in range(self.height):
            for x in range(self.width):
                
                cell = maze[y][x]
                left = x * CELL_SIZE
                top = y * CELL_SIZE
                right = left + CELL_SIZE
                bottom = top + CELL_SIZE

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

    def display(self) -> None:
        maze_generator = MazeGenerator(
            size=(self.width, self.height),
            seed=self.seed
        )
        
        maze = maze_generator.maze
        print(f"MAZE: {maze}")

        pygame.init()

        screen = pygame.display.set_mode(
            (
                self.width * CELL_SIZE,
                self.height * CELL_SIZE,
            )
        )

        pygame.display.set_caption("PAC-MAN")
        clock = pygame.time.Clock()

        self.running = True
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            screen.fill(BACKGROUND)
            self.draw_maze(screen, maze)
            #self.pacman.spawn_pacman()

            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()
