import os
from pathlib import Path

os.environ.setdefault("SDL_RENDER_DRIVER", "software")

WIDTH, HEIGHT = 960, 640
FPS = 60


def asset_path(*parts):
    return str(Path("assets", *parts))
