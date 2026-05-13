import asyncio
import pygame

WIDTH, HEIGHT = 900, 600
FPS = 60

ROOMS = {
    "dorm": {
        "name": "Your Dorm Room",
        "description": "Your desk is buried under notebooks. A brass key glints beneath a syllabus.",
        "exits": {"east": "quad"},
        "items": ["key"],
    },
    "quad": {
        "name": "The Moonlit Quad",
        "description": "The campus is quiet. Music drifts from the chapel. Paths lead west and north.",
        "exits": {"west": "dorm", "north": "chapel"},
        "items": [],
    },
    "chapel": {
        "name": "The Chapel",
        "description": "Candles flicker. A locked door waits behind the altar.",
        "exits": {"south": "quad"},
        "items": [],
    },
}


class Game:
    def __init__(self):
        pygame.init()

        self.audio_enabled = True
        self.pickup_sound = None
        self.unlock_sound = None

        try:
            pygame.mixer.init()
            pygame.mixer.music.load("assets/ambient_chapel.ogg")
            pygame.mixer.music.play(-1)
            self.pickup_sound = pygame.mixer.Sound("assets/pickup.ogg")
            self.unlock_sound = pygame.mixer.Sound("assets/unlock.ogg")
        except Exception as e:
            # This keeps the game playable if audio files are missing or
            # if the browser blocks audio before the first user interaction.
            self.audio_enabled = False
            print("Audio disabled:", e)

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Designing Worlds: IF Demo")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 22)

        self.location = "dorm"
        self.inventory = []
        self.input_text = ""
        self.messages = []
        self.running = True

        self.write("Designing Worlds: A Tiny IF Demo")
        self.write("Type help for commands.")
        if not self.audio_enabled:
            self.write("Audio is currently unavailable. The game will still run.")
        self.describe_room()

    def play_sound(self, sound):
        if self.audio_enabled and sound is not None:
            sound.play()

    def write(self, text):
        self.messages.append(text)
        self.messages = self.messages[-16:]

    def describe_room(self):
        room = ROOMS[self.location]
        self.write("")
        self.write(room["name"])
        self.write(room["description"])

        if room["items"]:
            self.write("You see here: " + ", ".join(room["items"]))

        self.write("Exits: " + ", ".join(room["exits"].keys()))

    def handle_command(self, command):
        command = command.strip().lower()
        if not command:
            return

        self.write(f"> {command}")

        words = command.split()
        verb = words[0]
        noun = " ".join(words[1:]) if len(words) > 1 else ""

        if verb in ["help", "?"]:
            self.write("Commands: look, go east, take key, inventory, unlock door, quit")

        elif verb in ["look", "l"]:
            self.describe_room()

        elif verb in ["inventory", "i"]:
            if self.inventory:
                self.write("You are carrying: " + ", ".join(self.inventory))
            else:
                self.write("You are carrying nothing.")

        elif verb in ["go", "walk", "move"]:
            self.go(noun)

        elif verb in ["north", "south", "east", "west"]:
            self.go(verb)

        elif verb in ["take", "get"]:
            self.take(noun)

        elif verb == "unlock":
            self.unlock(noun)

        elif verb == "quit":
            self.write("Thanks for playing.")
            self.running = False

        else:
            self.write("I don't understand that command.")

    def go(self, direction):
        room = ROOMS[self.location]

        if direction in room["exits"]:
            self.location = room["exits"][direction]
            self.describe_room()
        else:
            self.write("You can't go that way.")

    def take(self, item):
        room = ROOMS[self.location]

        if item in room["items"]:
            self.play_sound(self.pickup_sound)
            room["items"].remove(item)
            self.inventory.append(item)
            self.write(f"You take the {item}.")
        else:
            self.write("You don't see that here.")

    def unlock(self, thing):
        if self.location == "chapel" and thing == "door":
            if "key" in self.inventory:
                self.play_sound(self.unlock_sound)
                self.write("The key turns. The door opens onto a room full of music.")
                self.write("You win.")
            else:
                self.write("The door is locked.")
        else:
            self.write("You can't unlock that.")

    def draw_text_wrapped(self, text, x, y, max_width, font):
        words = text.split()
        line = ""

        for word in words:
            test_line = line + word + " "
            if font.size(test_line)[0] <= max_width:
                line = test_line
            else:
                self.draw_text(line, x, y, font)
                y += font.get_height() + 4
                line = word + " "

        if line:
            self.draw_text(line, x, y, font)
            y += font.get_height() + 4

        return y

    def draw_text(self, text, x, y, font):
        surface = font.render(text, True, "white")
        self.screen.blit(surface, (x, y))

    def draw(self):
        self.screen.fill((20, 20, 30))

        pygame.draw.rect(self.screen, (40, 40, 60), (20, 20, WIDTH - 40, HEIGHT - 100))
        pygame.draw.rect(self.screen, (80, 80, 120), (20, 20, WIDTH - 40, HEIGHT - 100), 2)

        pygame.draw.rect(self.screen, (30, 30, 45), (20, HEIGHT - 70, WIDTH - 40, 50))
        pygame.draw.rect(self.screen, (120, 120, 180), (20, HEIGHT - 70, WIDTH - 40, 50), 2)

        y = 40
        for message in self.messages:
            y = self.draw_text_wrapped(message, 40, y, WIDTH - 80, self.font)

        self.draw_text("> " + self.input_text, 40, HEIGHT - 55, self.font)

        pygame.display.flip()

    async def run(self):
        while self.running:
            self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.handle_command(self.input_text)
                        self.input_text = ""

                    elif event.key == pygame.K_BACKSPACE:
                        self.input_text = self.input_text[:-1]

                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                    else:
                        self.input_text += event.unicode

            self.draw()

            # Required by pygbag / pygame-wasm so the browser can breathe.
            await asyncio.sleep(0)


async def main():
    game = Game()
    await game.run()


if __name__ == "__main__":
    asyncio.run(main())
