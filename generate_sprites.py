"""
generate_sprites.py

Generates simple, original placeholder sprites for Pac-Man and the 4 ghosts
(Blinky, Pinky, Inky, Clyde), and saves them into per-entity subfolders:

    assets/
        pacman/pacman.png
        blinky/blinky.png
        pinky/pinky.png
        inky/inky.png
        clyde/clyde.png

Run this once from your project root:
    python generate_sprites.py

These are placeholder shapes (not copies of the original arcade sprites) —
swap them out later with licensed or hand-drawn art whenever you like,
the filenames/paths will stay the same so your loading code won't break.
"""

import os
import pygame

pygame.init()

SIZE = 32
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

GHOST_COLORS = {
    "blinky": (255, 0, 0),      # red
    "pinky": (255, 184, 222),   # pink
    "inky": (0, 255, 222),      # cyan
    "clyde": (255, 184, 82),    # orange
}


def make_pacman(size):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    center = (size // 2, size // 2)
    radius = size // 2 - 1
    pygame.draw.circle(surf, (255, 255, 0), center, radius)
    # mouth wedge (pointing right)
    mouth = [
        center,
        (center[0] + radius, center[1] - radius // 2),
        (center[0] + radius, center[1] + radius // 2),
    ]
    pygame.draw.polygon(surf, (0, 0, 0, 0), mouth)  # transparent cut
    # actually cut the mouth using a separate transparent surface trick:
    pygame.draw.polygon(surf, (0, 0, 0), mouth)
    surf.set_colorkey(None)
    return surf


def make_ghost(size, color):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    # Body: rounded top (circle) + rectangle base
    radius = size // 2 - 1
    pygame.draw.circle(surf, color, (size // 2, radius), radius)
    pygame.draw.rect(surf, color, (1, radius, size - 2, size // 2))

    # Wavy bottom edge (scallops), cut out using background-colored circles
    scallop_count = 4
    scallop_w = (size - 2) / scallop_count
    for i in range(scallop_count):
        cx = int(1 + scallop_w * i + scallop_w / 2)
        pygame.draw.circle(surf, (0, 0, 0, 0), (cx, size - 1), int(scallop_w / 2))

    # Eyes (white with colored pupils looking forward)
    eye_radius = size // 7
    left_eye = (size // 2 - size // 6, size // 2 - 2)
    right_eye = (size // 2 + size // 6, size // 2 - 2)
    pygame.draw.circle(surf, (255, 255, 255), left_eye, eye_radius)
    pygame.draw.circle(surf, (255, 255, 255), right_eye, eye_radius)
    pupil_radius = max(1, eye_radius // 2)
    pygame.draw.circle(surf, (0, 0, 255), left_eye, pupil_radius)
    pygame.draw.circle(surf, (0, 0, 255), right_eye, pupil_radius)

    return surf


def save(surf, filename):
    folder = os.path.join(ASSETS_DIR)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(filename)
    pygame.image.save(surf, path)
    print(f"Saved: {path}")


def main():
    save(make_pacman(SIZE), "pacman.png")
    for name, color in GHOST_COLORS.items():
        save(make_ghost(SIZE, color), f"{name}.png")

    print("\nDone. Your assets folder now looks like:")
    print("assets/")
    print("pacman.png")
    for name in GHOST_COLORS:
        print(f"{name}.png")


if __name__ == "__main__":
    main()
