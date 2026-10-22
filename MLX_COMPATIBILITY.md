# MLX compatibility

The subject (chapter IV) asks for "a simple graphical library (MLX or
similar)" and adds:

> A graphical library is considered similar to MLX if each function you use
> has an equivalent in the MLX library. If a function you rely on has no MLX
> equivalent, it is not allowed.

We use pygame-ce, so we went through every pygame call of the game and
replaced the ones the MLX can't do. The MLX only offers:

- a window: `mlx_new_window`, `mlx_clear_window`, `mlx_destroy_window`;
- pixels: `mlx_pixel_put`;
- images: `mlx_new_image`, `mlx_png_file_to_image` / `mlx_xpm_file_to_image`,
  `mlx_get_data_addr` (read and write the pixels of an image),
  `mlx_put_image_to_window`;
- text in its built-in font: `mlx_string_put`;
- events and the loop: `mlx_hook`, `mlx_key_hook`, `mlx_loop_hook`, `mlx_loop`.

There is no shape drawing (lines, rectangles, circles), no TTF font loading,
no transparency blending, no window scaling and no clock.

## What changed

| Before                                       | Problem                     | Now                                                         |
|----------------------------------------------|-----------------------------|-------------------------------------------------------------|
| `pygame.draw.line` for the walls             | MLX has no line drawing     | `wall_horizontal.png` / `wall_vertical.png` images          |
| `pygame.draw.rect` for the "42" cells        | MLX has no rectangles       | `block_42.png` image                                        |
| `pygame.draw.circle` for the pacgums         | MLX has no circles          | `pacgum.png` image                                          |
| `pygame.font.Font("pacman.ttf", size)`, `render` | MLX can't load a TTF font, only its own font in one size | Bitmap font: PNG sheets of glyphs, drawn by `src/font.py` |
| `pygame.font.init()`                         | Only needed by the TTF font | Removed                                                     |
| `screen.subsurface(...)` for the maze area   | MLX has no sub-images       | Positions are shifted by `HUD_HEIGHT` (`Draw._cell_center`) |
| `pygame.SCALED` window flag                  | MLX can't scale a window    | Removed: the window has the real size of the maze           |
| Pause: game darkened by a `SRCALPHA` surface | MLX has no alpha blending   | Pause menu drawn on a black screen                          |
| `pygame.time.Clock().tick(FPS)`              | MLX has no clock            | `time.monotonic()` and `time.sleep()` from Python           |
| `pygame.time.get_ticks()` (mouth animation)  | MLX has no clock            | `time.monotonic()`                                          |

The game looks the same. We rendered every screen before and after the
change and compared them pixel by pixel. The menu, game, HUD, instructions,
leaderboard, save, victory and game over screens have **0 different pixels**.
Only the pause screen changed, because it no longer shows the darkened game
behind the menu.

## Details

### Walls, "42" cells and pacgums are images

Before, `Draw.maze` drew 4 lines per cell with `pygame.draw.line`, the "42"
cells with `pygame.draw.rect`, and `Draw.gums` drew a circle per pacgum.

Now `Draw.load_assets` loads these images from `assets/game/` and
`Draw.maze` / `Draw.gums` only blit them:

| Image                      | Size (px) | Used for                                       |
|----------------------------|-----------|------------------------------------------------|
| `wall_horizontal.png`      | 57 × 4    | North and south walls of a cell                |
| `wall_vertical.png`        | 4 × 57    | East and west walls of a cell                  |
| `wall_horizontal_edge.png` | 57 × 3    | North wall of the top row (see below)          |
| `block_42.png`             | 56 × 56   | Cells closed on all sides (the "42" pattern)   |
| `pacgum.png`               | 8 × 8     | Pacgum                                         |

The images are exactly what pygame used to draw. A wall image is centered on
the cell edge, one pixel above (or left of) it, as pygame centered its 4 pixel
lines. The `shift` in `Draw.maze` does that.

Before, the maze was drawn in a sub-surface under the HUD, which cut the
first pixel row of the top walls. Without the sub-surface, that row would
cover the bottom of the HUD, so the top border uses `wall_horizontal_edge.png`,
the same image without its first row.

`WALL_WIDTH` and `GUM_COLOR` were removed from `src/definitions.py`: the
thickness and the color are now in the images.

### Text uses a bitmap font

`pacman.ttf` is no longer loaded by the game. Its glyphs were rendered once,
for every size the screens use (64, 48, 32, 24, 20, 16 and 8), and saved as
images:

- `assets/fonts/pacman_<size>.png`: one row with every printable ASCII
  character (space to `~`), white on transparent;
- `assets/fonts/pacman.json`: for each size, the line height (`height`), the
  height of the glyph images (`image_height`) and, for each character, its
  `x` position and width in the sheet.

`src/font.py` has the `BitmapFont` class that replaces `pygame.font.Font`.
It keeps the methods the drawing code used, so the layouts didn't change:

- `size(text)` returns the width (sum of the glyph widths) and the line
  height, like `Font.size`;
- `get_height()` returns the line height, like `Font.get_height`;
- `draw(screen, text, topleft, color)` blits one glyph image after the other.

The sheets are white. The first time a character is needed in a color,
`BitmapFont._glyph` creates a new image and copies the glyph pixel by pixel
in that color (`get_at` / `set_at`, what `mlx_get_data_addr` allows on an MLX
image). The result is cached, so each (character, color) pair is only built
once. The first frame of the menu takes about 0.16 s because of that, then
drawing text is just blits.

`Draw.text` places the text the same way as before: a `pygame.Rect` (only
coordinates, nothing drawn) of the text size is anchored at the given point,
then the glyphs are drawn from its top-left corner. The font is pixel art
without antialiasing, so every pixel is fully on or off. Recoloring needs no
blending.

### No sub-surface for the maze

`Draw.game_screen` used `screen.subsurface(...)` so the maze could be drawn
from (0, 0) under the HUD. Now everything is drawn on the screen itself:
`Draw._cell_center` adds `HUD_HEIGHT` to the y of Pac-Man, the ghosts and the
pacgums, and `Draw.maze` does the same for the walls.

### Window, loop and time

- `pygame.display.set_mode(size)` without `pygame.SCALED`, like
  `mlx_new_window(mlx, width, height, title)`.
- `Render.display` no longer uses `pygame.time.Clock`. Each frame measures
  `dt` with `time.monotonic()`, then sleeps for the rest of the frame with
  `time.sleep()` to keep `FPS` frames per second. These are Python standard
  library functions, not graphics functions.
- The mouth animation uses `time.monotonic()` instead of
  `pygame.time.get_ticks()`.

## pygame functions still used, and their MLX equivalent

| pygame                                         | MLX                                              |
|------------------------------------------------|--------------------------------------------------|
| `pygame.display.set_mode(size)`                | `mlx_init` + `mlx_new_window`                    |
| `pygame.display.set_caption(title)`            | `title` argument of `mlx_new_window`             |
| `screen.fill(BACKGROUND)` (black)              | `mlx_clear_window`                               |
| `pygame.image.load(path)`, `.convert_alpha()`  | `mlx_png_file_to_image`                          |
| `Surface((w, h), SRCALPHA)`                    | `mlx_new_image`                                  |
| `surface.get_at` / `surface.set_at`            | read / write a pixel through `mlx_get_data_addr` |
| `screen.blit(image, pos)`                      | `mlx_put_image_to_window`                        |
| `pygame.display.flip()`                        | end of the frame in the `mlx_loop_hook`          |
| `pygame.event.get()`, `KEYDOWN`, `K_*`         | `mlx_hook` / `mlx_key_hook` with key codes       |
| `QUIT` event                                   | `mlx_hook` on the window close event (17)        |
| `pygame.quit()`                                | `mlx_destroy_window`                             |
| `get_rect`, `get_size`, `get_width`, `pygame.Rect` | no drawing: only width / height and coordinate math |

## Regenerating the images

The images were generated once with a small script that used `pygame.font`
and `pygame.draw` *outside* the game. They only need to be generated again
to change the wall thickness, the pacgum, the "42" color or add a font size:

1. Draw the shape (or render each glyph of `pacman.ttf` without antialiasing)
   on a transparent surface.
2. Crop it to its bounding box and save it as PNG in `assets/game/` (shapes)
   or `assets/fonts/` (one sheet per size, plus its entry in `pacman.json`).
3. For a new font size, also add it to `FONT_SIZES` in `src/draw.py`.
