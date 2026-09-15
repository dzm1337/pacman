"""Renderiza a saida do MazeGenerator como um labirinto de Pac-Man em ASCII.

Uso: python3 renderer/demo_render.py [largura] [altura] [seed] [--no-color]
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "maze"))
from mazegenerator import MazeGenerator

N, E, S, W = 1, 2, 4, 8
MOVES = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}

EMPTY, WALL, LOGO, GUM, PATH, PACMAN, EXIT = range(7)

GLYPHS = {
    EMPTY: ("  ", ""),
    WALL: ("██", "\033[38;5;27m"),
    LOGO: ("▓▓", "\033[38;5;170m"),
    GUM: ("· ", "\033[38;5;223m"),
    PATH: ("◦ ", "\033[38;5;51m"),
    PACMAN: ("ᗧ ", "\033[38;5;226m"),
    EXIT: ("◎ ", "\033[38;5;46m"),
}
RESET = "\033[0m"


def build_tiles(gen):
    """Converte a grade de bitmasks numa grade de tiles (2*h+1) x (2*w+1)."""
    maze = gen.maze
    h, w = len(maze), len(maze[0])
    tiles = [[WALL] * (2 * w + 1) for _ in range(2 * h + 1)]

    # 1. escava os corredores a partir dos bits de parede de cada celula
    for y in range(h):
        for x in range(w):
            cell = maze[y][x]
            if cell == 15:  # celula isolada: bloco do '42'
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        tiles[2 * y + 1 + dy][2 * x + 1 + dx] = LOGO
                continue
            tiles[2 * y + 1][2 * x + 1] = GUM  # centro da celula: pacgum
            if not cell & N:
                tiles[2 * y][2 * x + 1] = EMPTY
            if not cell & S:
                tiles[2 * y + 2][2 * x + 1] = EMPTY
            if not cell & W:
                tiles[2 * y + 1][2 * x] = EMPTY
            if not cell & E:
                tiles[2 * y + 1][2 * x + 2] = EMPTY

    # 2. desenha o menor caminho por cima, seguindo as letras N/E/S/W
    if isinstance(gen.shortest_path, str):
        x, y = gen.maze_entry
        for letter in gen.shortest_path:
            dx, dy = MOVES[letter]
            tiles[2 * y + 1 + dy][2 * x + 1 + dx] = PATH  # passagem na parede
            x, y = x + dx, y + dy
            tiles[2 * y + 1][2 * x + 1] = PATH  # centro da celula seguinte

    # 3. entrada e saida por ultimo, para ficarem sempre visiveis
    ex, ey = gen.maze_entry
    sx, sy = gen.maze_exit
    tiles[2 * ey + 1][2 * ex + 1] = PACMAN
    tiles[2 * sy + 1][2 * sx + 1] = EXIT
    return tiles


def paint(tiles, color=True):
    lines = []
    for row in tiles:
        out = []
        for tile in row:
            glyph, ansi = GLYPHS[tile]
            out.append(f"{ansi}{glyph}{RESET}" if color and ansi else glyph)
        lines.append("  " + "".join(out).rstrip())
    return "\n".join(lines)


def legend(color=True):
    items = [
        (PACMAN, "entrada"),
        (EXIT, "saida"),
        (PATH, "menor caminho"),
        (GUM, "pacgum"),
        (WALL, "parede"),
        (LOGO, "'42'"),
    ]
    parts = []
    for tile, label in items:
        glyph, ansi = GLYPHS[tile]
        head = f"{ansi}{glyph}{RESET}" if color and ansi else glyph
        parts.append(f"{head}{label}")
    return "   ".join(parts)


def main(argv):
    color = sys.stdout.isatty() and "--no-color" not in argv
    args = [a for a in argv if not a.startswith("--")]
    width = int(args[0]) if len(args) > 0 else 12
    height = int(args[1]) if len(args) > 1 else 10
    seed = int(args[2]) if len(args) > 2 else 42

    gen = MazeGenerator(size=(width, height), seed=seed)
    tiles = build_tiles(gen)
    gums = sum(row.count(GUM) for row in tiles)
    path = gen.shortest_path

    print(f"\n  Pac-Man maze  {width}x{height}  seed {seed}\n")
    print(paint(tiles, color))
    print(
        f"\n  entrada {gen.maze_entry}   saida {gen.maze_exit}   "
        f"pacgums {gums}   passos {len(path) if path else 0}"
    )
    print(f"  {legend(color)}\n")
    if path:
        print(f"  caminho: {path}\n")


if __name__ == "__main__":
    main(sys.argv[1:])
