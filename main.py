import asyncio
import sys
from pathlib import Path

import pygame

WIDTH, HEIGHT = 960, 640
FPS = 60


def asset_path(*parts):
    """Return a path that works locally and with pygbag.

    Keep all project assets inside the assets/ folder.
    Example: asset_path("music", "ambient_chapel.mp3")
    """
    return str(Path("assets", *parts))


class Theme:
    BG = (12, 14, 24)
    PANEL = (28, 31, 48)
    PANEL_2 = (38, 42, 64)
    BORDER = (110, 116, 170)
    BORDER_DIM = (65, 70, 105)
    TEXT = (236, 238, 248)
    MUTED = (175, 181, 205)
    ACCENT = (221, 187, 102)
    ACCENT_DARK = (112, 82, 35)
    INPUT_BG = (18, 20, 32)
    ERROR = (235, 130, 130)


class AudioManager:
    """Small wrapper around pygame.mixer.

    Missing files are ignored so the starter still runs before students
    add their own music/sound effects.
    """

    def __init__(self):
        self.enabled = False
        self.sounds = {}
        try:
            pygame.mixer.init()
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def load_sound(self, name, filename):
        if not self.enabled:
            return
        try:
            self.sounds[name] = pygame.mixer.Sound(asset_path("sfx", filename))
        except (pygame.error, FileNotFoundError):
            print(f"Audio warning: could not load sfx/{filename}")
            self.sounds[name] = None

    def play_sound(self, name):
        sound = self.sounds.get(name)
        if self.enabled and sound is not None:
            sound.play()

    def play_music(self, filename, loops=-1, volume=0.35):
        if not self.enabled:
            return
        try:
            pygame.mixer.music.load(asset_path("music", filename))
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(loops)
        except (pygame.error, FileNotFoundError):
            print(f"Audio warning: could not load music/{filename}")

    def stop_music(self):
        if self.enabled:
            pygame.mixer.music.stop()


class ChoiceMenu:
    """Keyboard-navigable vertical choice menu."""

    def __init__(self, choices):
        # choices should be list of (label, callback)
        self.choices = choices
        self.selected = 0

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN or not self.choices:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.selected = (self.selected - 1) % len(self.choices)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.selected = (self.selected + 1) % len(self.choices)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            _, callback = self.choices[self.selected]
            callback()

    def draw(self, screen, font, x, y, width):
        for i, (label, _) in enumerate(self.choices):
            rect = pygame.Rect(x, y + i * 46, width, 38)
            selected = i == self.selected
            fill = Theme.ACCENT_DARK if selected else Theme.INPUT_BG
            border = Theme.ACCENT if selected else Theme.BORDER_DIM
            pygame.draw.rect(screen, fill, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, width=2, border_radius=8)
            prefix = "▶ " if selected else "  "
            draw_text(screen, font, prefix + label, rect.x + 12, rect.y + 8, Theme.TEXT)


class Scene:
    """Base class for all scenes.

    Subclasses usually override handle_event(), update(), and draw().
    """

    def __init__(self, game):
        self.game = game

    def on_enter(self):
        pass

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, screen):
        pass


class DialogueScene(Scene):
    """A simple text-heavy scene with room descriptions, commands, and choices."""

    def __init__(self, game):
        super().__init__(game)
        self.location = "dorm"
        self.inventory = []
        self.messages = []
        self.input_text = ""
        self.choice_menu = None
        self.door_unlocked = False
        self.game_over = False
        self.rooms = {
            "dorm": {
                "name": "Your Dorm Room",
                "description": "Your desk is buried under notebooks. A brass key glints beneath a syllabus. Outside, the quad is washed in moonlight.",
                "exits": {"east": "quad"},
                "items": ["key"],
                "image": None,
            },
            "quad": {
                "name": "The Moonlit Quad",
                "description": "The campus is quiet. Music drifts from the chapel. A wind moves through the trees like whispered stage directions.",
                "exits": {"west": "dorm", "north": "chapel"},
                "items": [],
                "image": None,
            },
            "chapel": {
                "name": "The Chapel",
                "description": "Candles flicker along the stone walls. A locked door waits behind the altar, humming faintly with music.",
                "exits": {"south": "quad"},
                "items": [],
                "image": None,
            },
        }

    def on_enter(self):
        self.set_text([
            ("Designing Worlds: A Tiny IF Demo", Theme.ACCENT),
            ("Type commands, or use the choices that appear. Try: look, go east, take key, inventory, unlock door", Theme.TEXT),
        ])
        self.describe_room()
        self.game.audio.play_music("ambient_chapel.mp3")

    def set_text(self, lines):
        """Replace the story panel with new text.

        Each line can be either a string or a (text, color) tuple.
        This keeps the main story area from becoming an endlessly growing log.
        """
        self.messages = []
        for line in lines:
            if isinstance(line, tuple):
                text, color = line
            else:
                text, color = line, Theme.TEXT
            self.messages.append((text, color))

    def write(self, text, color=None):
        """Append a short response to the current story panel."""
        self.messages.append((text, color or Theme.TEXT))

    def describe_room(self, note=None, note_color=Theme.TEXT):
        room = self.rooms[self.location]
        lines = []
        if note:
            lines.append((note, note_color))
            lines.append("")
        lines.append((room["name"], Theme.ACCENT))
        lines.append(room["description"])
        if room["items"]:
            lines.append(("You see here: " + ", ".join(room["items"]), Theme.MUTED))
        lines.append(("Exits: " + ", ".join(room["exits"].keys()), Theme.MUTED))
        self.set_text(lines)
        self.update_choices()

    def update_choices(self):
        room = self.rooms[self.location]
        if self.game_over:
            self.choice_menu = ChoiceMenu([
                ("Restart", self.restart),
                ("Quit", self.quit_game),
            ])
            return

        choices = []
        for direction in room["exits"]:
            choices.append((f"Go {direction}", lambda d=direction: self.go(d)))
        for item in room["items"]:
            choices.append((f"Take {item}", lambda item=item: self.take(item)))
        if self.location == "chapel" and not self.door_unlocked:
            choices.append(("Unlock door", lambda: self.unlock("door")))
        choices.append(("Look around", self.describe_room))
        self.choice_menu = ChoiceMenu(choices)

    def handle_event(self, event):
        if self.choice_menu:
            self.choice_menu.handle_event(event)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.handle_command(self.input_text)
                self.input_text = ""
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.game.change_scene(TitleScene(self.game))
            else:
                if event.unicode and event.unicode.isprintable():
                    self.input_text += event.unicode

    def handle_command(self, command):
        command = command.strip().lower()
        if not command:
            return
        words = command.split()
        verb = words[0]
        noun = " ".join(words[1:]) if len(words) > 1 else ""
        if verb in ["help", "?"]:
            self.set_text([
                ("Help", Theme.ACCENT),
                "Commands: look, go east, take key, take robe, inventory, unlock door, restart, quit",
                "You can also use the Choices panel with the arrow keys and Enter.",
            ])
        elif verb in ["look", "l"]:
            self.describe_room()
        elif verb in ["inventory", "i"]:
            self.set_text([
                ("Inventory", Theme.ACCENT),
                "You are carrying: " + ", ".join(self.inventory) if self.inventory else "You are carrying nothing.",
            ])
        elif verb in ["go", "walk", "move"]:
            self.go(noun)
        elif verb in ["north", "south", "east", "west"]:
            self.go(verb)
        elif verb in ["take", "get"]:
            self.take(noun)
        elif verb == "restart":
            self.restart()
        elif verb == "unlock":
            self.unlock(noun)
        elif verb == "quit":
            self.quit_game()
        else:
            self.set_text([
                ("I don't understand that command.", Theme.ERROR),
                "Try: look, go east, take key, inventory, unlock door, or help.",
            ])

    def restart(self):
        self.game.change_scene(DialogueScene(self.game))

    def quit_game(self):
        self.game.running = False

    def go(self, direction):
        if self.game_over:
            self.set_text([
                ("The story has ended.", Theme.ACCENT),
                "Choose Restart or Quit from the side panel.",
            ])
            self.update_choices()
            return
        room = self.rooms[self.location]
        if direction in room["exits"]:
            self.game.audio.play_sound("move")
            self.location = room["exits"][direction]
            self.describe_room(f"You go {direction}.", Theme.MUTED)
        else:
            self.set_text([
                ("You can't go that way.", Theme.ERROR),
                ("Available exits: " + ", ".join(room["exits"].keys()), Theme.MUTED),
            ])

    def take(self, item):
        room = self.rooms[self.location]
        if item in room["items"]:
            room["items"].remove(item)
            self.inventory.append(item)

            if item == "robe":
                self.win_game()
                return

            self.game.audio.play_sound("pickup")
            self.describe_room(f"You take the {item}.", Theme.ACCENT)
        else:
            self.set_text([
                ("You don't see that here.", Theme.ERROR),
                "Try looking around to see what is available.",
            ])
            self.update_choices()

    def unlock(self, thing):
        if self.location == "chapel" and thing == "door":
            if "key" in self.inventory:
                self.game.audio.play_sound("unlock")
                self.door_unlocked = True
                if "robe" not in self.rooms["chapel"]["items"] and "robe" not in self.inventory:
                    self.rooms["chapel"]["items"].append("robe")
                self.set_text([
                    ("The key turns.", Theme.ACCENT),
                    'The door opens onto a man in an ermine cape playing the carillon. His hair is an unnatural shade of silver and he is smiling at you. He says, "Tu vincis" and takes off the robe. As he holds it out for you, his body disintegrates, turns to smoke, and the ermine robe falls to the floor.',
                    ("You see here: robe", Theme.MUTED),
                ])
                self.update_choices()
            else:
                self.set_text([
                    ("The door is locked.", Theme.ERROR),
                    "You will need something that can open it.",
                ])
                self.update_choices()
        else:
            self.set_text([
                ("You can't unlock that.", Theme.ERROR),
                "There is nothing here that responds to that command.",
            ])
            self.update_choices()

    def win_game(self):
        self.game_over = True
        self.game.audio.stop_music()
        self.game.audio.play_sound("win")
        self.set_text([
            ("You are now the 19th Vice-Chancellor of the University of the South.", Theme.ACCENT),
            "The bells continue ringing long after the smoke clears.",
            ("Choose Restart or Quit from the side panel.", Theme.MUTED),
        ])
        self.update_choices()

    def draw(self, screen):
        draw_background(screen)
        draw_panel(screen, pygame.Rect(28, 28, 604, 492), "Story")
        draw_panel(screen, pygame.Rect(652, 28, 280, 492), "Choices")
        draw_panel(screen, pygame.Rect(28, 538, 904, 74), "Command")

        y = 70
        for message, color in self.messages:
            y = draw_text_wrapped(screen, self.game.font, message, 54, y, 552, color)

        if self.choice_menu:
            self.choice_menu.draw(screen, self.game.small_font, 674, 76, 236)

        draw_text(screen, self.game.font, "> " + self.input_text, 54, 574, Theme.TEXT)
        draw_text(screen, self.game.tiny_font, "Esc: title screen    Enter: submit command    ↑/↓ + Enter: choose", 670, 584, Theme.MUTED)


class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.menu = ChoiceMenu([
            ("Start demo", lambda: self.game.change_scene(DialogueScene(self.game))),
            ("Quit", self.quit_game),
        ])

    def quit_game(self):
        self.game.running = False

    def handle_event(self, event):
        self.menu.handle_event(event)

    def draw(self, screen):
        draw_background(screen)
        draw_panel(screen, pygame.Rect(150, 120, 660, 390), None)
        draw_text(screen, self.game.title_font, "Designing Worlds", 244, 194, Theme.ACCENT)
        draw_text(screen, self.game.font, "A Pygame framework for text-driven games", 268, 258, Theme.TEXT)
        draw_text(screen, self.game.small_font, "Use arrows/WASD to move through choices. Press Enter to select.", 252, 306, Theme.MUTED)
        self.menu.draw(screen, self.game.font, 330, 366, 300)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Designing Worlds Starter")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("georgia", 25)
        self.small_font = pygame.font.SysFont("georgia", 21)
        self.tiny_font = pygame.font.SysFont("georgia", 17)
        self.title_font = pygame.font.SysFont("georgia", 56, bold=True)
        self.audio = AudioManager()
        self.audio.load_sound("pickup", "pickup.mp3")
        self.audio.load_sound("unlock", "unlock.mp3")
        self.audio.load_sound("move", "move.mp3")
        self.audio.load_sound("win", "win.mp3")
        self.scene = TitleScene(self)
        self.scene.on_enter()
        self.running = True

    def change_scene(self, scene):
        self.scene = scene
        self.scene.on_enter()

    async def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene.handle_event(event)
            self.scene.update(dt)
            self.scene.draw(self.screen)
            pygame.display.flip()
            await asyncio.sleep(0)
        pygame.quit()


def draw_background(screen):
    screen.fill(Theme.BG)
    # Subtle star/noise field
    for x, y in [(90, 80), (180, 48), (320, 96), (760, 80), (860, 155), (105, 500), (810, 540)]:
        pygame.draw.circle(screen, Theme.BORDER_DIM, (x, y), 2)


def draw_panel(screen, rect, title=None):
    shadow = rect.move(5, 6)
    pygame.draw.rect(screen, (4, 5, 10), shadow, border_radius=14)
    pygame.draw.rect(screen, Theme.PANEL, rect, border_radius=14)
    pygame.draw.rect(screen, Theme.BORDER_DIM, rect, width=2, border_radius=14)
    if title:
        label_rect = pygame.Rect(rect.x + 18, rect.y - 12, 112, 24)
        pygame.draw.rect(screen, Theme.PANEL_2, label_rect, border_radius=8)
        pygame.draw.rect(screen, Theme.BORDER_DIM, label_rect, width=1, border_radius=8)


def draw_text(screen, font, text, x, y, color=Theme.TEXT):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_text_wrapped(screen, font, text, x, y, max_width, color=Theme.TEXT):
    if text == "":
        return y + font.get_height() // 2
    words = text.split()
    line = ""
    for word in words:
        test_line = line + word + " "
        if font.size(test_line)[0] <= max_width:
            line = test_line
        else:
            draw_text(screen, font, line, x, y, color)
            y += font.get_height() + 5
            line = word + " "
    if line:
        draw_text(screen, font, line, x, y, color)
        y += font.get_height() + 5
    return y


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
