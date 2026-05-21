import pygame
from rendering import draw_background, draw_panel, draw_text
from scenes.base import Scene
from scenes.title import TitleScene
from story import CHAPEL_TEXT, DORM_TEXT, ESSAY_TEXT, PURPLE_TEXT, QUAD_TEXT, UNLOCK_TEXT, WIN_TEXT
from theme import Theme
from ui import ChoiceMenu


class DialogueScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.location = "dorm"
        self.inventory = []
        self.messages = []
        self.choice_menu = None
        self.pages = []
        self.current_page = 0
        self.waiting_for_more = False
        self.door_unlocked = False
        self.game_over = False

        self.rooms = {
            "dorm": {
                "name": "Your Dorm Room",
                "description": DORM_TEXT,
                "exits": {"east": "quad"},
                "items": ["key"],
            },
            "quad": {
                "name": "The Moonlit Quad",
                "description": QUAD_TEXT,
                "exits": {"west": "dorm", "north": "chapel"},
                "items": [],
            },
            "chapel": {
                "name": "The Chapel",
                "description": CHAPEL_TEXT,
                "exits": {"south": "quad"},
                "items": [],
            },
        }

    def on_enter(self):
        self.game.audio.play_music("ambient_chapel.mp3")
        self.describe_room()

    def wrap_text(self, text, max_width):
        if text == "":
            return [""]

        lines = []
        for paragraph in text.split("\n"):
            if paragraph.strip() == "":
                lines.append("")
                continue

            words = paragraph.split()
            line = ""

            for word in words:
                test_line = line + word + " "
                if self.game.font.size(test_line)[0] <= max_width:
                    line = test_line
                else:
                    if line:
                        lines.append(line.rstrip())
                    line = word + " "

            if line:
                lines.append(line.rstrip())

        return lines

    def set_text(self, lines):
        if isinstance(lines, str):
            lines = [lines]

        story_top = 70
        story_bottom = 532
        line_height = self.game.font.get_height() + 5
        max_lines = max(1, (story_bottom - story_top) // line_height)
        display_lines = []

        for entry in lines:
            if isinstance(entry, tuple):
                text, color = entry
            else:
                text, color = entry, Theme.TEXT

            for wrapped_line in self.wrap_text(text, 552):
                display_lines.append((wrapped_line, color))

        pages = []
        for i in range(0, len(display_lines), max_lines):
            pages.append(display_lines[i:i + max_lines])

        if not pages:
            pages = [[("", Theme.TEXT)]]

        self.pages = pages
        self.current_page = 0
        self.messages = self.pages[0]
        self.waiting_for_more = len(self.pages) > 1

        if self.waiting_for_more:
            self.choice_menu = None
        else:
            self.update_choices()

    def next_page(self):
        self.current_page += 1

        if self.current_page < len(self.pages):
            self.messages = self.pages[self.current_page]
            self.waiting_for_more = self.current_page < len(self.pages) - 1

            if not self.waiting_for_more:
                self.update_choices()
        else:
            self.waiting_for_more = False
            self.update_choices()

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

    def update_choices(self):
        if self.game_over:
            self.choice_menu = ChoiceMenu([
                ("Restart", self.restart),
                ("Quit", self.quit_game),
            ])
            return

        room = self.rooms[self.location]
        choices = []

        if self.location == "dorm":
            choices.append(("Read Essay", lambda: self.look_at("essay")))
            choices.append(("Read Sewanee Purple", lambda: self.look_at("sewanee purple")))

        for direction in room["exits"]:
            choices.append((f"Go {direction.title()}", lambda d=direction: self.go(d)))

        for item in room["items"]:
            choices.append((f"Take {item.title()}", lambda item=item: self.take(item)))

        if self.location == "chapel" and not self.door_unlocked:
            choices.append(("Unlock Door", lambda: self.unlock("door")))

        choices.append(("Look Around", self.describe_room))
        self.choice_menu = ChoiceMenu(choices)

    def handle_event(self, event):
        if self.waiting_for_more:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.next_page()
            return

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_scene(TitleScene(self.game))
            return

        if self.choice_menu:
            self.choice_menu.handle_event(event)

    def look_at(self, thing):
        if self.location != "dorm":
            self.set_text([
                ("You don't see that here.", Theme.ERROR),
                "Those documents are back in your dorm room.",
            ])
            return

        if thing == "essay":
            self.set_text([("History 101 Essay", Theme.ACCENT), ESSAY_TEXT])
        elif thing == "sewanee purple":
            self.set_text([("The Sewanee Purple", Theme.ACCENT), PURPLE_TEXT])

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

    def unlock(self, thing):
        if self.location == "chapel" and thing == "door":
            if "key" in self.inventory:
                self.game.audio.play_sound("unlock")
                self.door_unlocked = True

                if "robe" not in self.rooms["chapel"]["items"] and "robe" not in self.inventory:
                    self.rooms["chapel"]["items"].append("robe")

                self.set_text([
                    ("The key turns.", Theme.ACCENT),
                    UNLOCK_TEXT,
                    ("You see here: robe", Theme.MUTED),
                ])
            else:
                self.set_text([
                    ("The door is locked.", Theme.ERROR),
                    "You will need something that can open it.",
                ])
        else:
            self.set_text([
                ("You can't unlock that.", Theme.ERROR),
                "There is nothing here that responds to that command.",
            ])

    def win_game(self):
        self.game_over = True
        self.game.audio.stop_music()
        self.game.audio.play_sound("win")
        self.set_text([
            ("You are now the 19th Vice-Chancellor of the University of the South.", Theme.ACCENT),
            WIN_TEXT,
            ("Choose Restart or Quit from the side panel.", Theme.MUTED),
        ])

    def draw(self, screen):
        draw_background(screen)
        draw_panel(screen, pygame.Rect(28, 28, 604, 560), "Story")
        draw_panel(screen, pygame.Rect(652, 28, 280, 560), "Choices")

        y = 70
        line_height = self.game.font.get_height() + 5

        for message, color in self.messages:
            if message == "":
                y += self.game.font.get_height()
            else:
                draw_text(screen, self.game.font, message, 54, y, color)
                y += line_height

        if self.choice_menu:
            self.choice_menu.draw(screen, self.game.small_font, 674, 76, 236)

        if self.waiting_for_more:
            draw_text(screen, self.game.small_font, "[Press Space or Enter for more]", 330, 560, Theme.ACCENT)
        else:
            draw_text(screen, self.game.tiny_font, "Up/Down or W/S: move   Enter/Space: choose   Esc: title screen", 54, 594, Theme.MUTED)
