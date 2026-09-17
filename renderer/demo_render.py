import sys
from pathlib import Path

import pygame

sys.path.insert(0, str(Path(__file__).parent.parent / "maze"))
from mazegenerator import MazeGenerator


# Wall bitmasks supplied by the maze generator
N, E, S, W = 1, 2, 4, 8


# Pygame settings
CELL_SIZE = 40
WALL_WIDTH = 15

WINDOW_WIDTH = 15 * CELL_SIZE
WINDOW_HEIGHT = 15 * CELL_SIZE

FPS = 60


# Colors
BACKGROUND = (0, 0, 0)
WALL_COLOR = (30, 100, 255)
GUM_COLOR = (255, 220, 100)
PACMAN_COLOR = (255, 220, 0)


def draw_maze(screen, maze):
    """
    Draw the maze walls and Pac-Gums.
    """

    height = len(maze)
    width = len(maze[0])

    for y in range(height):
        for x in range(width):

            cell = maze[y][x]
            left = x * CELL_SIZE
            top = y * CELL_SIZE
            right = left + CELL_SIZE
            bottom = top + CELL_SIZE

            # ------------------------------------------------
            # Pac-Gum
            # ------------------------------------------------
            #
            # A cell with value 15 has all four walls closed.
            # Therefore we don't put a gum there.
            #
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

            # ------------------------------------------------
            # Walls
            # ------------------------------------------------

            # North
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

def find_center_position(maze):
    """
    Find the cell closest to the center of the maze
    that isn't completely closed.

    Returns:
        (x, y)
    """

    height = len(maze)
    width = len(maze[0])

    center_x = width // 2
    center_y = height // 2

    # If the exact center is usable, use it.
    if maze[center_y][center_x] != 15:
        return center_x, center_y

    # Otherwise search outward for the closest usable cell.
    max_distance = max(width, height)

    for distance in range(1, max_distance):

        for dy in range(-distance, distance + 1):
            for dx in range(-distance, distance + 1):

                x = center_x + dx
                y = center_y + dy

                if 0 <= x < width and 0 <= y < height:

                    if maze[y][x] != 15:
                        return x, y

    # Fallback
    return center_x, center_y


def draw_pacman(screen, x, y):
    """
    Draw Pac-Man in the center of a maze cell.
    """

    center_x = x * CELL_SIZE + CELL_SIZE // 2
    center_y = y * CELL_SIZE + CELL_SIZE // 2

    radius = CELL_SIZE // 3

    pygame.draw.circle(
        screen,
        PACMAN_COLOR,
        (center_x, center_y),
        radius,
    )


def main() -> None:

    # --------------------------------------------
    # Generate maze
    # --------------------------------------------

    width = 15
    height = 15

    maze_generator = MazeGenerator(
        size=(width, height),
        seed=42,
    )

    maze = maze_generator.maze

    # --------------------------------------------
    # Find Pac-Man starting position
    # --------------------------------------------

    pacman_x, pacman_y = find_center_position(maze)

    # --------------------------------------------
    # Initialise Pygame
    # --------------------------------------------

    pygame.init()

    screen = pygame.display.set_mode(
        (
            width * CELL_SIZE,
            height * CELL_SIZE,
        )
    )

    pygame.display.set_caption("Pac-Man")

    clock = pygame.time.Clock()

    running = True

    # --------------------------------------------
    # Game loop
    # --------------------------------------------

    while running:

        # Handle events
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

        # ----------------------------------------
        # Draw background
        # ----------------------------------------

        screen.fill(BACKGROUND)

        # ----------------------------------------
        # Draw maze + gums
        # ----------------------------------------

        draw_maze(screen, maze)

        # ----------------------------------------
        # Draw Pac-Man
        # ----------------------------------------

        draw_pacman(
            screen,
            pacman_x,
            pacman_y,
        )

        # ----------------------------------------
        # Update display
        # ----------------------------------------

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
