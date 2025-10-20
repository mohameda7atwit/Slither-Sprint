import pygame
import random
from constants import *

# Initialize Pygame
pygame.init()

# Fonts
font = pygame.font.SysFont(None, 55)
small_font = pygame.font.SysFont(None, 35)

class Game:
    def __init__(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.snake_direction = (CELL_SIZE, 0)
        self.food = self.spawn_food()
        self.score = 0

    def draw_snake(self, screen):
        for segment in self.snake:
            pygame.draw.rect(screen, GREEN, (*segment, CELL_SIZE, CELL_SIZE))

    def draw_food(self, screen):
        pygame.draw.rect(screen, RED, (*self.food, CELL_SIZE, CELL_SIZE))

    def move_snake(self):
        # Calculate new head position
        new_head = (self.snake[0][0] + self.snake_direction[0], self.snake[0][1] + self.snake_direction[1])

        # Wrap around the screen
        new_head = (
            new_head[0] % WIDTH,  
            new_head[1] % HEIGHT  
        )

        # Insert new head and remove tail
        self.snake.insert(0, new_head)
        self.snake.pop()

    def check_collision(self):
        # Check if snake eats food
        if self.snake[0] == self.food:
            return True
        return False

    def spawn_food(self):
        return (
            random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
            random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
        )

    def reset(self):
        self.snake = [(100, 100), (80, 100), (60, 100)]
        self.snake_direction = (CELL_SIZE, 0)
        self.food = self.spawn_food()
        self.score = 0