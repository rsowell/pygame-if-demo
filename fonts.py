from pathlib import Path
import pygame
from settings import asset_path


def load_font(filename, size, fallback_name=None, bold=False):
    path = Path(asset_path("fonts", filename))
    if path.exists():
        return pygame.font.Font(str(path), size)

    print(f"Font warning: could not load fonts/{filename}; using fallback font.")
    return pygame.font.SysFont(fallback_name, size, bold=bold)


def menu_label_font():
    return load_font("LibreBaskerville-Regular.ttf", 16, fallback_name="georgia")
