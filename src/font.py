import json
from pathlib import Path
from typing import Any

import pygame
from pygame import Surface

from src.definitions import ROOT

FONT_DIR = ROOT / "assets" / "fonts"
# Glyph positions in each sheet, and the line height of each size
FONT_META = FONT_DIR / "pacman.json"


class BitmapFont:
    """
    The pacman font baked into a PNG sheet of white glyphs, one per size.
    Text is drawn by copying glyph images onto the screen, like
    mlx_put_image_to_window: no TTF rendering while the game runs
    """

    def __init__(
        self,
        sheet: Surface,
        height: int,
        image_height: int,
        glyphs: dict[str, list[int]],
    ) -> None:
        self.sheet = sheet
        # Line height, used to lay out rows of text
        self.height = height
        # Glyph images go a few pixels below the line height
        self.image_height = image_height
        # char -> [x in the sheet, width]
        self.glyphs = glyphs
        # (char, color) -> glyph image in that color, made on first use
        self._cache: dict[tuple[str, tuple[int, int, int]], Surface] = {}

    def get_height(self) -> int:
        return self.height

    def _glyph_box(self, char: str) -> list[int]:
        # Characters missing from the sheet are drawn as '?'
        return self.glyphs.get(char, self.glyphs["?"])

    def size(self, text: str) -> tuple[int, int]:
        """
        Width and height in pixels of the text written with this font
        """
        width = sum(self._glyph_box(char)[1] for char in text)
        return width, self.height

    def image_size(self, text: str) -> tuple[int, int]:
        """
        Size of the drawn text, glyphs included (positions the text)
        """
        return self.size(text)[0], self.image_height

    def _glyph(self, char: str, color: tuple[int, int, int]) -> Surface:
        key = (char, color)
        if key not in self._cache:
            sheet_x, width = self._glyph_box(char)
            glyph = Surface((width, self.image_height), pygame.SRCALPHA)
            for y in range(self.image_height):
                for x in range(width):
                    if self.sheet.get_at((sheet_x + x, y)).a:
                        glyph.set_at((x, y), color)
            self._cache[key] = glyph
        return self._cache[key]

    def draw(
        self,
        screen: Surface,
        text: str,
        topleft: tuple[int, int],
        color: tuple[int, int, int],
    ) -> None:
        """
        Draw the text one glyph image after the other from topleft
        """
        x, y = topleft
        for char in text:
            screen.blit(self._glyph(char, color), (x, y))
            x += self._glyph_box(char)[1]


def load_image(path: Path) -> Surface:
    """
    Load a PNG, raising OSError with the real reason (missing file,
    permission denied...) instead of pygame's generic message
    """
    with open(path, "rb") as file:
        try:
            return pygame.image.load(file, path.name)
        except pygame.error as e:
            raise ValueError(f"{path} is not a valid image: {e}") from e


def _is_size(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _check_font(size: int, entry: object, sheet: Surface) -> dict[str, Any]:
    """
    Return the FONT_META entry of a size, or raise ValueError if it doesn't
    match its sheet, so a broken file stops the game at start, not while
    drawing
    """
    where = f"{FONT_META.name}, size {size}"
    if not isinstance(entry, dict):
        raise ValueError(f"{where}: missing or not an object")
    for key in ("height", "image_height"):
        if not _is_size(entry.get(key)):
            raise ValueError(f"{where}: {key} must be a positive integer")
    if entry["image_height"] > sheet.get_height():
        raise ValueError(f"{where}: image_height is taller than the sheet")
    glyphs = entry.get("glyphs")
    if not isinstance(glyphs, dict) or "?" not in glyphs:
        raise ValueError(f"{where}: glyphs must be an object with '?'")
    for char, box in glyphs.items():
        if (
            not isinstance(box, list)
            or len(box) != 2
            or not all(isinstance(n, int) for n in box)
            or box[0] < 0
            or box[1] <= 0
            or box[0] + box[1] > sheet.get_width()
        ):
            raise ValueError(f"{where}: glyph {char!r} is outside the sheet")
    return entry


def load_fonts(sizes: tuple[int, ...]) -> dict[int, BitmapFont]:
    """
    Load the sheet of each size listed in FONT_META
    """
    try:
        meta = json.loads(FONT_META.read_text(encoding="utf-8"))
    except ValueError as e:
        # Not UTF-8 or not JSON
        raise ValueError(f"{FONT_META} is not valid JSON: {e}") from e
    if not isinstance(meta, dict):
        raise ValueError(f"{FONT_META.name} must contain a JSON object")
    fonts = {}
    for size in sizes:
        sheet = load_image(FONT_DIR / f"pacman_{size}.png")
        entry = _check_font(size, meta.get(str(size)), sheet)
        fonts[size] = BitmapFont(
            sheet, entry["height"], entry["image_height"], entry["glyphs"]
        )
    return fonts
