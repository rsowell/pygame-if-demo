# Pygame Web Demo

Put audio files here:

- `assets/ambient_chapel.mp3`
- `assets/pickup.mp3`
- `assets/unlock.mp3`

The game will still run if those files are missing, but audio will be disabled.

## Run locally with normal Python

```bash
python main.py
```

## Run/build for browser with pygbag

Install pygbag:

```bash
python -m pip install pygbag --user --upgrade
```

From the folder **above** this project folder, run:

```bash
python -m pygbag pygame_web_demo
```

Open the local URL that pygbag prints, usually:

```text
http://localhost:8000
```

When ready to publish, use the generated files in:

```text
pygame_web_demo/build/web/
```

Upload that `web` folder to GitHub Pages, itch.io HTML5, Netlify, or any static web host.
