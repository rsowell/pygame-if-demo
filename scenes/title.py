import pygame
from rendering import draw_background, draw_panel, draw_text
from scenes.base import Scene
from theme import Theme
from ui import ChoiceMenu


class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        from scenes.dialogue import DialogueScene

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

        draw_text(screen, self.game.title_font, "Designing Worlds", 248, 170, Theme.ACCENT)
        draw_text(screen, self.game.font, "A Pygame framework for text-driven games", 268, 245, Theme.TEXT)
        draw_text(screen, self.game.small_font, "Use arrows/WASD to move through choices.", 270, 310, Theme.MUTED)
        draw_text(screen, self.game.small_font, "Press Enter or Space to select.", 325, 340, Theme.MUTED)

        self.menu.draw(screen, self.game.font, 330, 400, 300)
