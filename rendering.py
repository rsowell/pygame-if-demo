import pygame
from fonts import menu_label_font
from theme import Theme


def draw_background(screen):
    screen.fill(Theme.BG)
    stars = [(90, 80), (180, 48), (320, 96), (760, 80), (860, 155), (105, 500), (810, 540)]
    for x, y in stars:
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
