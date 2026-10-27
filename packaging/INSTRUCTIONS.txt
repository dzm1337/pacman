PAC-MAN
=======

A remake of the 1980 arcade game, made at 42 by dde-paul and acobbaer.


LAUNCH
------

Double-click "pacman" (pacman.exe on Windows), or from a terminal in this
folder:

    ./pacman                    uses config.json from this folder
    ./pacman my_config.json     uses another config file

A terminal window stays open next to the game: config errors and warnings
are printed there.


CONTROLS
--------

    Arrows or WASD   Move (and navigate the menus)
    Enter            Select a menu option
    P or Esc         Pause / resume
    Esc              Go back (leaderboard, instructions)

Cheats (for the evaluation):

    F1   Invincibility
    F2   Freeze the ghosts
    F3   Extra life
    F4   Extra speed
    F5   Skip the level


CONFIGURATION
-------------

Edit config.json in this folder. Lines starting with # are comments.

    level                   Size of each level: [{"width": w, "height": h}]
    width                   Maze width in cells (12 to 25), default 14
    height                  Maze height in cells (12 to 15), default 14
    lives                   Lives at the start, default 3
    pacgum                  Validated, not used: every open cell has one
    points_per_pacgum       Points for a pacgum, default 10
    point_per_superpacgum   Points for a super-pacgum, default 50
    points_per_ghost        Points for an edible ghost, default 200
    seed                    Seed of the first level's maze, default 42
    level_max_time          Seconds to clear a level, default 90

A missing or invalid value prints a warning and uses its default. Unknown
keys are ignored.


HIGHSCORES
----------

The top 10 is saved in db/leaderboard.db, in this folder. Delete it to reset
the highscores.
