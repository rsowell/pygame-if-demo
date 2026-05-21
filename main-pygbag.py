import asyncio
import os
from pathlib import Path

# Helps avoid some Linux/VM/OpenGL driver issues.
os.environ.setdefault("SDL_RENDER_DRIVER", "software")

import pygame

# Keep this fixed logical resolution for both local Python and pygbag/web.
# Changing this affects text wrapping, pagination, and browser canvas size.
WIDTH, HEIGHT = 960, 640
FPS = 60


def asset_path(*parts):
    """Return a path that works locally and with pygbag."""
    return str(Path("assets", *parts))


def load_font(filename, size, fallback_name=None, bold=False):
    """Load a bundled font if available; otherwise fall back safely.

    For the most consistent local/web appearance, place .ttf files in:
        assets/fonts/

    Suggested files:
        assets/fonts/LibreBaskerville-Regular.ttf
        assets/fonts/LibreBaskerville-Bold.ttf
    """
    path = Path(asset_path("fonts", filename))

    if path.exists():
        return pygame.font.Font(str(path), size)

    print(f"Font warning: could not load fonts/{filename}; using fallback font.")
    return pygame.font.SysFont(fallback_name, size, bold=bold)


def menu_label_font():
    """Small label font for panel tabs."""
    return load_font("LibreBaskerville-Regular.ttf", 16, fallback_name="georgia")


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
    """Keyboard-navigable vertical choice menu.

    This class should NOT know anything about pagination.
    It only knows choices and selection.
    """

    def __init__(self, choices):
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

            prefix = "> " if selected else "  "
            draw_text(screen, font, prefix + label, rect.x + 12, rect.y + 8, Theme.TEXT)


class Scene:
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
    DORM_TEXT = """It’s 2 AM, and you awaken from uneasy dreams. The room is empty, your roommate having left early for Christmas Break, and you’re grateful no one is around to hear the strange squeaking sound of panic you made when you opened your eyes.

You take a sip of water and get out of bed. Your desk is buried under papers and notebooks, but at the top is your latest essay from your History 101 course and the latest copy of The Sewanee Purple.

Underneath these two documents, you see a brass key, which glints from the moonlight coming through the window."""

    ESSAY_TEXT = """Your final paper for History 101 (The Domain and Beyond) was about the tragic fates of previous Vice-Chancellors, and your thesis asserted that every fourth Vice-Chancellor falls victim to what is known in the Appalachian Region as a Mimic, which uses the familiar voice of loved ones past and present to lure people to their doom. The professor’s comments cover many of the pages, and his final statement says, “I cannot give this a passing grade, Eleanor, as half of this essay consists of your own personal stories of hearing the voices of your parents and siblings on the domain. I am filing a CARE report and ask that you meet with me before break.”"""

    PURPLE_TEXT = """The headline on the student newspaper reads “Vice Chancellor Still Missing After 45 Days. Trustees to Hold Emergency Meeting to Determine Course of Action.”"""

    QUAD_TEXT = """The campus is quiet, most students either asleep or already on their way home. A wind moves through the trees like whispered stage directions. It was here that you first heard the voice of the Mimic.

Earlier that day, three months previous, in McClurg, while eating in one of the nooks hidden from the main dining area, you heard your roommate and her friends talking about you, how pronounced your southern accent was, the weird t-shirts you wore for punk bands they’d never heard of, how you always smelled like pine tar because of the giant black brick of homemade soap you used. You had to wait until they took their trays back to the kitchen in order to sneak out, your food untouched. You walked to the quad, students and faculty moving in all directions when you distinctly heard the voice of your best friend from high school, Cullen, say, “Why would you wanna be friends with anyone who didn’t know any songs by the Hospital Bombers or Satan Helpers? Why not come back to Coalfield? In fact, if you can get to the interstate, I’ll pick you up.”

Now, in the moonlight, the absence of sound, you try to listen for the voices of Cullen or your mother, sick with cancer and telling you she might get better if you just dropped out and came home. But there’s nothing, just you, holding this key.

And then you hear it, the carillon, the sound of bells coming from the chapel. And, underneath that, a voice, whispering, “We are assembled to commemorate the wisdom and virtue of the great men, who, years ago, laid the cornerstone of this University. And it is fitting that this fragment of the original corner stone, destroyed during the Civil War, should be placed here in the wall of our chapel, as a perpetual memorial of our Founders and a challenge to succeeding generations.”

“Hello?” you ask, but the voice fades out, and all you can hear is the carillon."""

    CHAPEL_TEXT = """Candles flicker along the stone walls, the entire chapel empty except for you. As you follow the sound of the music, you step onto the altar, where you see a locked door at the furthest edge of the chapel."""

    UNLOCK_TEXT = """The key turns. The door opens onto a man in an ermine cape playing the carillon. His hair is an unnatural shade of silver and he is smiling at you. It is the Vice-Chancellor, the one who, at the signing of the Honor Code, seemed to be looking directly at you as he said, “If Sewanee is truly your home, you will know it in your bones,” You felt nothing in your bones on that day, but you vowed that you would not leave, would not quit, until you did. You think you feel it right now, at this very moment.

He says, "Tu vincis" and takes off the robe. As he holds it out for you, his body disintegrates, turns to smoke, and the ermine robe falls to the floor."""

    WIN_TEXT = """The bells continuing ringing long after the smoke clears. You wrap the ermine robe around your shoulders and you head back across the quad, to your dorm room, to rewrite your essay, to prove to your teacher that you belong here, that you know what you are talking about, that you can feel it in your bones."""

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
                "description": self.DORM_TEXT,
                "exits": {"east": "quad"},
                "items": ["key"],
            },
            "quad": {
                "name": "The Moonlit Quad",
                "description": self.QUAD_TEXT,
                "exits": {"west": "dorm", "north": "chapel"},
                "items": [],
            },
            "chapel": {
                "name": "The Chapel",
                "description": self.CHAPEL_TEXT,
                "exits": {"south": "quad"},
                "items": [],
            },
        }

    def on_enter(self):
        self.game.audio.play_music("ambient_chapel.ogg")
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

        # Calculate how many lines actually fit in the story panel.
        # This keeps pagination correct even if the font changes.
        story_top = 70
        story_bottom = 532  # leave room for the "[Press Space...]" prompt
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
        # Pagination belongs here, not in ChoiceMenu.
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
            self.set_text([
                ("History 101 Essay", Theme.ACCENT),
                self.ESSAY_TEXT,
            ])
        elif thing == "sewanee purple":
            self.set_text([
                ("The Sewanee Purple", Theme.ACCENT),
                self.PURPLE_TEXT,
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
                    self.UNLOCK_TEXT,
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
            self.WIN_TEXT,
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


class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.menu = ChoiceMenu([
            ("Start Demo", lambda: self.game.change_scene(DialogueScene(self.game))),
            ("Quit", self.quit_game),
        ])

    def quit_game(self):
        self.game.running = False

    def handle_event(self, event):
        self.menu.handle_event(event)

    def draw(self, screen):
        draw_background(screen)
        draw_panel(screen, pygame.Rect(150, 120, 660, 390), None)
        draw_text(screen, self.game.title_font, "Designing Worlds", 248, 194, Theme.ACCENT)
        draw_text(screen, self.game.font, "A Pygame framework for text-driven games", 268, 258, Theme.TEXT)
        draw_text(screen, self.game.small_font,"Use arrows/WASD to move through choices.",270,300,Theme.MUTED,)
        draw_text(screen,self.game.small_font,"Press Enter or Space to select.",325,330,Theme.MUTED,)
        self.menu.draw(screen, self.game.font, 330, 366, 300)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Designing Worlds Starter")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Use bundled fonts for consistent appearance locally and on the web.
        # Put these files in assets/fonts/:
        #   LibreBaskerville-Regular.ttf
        #   LibreBaskerville-Bold.ttf
        self.font = load_font("LibreBaskerville-Regular.ttf", 23, fallback_name="georgia")
        self.small_font = load_font("LibreBaskerville-Regular.ttf", 19, fallback_name="georgia")
        self.tiny_font = load_font("LibreBaskerville-Regular.ttf", 16, fallback_name="georgia")
        self.title_font = load_font("LibreBaskerville-Bold.ttf", 52, fallback_name="georgia", bold=True)

        self.audio = AudioManager()
        self.audio.load_sound("pickup", "pickup.ogg")
        self.audio.load_sound("unlock", "unlock.ogg")
        self.audio.load_sound("move", "move.ogg")
        self.audio.load_sound("win", "win.ogg")

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
        draw_text(screen, menu_label_font(), title, label_rect.x + 12, label_rect.y + 3, Theme.MUTED)


def draw_text(screen, font, text, x, y, color=Theme.TEXT):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
