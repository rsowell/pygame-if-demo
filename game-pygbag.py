import asyncio
import pygame
from audio import AudioManager
from fonts import load_font
from scenes.title import TitleScene
from settings import FPS, HEIGHT, WIDTH


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Designing Worlds Starter")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

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
