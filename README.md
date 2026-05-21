# Designing Worlds Pygame Starter

Refactored, modular version of the Pygame interactive fiction demo.

## Run locally

```bash
python main.py
```

## Build for the web with pygbag

From the directory above this project folder:

```bash
python -m pygbag designing_worlds_refactored
```

## File overview

- `main.py`: starts the game.
- `game.py`: main game loop.
- `settings.py`: resolution, FPS, asset paths.
- `theme.py`: colors.
- `fonts.py`: bundled font loading.
- `audio.py`: sound/music manager.
- `ui.py`: reusable choice menu.
- `rendering.py`: drawing helpers.
- `story.py`: editable story text.
- `scenes/title.py`: title screen.
- `scenes/dialogue.py`: main interactive fiction scene.

## Suggested folders

```text
assets/
  fonts/
    LibreBaskerville-Regular.ttf
    LibreBaskerville-Bold.ttf
  music/
    ambient_chapel.mp3
  sfx/
    pickup.mp3
    unlock.mp3
    move.mp3
    win.mp3
  images/
```

Missing audio files will not crash the game.
