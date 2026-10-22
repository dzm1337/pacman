# Project Management

Project: Pac-Man (42 curriculum), from **2026-09-14** to **2026-10-22**.

Team:

- **dde-paul**: game core, interface and highscores
- **acobbaer**: maze integration, ghost AI, sprites and cheat mode

## Task split

We split the work by module, so each of us could work on separate files most
of the time and merge with few conflicts.

### dde-paul

| Area           | Tasks                                                                                   |
|----------------|-----------------------------------------------------------------------------------------|
| Setup          | `pyproject.toml` and `uv`, `.gitignore`, `Makefile` (install, run, debug, clean, lint)  |
| Configuration  | JSON parser with defaults, warnings, size clamping and per-level sizes; `Config` class  |
| Architecture   | `Maze` wrapper, `Entity` base class, `Game` class separated from rendering, `Draw`      |
| Gameplay       | Pac-Man movement and buffered turns, tick timer, lives, collisions (same cell and swap) |
| Levels         | Level setup, fixed seed on level 1, random seeds after, win and game over states        |
| Power-ups      | Super-pacgums in the corners, frightened and eaten states, eyes going back home          |
| Interface      | Menu, HUD, victory, game over, pause and instructions screens, Pac-Man mouth animation  |
| Highscores     | SQLite `Database` class, leaderboard screen, name entry and validation                  |
| Quality        | Type hints, flake8 / mypy fixes, README                                                 |

### acobbaer

| Area           | Tasks                                                                          |
|----------------|--------------------------------------------------------------------------------|
| Maze           | Integration of the assigned A-Maze-ing package (`mazegenerator` wheel)         |
| Ghost AI       | Ghost movement logic and the behaviour of each ghost (`ghosts.py`)             |
| Movement       | Entity speed (`vel`) for Pac-Man and the ghosts                                |
| Sprites        | Sprite loading and the entity sprites                                          |
| Cheat mode     | Invincibility, ghost freeze, extra life, extra speed and level skip (F1 to F5) |

## Timeline

| Dates           | Milestone                                                                     |
|-----------------|-------------------------------------------------------------------------------|
| 09-14 → 09-18   | Project setup, config parser, maze generator integrated, first Pac-Man moves  |
| 09-21 → 09-27   | `Entity` / `Game` architecture, ghost classes, tick timer, lives, collisions  |
| 09-27 → 10-08   | Sprites, menu screen, levels with new mazes, ghost movement (PR #1 to #3)     |
| 10-13 → 10-17   | Database and leaderboard, `Draw` module, game over / victory screens, HUD     |
| 10-16 → 10-20   | Ghost speed and behaviours, super-pacgums, frightened and eaten ghosts        |
| 10-21 → 10-22   | Pause, instructions, animations, cheat mode, config robustness, lint, README  |

## Workflow and tools

- **Git and GitHub**: one branch per feature or per person (`collision`,
  `game-flow`, `ghost-movement`, `database`, `cheat-modes`, `dde-paul`),
  merged into `main` through pull requests (#1 to #10).
- Before merging, the branch was updated with `main` and the conflicts were
  fixed on the branch, so `main` always ran.
- **Commit messages** with a prefix (`Feat:`, `Fix:`, `Refactor:`, `Chore:`)
  to keep the history readable.
- **uv** for the virtual environment and the dependencies, so we both ran
  the same versions of pygame-ce and the maze package.
- **flake8 and mypy** (`make lint`) to keep the code style and the types
  consistent between the two of us.

## Difficulties and what we learned

- **Merge conflicts**: early on we both edited `game.py` and `render.py` at
  the same time. Moving the drawing to `draw.py` and the rules to `game.py`
  split the code so each of us touched fewer shared files.
- **Coordinates**: some code used `(x, y)` and some `(y, x)`, which made the
  super-pacgums fail in some corners. We now keep `(x, y)` for positions.
- **Collisions**: Pac-Man and a ghost could cross each other without
  colliding when they swapped cells in the same step. We added a swap check.
- **Eaten ghosts**: getting the eyes back home and the ghost back to normal
  without glitches took several iterations (go home with a BFS, wait, revive).
