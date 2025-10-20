import pygame
from constants import *
from game_logic import small_font
from game_logic import font

def draw_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def home_screen(screen):
    screen.fill(BLACK)
    draw_text(screen, "Snake Game", font, GREEN, WIDTH // 2 - 120, HEIGHT // 2 - 100)
    draw_text(screen, "1. Classic Mode", small_font, WHITE, WIDTH // 2 - 100, HEIGHT // 2 - 20)
    draw_text(screen, "Press 1 to Start", small_font, WHITE, WIDTH // 2 - 120, HEIGHT // 2 + 60)
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return CLASSIC_MODE
               