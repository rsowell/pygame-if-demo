# Designing Worlds Pygame Starter

A small Pygame framework for text-driven games that can run locally or in the browser with `pygbag`.

## Folder structure

```text
designing_worlds_pygame_starter/
  main.py
  assets/
    music/
    sfx/
    images/
    fonts/
```

Put all images, music, sound effects, and fonts inside `assets/`.

## Run locally

```bash
python -m pip install pygame
python main.py
```

The game still runs if sound files are missing.

## Build for the web

From the folder containing `designing_worlds_pygame_starter/`:

```bash
python -m pip install pygbag --user --upgrade
python -m pygbag designing_worlds_pygame_starter
```

Then open the local URL printed by pygbag.

## Publish on GitHub Pages

From inside `designing_worlds_pygame_starter/` after building:

```bash
rm -rf docs
cp -r build/web docs
git add .
git commit -m "Update web build"
git push
```

In GitHub: Settings → Pages → Deploy from branch → `main` → `/docs`.

## Where students should customize

- Edit `DialogueScene.rooms` to create rooms, exits, descriptions, and items.
- Add new command behavior in `DialogueScene.handle_command`.
- Add new sounds in `AudioManager` setup inside `Game.__init__`.
- Add new scenes by subclassing `Scene`.
- Put assets in `assets/music`, `assets/sfx`, and `assets/images`.
