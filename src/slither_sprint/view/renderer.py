"""
Renderer - handles all drawing operations
"""

import pygame
from config import (
    WIDTH,
    HEIGHT,
    CELL,
    GRID_H,
    PANE_COLS,
    BG_COLOR,
    DIVIDER_COLOR,
    TEXT_COLOR,
    PADDING,
    RED_APPLE_COLOR,
    GOLDEN_APPLE_COLOR,
    OBSTACLE_A,
    OBSTACLE_B,
    FINISH_LINE_COLOR,
    P1_HEAD,
    P2_HEAD,
)
from settings import COLOR_PRESETS
from model.power_up import PowerUpType


class Renderer:
    """Handles all rendering operations"""

    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("consolas", 18)
        # Larger fonts for titles and game-over banner
        self.title_font = pygame.font.SysFont("consolas", 54)
        self.banner_sub_font = pygame.font.SysFont("consolas", 28)

        # Create clip rectangles for split screen
        self.clip_p1 = pygame.Rect(0, 0, PANE_COLS * CELL, HEIGHT)
        self.clip_p2 = pygame.Rect(PANE_COLS * CELL, 0, PANE_COLS * CELL, HEIGHT)

        # UI rectangles used for mouse interaction, updated each frame
        self.start_button_rect = None
        self.customize_button_rect = None
        self.custom_save_button_rect = None
        self.custom_cancel_button_rect = None
        self.p1_palette_rects = []
        self.p2_palette_rects = []
        self.mute_button_rect = None
        self.p1_name_rect = None
        self.p2_name_rect = None

    def render(
        self,
        game_state,
        fps: float = 0.0,
        in_start_menu: bool = False,
        in_customize_menu: bool = False,
        customize_state=None,
        is_muted: bool = False,
    ):
        """
        Render the complete game state

        Args:
            game_state: GameState object containing all game data
        """
        self.screen.fill(BG_COLOR)

        # Menus overlay everything else
        if in_customize_menu and customize_state is not None:
            colors = customize_state
            self._draw_customize_screen(colors, fps, is_muted)
            pygame.display.flip()
            return

        if in_start_menu:
            self._draw_start_screen(fps, is_muted)
            pygame.display.flip()
            return

        # Draw Player 1's view
        self.screen.set_clip(self.clip_p1)
        self._draw_finish_line(game_state.camera_y_p1, self.clip_p1)
        self._draw_obstacles(game_state.obstacles, game_state.camera_y_p1, self.clip_p1)
        self._draw_apples_for_pane(
            game_state.apples, game_state.pane1, game_state.camera_y_p1, self.clip_p1
        )
        self._draw_snake(game_state.snake1, game_state.camera_y_p1, self.clip_p1)

        # Draw Player 2's view
        self.screen.set_clip(self.clip_p2)
        self._draw_finish_line(game_state.camera_y_p2, self.clip_p2)
        self._draw_obstacles(game_state.obstacles, game_state.camera_y_p2, self.clip_p2)
        self._draw_apples_for_pane(
            game_state.apples, game_state.pane2, game_state.camera_y_p2, self.clip_p2
        )
        self._draw_snake(game_state.snake2, game_state.camera_y_p2, self.clip_p2)

        # Draw divider and HUD without clipping
        self.screen.set_clip(None)
        pygame.draw.rect(
            self.screen, DIVIDER_COLOR, pygame.Rect(PANE_COLS * CELL - 2, 0, 4, HEIGHT)
        )
        self._draw_hud(
            game_state.snake1,
            game_state.snake2,
            game_state.winner_text,
            fps=fps,
            is_muted=is_muted,
        )

        pygame.display.flip()

    def _draw_start_screen(self, fps: float = 0.0, is_muted: bool = False):
        """Draw the start screen with title and start button/prompt"""
        title_text = "Slither Sprint"
        subtitle_text = "Two-player vertical snake racing"
        button_text = "Start (SPACE / ENTER)"
        customize_text = "Customize Colors (C)"

        # Title
        title_surface = self.title_font.render(title_text, True, TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        self.screen.blit(title_surface, title_rect)

        # Subtitle
        subtitle_surface = self.font.render(subtitle_text, True, TEXT_COLOR)
        subtitle_rect = subtitle_surface.get_rect(
            center=(WIDTH // 2, title_rect.bottom + 30)
        )
        self.screen.blit(subtitle_surface, subtitle_rect)

        # Layout two stacked buttons in the center area
        button_width, button_height = 360, 70
        spacing = 20
        top_y = HEIGHT // 2 - button_height - spacing // 2

        # Start button
        start_rect = pygame.Rect(
            WIDTH // 2 - button_width // 2,
            top_y,
            button_width,
            button_height,
        )
        self.start_button_rect = start_rect
        pygame.draw.rect(self.screen, DIVIDER_COLOR, start_rect, border_radius=10)
        inner_rect = start_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, BG_COLOR, inner_rect, border_radius=8)

        start_surface = self.font.render(button_text, True, TEXT_COLOR)
        start_text_rect = start_surface.get_rect(center=start_rect.center)
        self.screen.blit(start_surface, start_text_rect)

        # Customize button just below
        custom_rect = pygame.Rect(
            WIDTH // 2 - button_width // 2,
            top_y + button_height + spacing,
            button_width,
            button_height,
        )
        self.customize_button_rect = custom_rect
        pygame.draw.rect(self.screen, DIVIDER_COLOR, custom_rect, border_radius=10)
        inner_rect2 = custom_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, BG_COLOR, inner_rect2, border_radius=8)

        custom_surface = self.font.render(customize_text, True, TEXT_COLOR)
        custom_text_rect = custom_surface.get_rect(center=custom_rect.center)
        self.screen.blit(custom_surface, custom_text_rect)

        # Mute button
        self._draw_mute_button(is_muted)

        # FPS counter in corner (useful during development)
        if fps:
            fps_text = self.font.render(f"{fps:05.1f} FPS", True, TEXT_COLOR)
            self.screen.blit(fps_text, (10, 10))

    def _draw_customize_screen(
        self, colors, fps: float = 0.0, is_muted: bool = False
    ):
        """Draw the player color customization screen for both players."""
        # Reset button / palette rects each frame; they will be re-created below
        self.custom_save_button_rect = None
        self.custom_cancel_button_rect = None
        self.p1_palette_rects = []
        self.p2_palette_rects = []
        self.p1_name_rect = None
        self.p2_name_rect = None

        # Title
        title_surface = self.title_font.render("Player Colors", True, TEXT_COLOR)
        title_rect = title_surface.get_rect(center=(WIDTH // 2, HEIGHT // 8))
        self.screen.blit(title_surface, title_rect)

        # Layout for two columns: Player 1 (left) and Player 2 (right)
        center_y = HEIGHT // 2 - CELL
        col_x_offsets = [WIDTH // 4, 3 * WIDTH // 4]
        keys = ["P1", "P2"]
        labels = ["Player 1", "Player 2"]

        for idx, (cx, key, label) in enumerate(zip(col_x_offsets, keys, labels)):
            body_col = colors[key]["body"]
            head_col = colors[key]["head"]
            player_name = str(colors[key].get("name", key))[:16]

            # Player label
            label_surface = self.font.render(label, True, TEXT_COLOR)
            label_rect = label_surface.get_rect(center=(cx, center_y - 70))
            self.screen.blit(label_surface, label_rect)

            # Preview snake
            start_x = cx - 3 * CELL
            head_rect = pygame.Rect(start_x, center_y - CELL // 2, CELL, CELL)
            pygame.draw.rect(self.screen, head_col, head_rect, border_radius=6)
            for i in range(1, 5):
                body_rect = pygame.Rect(
                    start_x + i * (CELL + 4), center_y - CELL // 2, CELL, CELL
                )
                pygame.draw.rect(self.screen, body_col, body_rect, border_radius=4)

            # Color palette swatches under the preview
            palette_y = center_y + CELL
            swatch_size = CELL
            margin = 6
            total_width = len(COLOR_PRESETS) * (swatch_size + margin) - margin
            start_px = cx - total_width // 2

            rects_list = self.p1_palette_rects if key == "P1" else self.p2_palette_rects
            rects_list.clear()

            for i, (body_preset, head_preset) in enumerate(COLOR_PRESETS):
                r = pygame.Rect(
                    start_px + i * (swatch_size + margin),
                    palette_y,
                    swatch_size,
                    swatch_size,
                )
                rects_list.append(r)
                # Draw border and fill with body color, small head color dot
                pygame.draw.rect(self.screen, DIVIDER_COLOR, r, border_radius=4)
                inner = r.inflate(-4, -4)
                pygame.draw.rect(self.screen, body_preset, inner, border_radius=4)
                dot_radius = max(3, swatch_size // 5)
                pygame.draw.circle(
                    self.screen,
                    head_preset,
                    (inner.centerx, inner.centery),
                    dot_radius,
                )

        # Instructions text above buttons
        instr_lines = [
            "Keyboard: A/D to change Player 1, LEFT/RIGHT to change Player 2",
            "Mouse: click a color for each player, then use buttons below",
        ]
        for i, text in enumerate(instr_lines):
            surf = self.font.render(text, True, TEXT_COLOR)
            self.screen.blit(
                surf,
                (WIDTH // 2 - surf.get_width() // 2, title_rect.bottom + 40 + i * 24),
            )

        # Name inputs below palettes
        name_box_width = 180
        name_box_height = 30
        name_y = palette_y + swatch_size + 20
        for cx, key, label in zip(col_x_offsets, keys, labels):
            player_name = str(colors[key].get("name", key))[:16]
            input_rect = pygame.Rect(
                cx - name_box_width // 2,
                name_y,
                name_box_width,
                name_box_height,
            )
            if key == "P1":
                self.p1_name_rect = input_rect
            else:
                self.p2_name_rect = input_rect

            pygame.draw.rect(self.screen, DIVIDER_COLOR, input_rect, border_radius=6)
            inner = input_rect.inflate(-4, -4)
            pygame.draw.rect(self.screen, BG_COLOR, inner, border_radius=6)

            name_surf = self.font.render(player_name, True, TEXT_COLOR)
            name_rect = name_surf.get_rect(center=inner.center)
            self.screen.blit(name_surf, name_rect)

        # Save / Cancel buttons placed further down
        button_width, button_height = 220, 60
        spacing = 40
        buttons_y = name_y + name_box_height + 40

        # Save button (left)
        save_rect = pygame.Rect(
            WIDTH // 2 - button_width - spacing // 2,
            buttons_y,
            button_width,
            button_height,
        )
        self.custom_save_button_rect = save_rect
        pygame.draw.rect(self.screen, DIVIDER_COLOR, save_rect, border_radius=10)
        save_inner = save_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, BG_COLOR, save_inner, border_radius=8)
        save_surface = self.font.render("Save & Back", True, TEXT_COLOR)
        save_text_rect = save_surface.get_rect(center=save_rect.center)
        self.screen.blit(save_surface, save_text_rect)

        # Cancel button (right)
        cancel_rect = pygame.Rect(
            WIDTH // 2 + spacing // 2,
            buttons_y,
            button_width,
            button_height,
        )
        self.custom_cancel_button_rect = cancel_rect
        pygame.draw.rect(self.screen, DIVIDER_COLOR, cancel_rect, border_radius=10)
        cancel_inner = cancel_rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, BG_COLOR, cancel_inner, border_radius=8)
        cancel_surface = self.font.render("Cancel", True, TEXT_COLOR)
        cancel_text_rect = cancel_surface.get_rect(center=cancel_rect.center)
        self.screen.blit(cancel_surface, cancel_text_rect)

        # Mute button
        self._draw_mute_button(is_muted)

        if fps:
            fps_text = self.font.render(f"{fps:05.1f} FPS", True, TEXT_COLOR)
            self.screen.blit(fps_text, (10, 10))

    def _draw_snake(self, snake, camera_y, clip_rect):
        """Draw a snake"""
        for i, (x, y) in enumerate(snake.body):
            screen_y = y - camera_y
            if -1 <= screen_y <= GRID_H:
                col = snake.head_col if i == 0 else snake.body_col

                # Add glow effect if invincible
                if snake.is_invincible() and i == 0:
                    glow_rect = pygame.Rect(
                        x * CELL - 2, screen_y * CELL - 2, CELL + 4, CELL + 4
                    )
                    if clip_rect is None or glow_rect.colliderect(clip_rect):
                        pygame.draw.rect(
                            self.screen, (255, 255, 200), glow_rect, border_radius=6
                        )

                r = pygame.Rect(
                    x * CELL + PADDING,
                    screen_y * CELL + PADDING,
                    CELL - 2 * PADDING,
                    CELL - 2 * PADDING,
                )
                if clip_rect is None or r.colliderect(clip_rect):
                    pygame.draw.rect(self.screen, col, r, border_radius=4)

    def _draw_apples_for_pane(self, apples, pane, camera_y, clip_rect):
        """Draw apples that belong to a specific pane"""
        for apple in apples:
            if pane.inside(apple.x):
                self._draw_apple(apple, camera_y, clip_rect)

    def _draw_apple(self, apple, camera_y, clip_rect):
        """Draw an apple"""
        screen_y = apple.y - camera_y
        if -1 <= screen_y <= GRID_H:
            color = GOLDEN_APPLE_COLOR if apple.is_golden else RED_APPLE_COLOR
            center_x = apple.x * CELL + CELL // 2
            center_y = int(screen_y * CELL + CELL // 2)

            if clip_rect is None or clip_rect.collidepoint(center_x, center_y):
                radius = int((CELL // 2 - 3) * 1.5)
                pygame.draw.circle(self.screen, color, (center_x, center_y), radius)

                # Add shine effect
                shine_offset = radius // 3
                pygame.draw.circle(
                    self.screen,
                    (255, 255, 255),
                    (center_x - shine_offset, center_y - shine_offset),
                    radius // 3,
                )

    def _draw_obstacles(self, obstacles, camera_y, clip_rect):
        """Draw obstacles"""
        for x, y in obstacles.blocks:
            screen_y = y - camera_y
            if -1 <= screen_y <= GRID_H:
                size = int((CELL - 4) * 1.15)
                offset = (CELL - size) // 2
                r = pygame.Rect(x * CELL + offset, screen_y * CELL + offset, size, size)
                if clip_rect is None or r.colliderect(clip_rect):
                    pygame.draw.rect(self.screen, OBSTACLE_A, r, border_radius=4)
                    pygame.draw.rect(
                        self.screen, OBSTACLE_B, r.inflate(-6, -6), border_radius=3
                    )

    def _draw_finish_line(self, camera_y, clip_rect):
        """Draw the finish line"""
        from config import FINISH_LINE_DISTANCE

        screen_y = FINISH_LINE_DISTANCE - camera_y
        if -5 <= screen_y <= GRID_H + 5:
            y_pixel = int(screen_y * CELL)
            # Draw checkered pattern
            for x in range(0, WIDTH, CELL):
                r = pygame.Rect(x, y_pixel, CELL, CELL // 2)
                if clip_rect is None or r.colliderect(clip_rect):
                    color = (
                        FINISH_LINE_COLOR if (x // CELL) % 2 == 0 else (200, 200, 50)
                    )
                    pygame.draw.rect(self.screen, color, r)

    def _draw_hud(self, snake1, snake2, winner_text, fps=0.0, is_muted: bool = False):
        """Draw the heads-up display"""
        # Player 1 info
        p1_text = f"{snake1.name}: {snake1.apples_collected} apples"
        if snake1.active_powerup == PowerUpType.SPEED_BOOST:
            p1_text += " [SPEED]"
        elif snake1.active_powerup == PowerUpType.INVINCIBILITY:
            p1_text += " [INVINCIBLE]"
        img1 = self.font.render(p1_text, True, P1_HEAD)
        self.screen.blit(img1, (12, 10))

        # Player 2 info
        p2_text = f"{snake2.name}: {snake2.apples_collected} apples"
        if snake2.active_powerup == PowerUpType.SPEED_BOOST:
            p2_text += " [SPEED]"
        elif snake2.active_powerup == PowerUpType.INVINCIBILITY:
            p2_text += " [INVINCIBLE]"
        img2 = self.font.render(p2_text, True, P2_HEAD)
        self.screen.blit(img2, (WIDTH - img2.get_width() - 12, 10))

        # Controls
        controls = self.font.render(
            "P1: A/D   P2: ◀/▶   R: restart   ESC: quit", True, TEXT_COLOR
        )
        self.screen.blit(controls, (12, HEIGHT - 30))

        # FPS counter
        fps_text = self.font.render(f"{fps:05.1f} FPS", True, TEXT_COLOR)
        fps_pos = (
            WIDTH // 2 - fps_text.get_width() // 2,
            10,
        )
        self.screen.blit(fps_text, fps_pos)

        # Mute button (bottom-right)
        self._draw_mute_button(is_muted)

        # Big game-over text in the middle when someone wins or it's a draw
        if winner_text:
            # First line: GAME OVER
            main_text = "GAME OVER"
            main_surf = self.title_font.render(main_text, True, TEXT_COLOR)
            main_rect = main_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))

            # Second line: winner / draw text
            sub_text = winner_text.upper()
            sub_surf = self.banner_sub_font.render(sub_text, True, TEXT_COLOR)
            sub_rect = sub_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))

            # Background box covering both lines
            union_rect = main_rect.union(sub_rect).inflate(40, 20)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), union_rect)

            self.screen.blit(main_surf, main_rect)
            self.screen.blit(sub_surf, sub_rect)

    def _draw_mute_button(self, is_muted: bool):
        """Draw a small mute/unmute button in the bottom-right corner."""
        label = "Unmute (M)" if is_muted else "Mute (M)"
        padding = 8
        text_surf = self.font.render(label, True, TEXT_COLOR)
        rect = text_surf.get_rect()
        rect.width += padding * 2
        rect.height += padding * 2
        rect.bottomright = (WIDTH - 10, HEIGHT - 10)

        self.mute_button_rect = rect
        pygame.draw.rect(self.screen, DIVIDER_COLOR, rect, border_radius=6)
        inner = rect.inflate(-4, -4)
        pygame.draw.rect(self.screen, BG_COLOR, inner, border_radius=6)

        text_pos = (
            inner.x + (inner.width - text_surf.get_width()) // 2,
            inner.y + (inner.height - text_surf.get_height()) // 2,
        )
        self.screen.blit(text_surf, text_pos)
