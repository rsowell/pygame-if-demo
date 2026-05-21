import pygame
from rendering import draw_text
from theme import Theme


class ChoiceMenu:
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
