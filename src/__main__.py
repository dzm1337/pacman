from mazegenerator import MazeGenerator


def main() -> None:
    maze: MazeGenerator = MazeGenerator((15, 15))
    grid = maze.maze
    for y, row in enumerate(grid):
        print(f"Row: {y}\n\ncontent:{row}\n")
        for x, col in enumerate(row):
            print(f"({x}, {y}): {grid[x][y]}")


if __name__ == "__main__":
    main()
