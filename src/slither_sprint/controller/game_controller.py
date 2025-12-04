"""
Game Controller - manages game loop and logic
"""

import pygame
import random
from pathlib import Path
from model.game_state import GameState
from model.game_mode import GameMode
from view.renderer import Renderer
from settings import load_player_colors, save_player_colors, COLOR_PRESETS
from config import (
    WIDTH,
    HEIGHT,
    FPS,
    GRID_H,
    OBSTACLE_SPAWN_EVERY_STEPS,
    OBSTACLE_SPAWN_CHANCE,
    SPAWN_AHEAD_MIN,
    SPAWN_AHEAD_MAX,
    FINISH_LINE_DISTANCE,
)


class GameController:
    """Controls game flow and updates"""

    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Slither Sprint")
        self.clock = pygame.time.Clock()

        self.game_state = GameState()
        self.renderer = Renderer(self.screen)

        self.acc_ms_p1 = 0
        self.acc_ms_p2 = 0
        self.game_mode = GameMode.MENU
        self.in_start_menu = True
        self.in_customize_menu = False
        self.custom_colors = load_player_colors()
        self.music_muted = False
        self._music_paused_for_fx = False
        self._music_resume_time = 0

        # Track previous alive states for death sound triggering
        self.prev_alive_p1 = self.game_state.snake1.alive
        self.prev_alive_p2 = self.game_state.snake2.alive
        self.prev_winner_text = None
        self.active_name_edit = None  # "P1" or "P2" when editing names

        self._init_audio()

    def run(self):
        """Main game loop"""
        running = True
        current_fps = 0.0
        while running:
            dt = self.clock.tick(FPS)
            current_fps = self.clock.get_fps()

            # Handle events
            if not self._handle_events():
                running = False
                continue

            # Update game only when playing (not paused or in menus)
            if self.game_mode == GameMode.PLAYING and self.game_state.winner_text is None:
                self._update_game(dt)

            # Handle resuming music after one-shot effects
            self._update_music()

            # Render
            self.renderer.render(
                self.game_state,
                current_fps,
                in_start_menu=self.in_start_menu,
                in_customize_menu=self.in_customize_menu,
                customize_state=self.custom_colors,
                is_muted=self.music_muted,
                is_paused=(self.game_mode == GameMode.PAUSED),
            )

    def _handle_events(self):
        """
        Handle pygame events

        Returns:
            False if should quit, True otherwise
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Mute toggle via mouse
                mute_rect = self.renderer.mute_button_rect
                if mute_rect is not None and mute_rect.collidepoint(mx, my):
                    self._toggle_mute()
                    continue
                # Mouse interaction on start menu buttons
                if self.in_start_menu:
                    start_rect = self.renderer.start_button_rect
                    custom_rect = self.renderer.customize_button_rect
                    if start_rect is not None and start_rect.collidepoint(mx, my):
                        self._start_game()
                        continue
                    if custom_rect is not None and custom_rect.collidepoint(mx, my):
                        self.in_customize_menu = True
                        self.in_start_menu = False
                        continue
                # Mouse interaction on customization UI
                if self.in_customize_menu:
                    # Name boxes
                    if (
                        self.renderer.p1_name_rect is not None
                        and self.renderer.p1_name_rect.collidepoint(mx, my)
                    ):
                        self.active_name_edit = "P1"
                        continue
                    if (
                        self.renderer.p2_name_rect is not None
                        and self.renderer.p2_name_rect.collidepoint(mx, my)
                    ):
                        self.active_name_edit = "P2"
                        continue

                    # Swatch clicks for both players
                    for idx, rect in enumerate(self.renderer.p1_palette_rects):
                        if rect.collidepoint(mx, my):
                            body_col, head_col = COLOR_PRESETS[idx]
                            self.custom_colors["P1"]["body"] = body_col
                            self.custom_colors["P1"]["head"] = head_col
                            break
                    for idx, rect in enumerate(self.renderer.p2_palette_rects):
                        if rect.collidepoint(mx, my):
                            body_col, head_col = COLOR_PRESETS[idx]
                            self.custom_colors["P2"]["body"] = body_col
                            self.custom_colors["P2"]["head"] = head_col
                            break

                    save_rect = self.renderer.custom_save_button_rect
                    cancel_rect = self.renderer.custom_cancel_button_rect
                    if save_rect is not None and save_rect.collidepoint(mx, my):
                        save_player_colors(self.custom_colors)
                        self.in_customize_menu = False
                        self.in_start_menu = True
                        continue
                    if cancel_rect is not None and cancel_rect.collidepoint(mx, my):
                        self.in_customize_menu = False
                        self.in_start_menu = True
                        continue
            elif event.type == pygame.KEYDOWN:
                # ESC always handled first
                if event.key == pygame.K_ESCAPE:
                    if self.in_customize_menu:
                        # Leave customization back to start screen without saving
                        self.in_customize_menu = False
                        self.in_start_menu = True
                    else:
                        return False

                # When in customization and editing a name, consume keys there first.
                # This prevents global shortcuts (like mute on "M") from firing
                # while the user is typing their name.
                if self.in_customize_menu:
                    if self._handle_name_input(event):
                        continue

                # Global mute toggle (only when not typing a name)
                if event.key == pygame.K_m and not self.in_customize_menu:
                    self._toggle_mute()
                    continue

                # Handle menus
                if self.in_customize_menu:
                    self._handle_customize_keys(event.key)
                    continue

                if self.in_start_menu:
                    # Start game from start menu
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self._start_game()
                    # Enter customization
                    elif event.key == pygame.K_c:
                        self.in_customize_menu = True
                        self.in_start_menu = False
                    continue

                # Pause/unpause when in game
                if event.key == pygame.K_p and not self.in_start_menu:
                    if self.game_mode == GameMode.PLAYING:
                        self.game_mode = GameMode.PAUSED
                    elif self.game_mode == GameMode.PAUSED:
                        self.game_mode = GameMode.PLAYING
                    continue

                # Restart when in game (or after win)
                if event.key == pygame.K_r:
                    self.game_state.reset()
                    self.acc_ms_p1 = 0
                    self.acc_ms_p2 = 0
                    self.in_start_menu = False

        # Handle continuous key presses for steering (only when playing)
        if self.game_mode == GameMode.PLAYING:
            keys = pygame.key.get_pressed()
            self.game_state.snake1.steer(keys[pygame.K_a], keys[pygame.K_d])
            self.game_state.snake2.steer(keys[pygame.K_LEFT], keys[pygame.K_RIGHT])

        return True

    def _start_game(self):
        """Transition from start menu into active gameplay"""
        # Persist chosen colors before starting
        save_player_colors(self.custom_colors)
        self._play_start_sound()
        self.game_state.reset()
        self.acc_ms_p1 = 0
        self.acc_ms_p2 = 0
        self.in_start_menu = False
        self.in_customize_menu = False
        self.game_mode = GameMode.PLAYING

    def _handle_customize_keys(self, key):
        """Handle key events while in the customization menu."""
        # Helpers to cycle through shared color presets for each player
        def cycle_for(player_key: str, direction: int):
            current_body = tuple(self.custom_colors[player_key]["body"])
            current_head = tuple(self.custom_colors[player_key]["head"])
            try:
                idx = list(COLOR_PRESETS).index((current_body, current_head))
            except ValueError:
                idx = 0
            idx = (idx + direction) % len(COLOR_PRESETS)
            body_col, head_col = COLOR_PRESETS[idx]
            self.custom_colors[player_key]["body"] = body_col
            self.custom_colors[player_key]["head"] = head_col

        # Player 1 keyboard controls
        if key in (pygame.K_a, pygame.K_q):
            cycle_for("P1", -1)
            return
        if key in (pygame.K_d, pygame.K_e):
            cycle_for("P1", 1)
            return

        # Player 2 keyboard controls
        if key in (pygame.K_LEFT,):
            cycle_for("P2", -1)
            return
        if key in (pygame.K_RIGHT,):
            cycle_for("P2", 1)
            return

        # Save and exit customization
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            save_player_colors(self.custom_colors)
            self.in_customize_menu = False
            self.in_start_menu = True

    def _handle_name_input(self, event: pygame.event.Event) -> bool:
        """Handle text input for player names in customization screen.

        Returns True if the event was consumed.
        """
        if self.active_name_edit is None:
            return False

        key = event.key
        player_key = self.active_name_edit
        current = str(self.custom_colors[player_key].get("name", player_key))

        # Finish editing with Enter
        if key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self.active_name_edit = None
            # Persist into in-memory settings; file is saved when user confirms
            self.custom_colors[player_key]["name"] = current[:16]
            return True

        # Switch focus between players with Tab
        if key == pygame.K_TAB:
            self.active_name_edit = "P2" if player_key == "P1" else "P1"
            return True

        # Backspace to delete characters
        if key == pygame.K_BACKSPACE:
            current = current[:-1]
            self.custom_colors[player_key]["name"] = current[:16]
            return True

        # Ignore modifier keys and non-character keys
        ch = getattr(event, "unicode", "")
        if not ch:
            return False

        if ch.isprintable():
            if len(current) < 16:
                current += ch
                self.custom_colors[player_key]["name"] = current
            return True

        return False

    def _update_game(self, dt):
        """Update game state"""
        # Update power-ups
        self.game_state.snake1.update_powerups()
        self.game_state.snake2.update_powerups()

        # Update snakes with independent timers (for speed boost)
        self._update_snake_movement(dt)

        # Game logic
        self._check_collisions()
        self._handle_apple_collection()
        self._spawn_apples()
        self._update_cameras()
        self._spawn_obstacles()
        self._check_win_conditions()
        self.game_state.cleanup_offscreen_items()

        # Detect new deaths and play explosion sound
        self._check_death_sounds()

    def _update_snake_movement(self, dt):
        """Update snake positions based on their individual step timers"""
        self.acc_ms_p1 += dt
        self.acc_ms_p2 += dt

        while self.acc_ms_p1 >= self.game_state.snake1.current_step_ms:
            self.acc_ms_p1 -= self.game_state.snake1.current_step_ms
            self.game_state.snake1.step()

        while self.acc_ms_p2 >= self.game_state.snake2.current_step_ms:
            self.acc_ms_p2 -= self.game_state.snake2.current_step_ms
            self.game_state.snake2.step()

    def _check_collisions(self):
        """Check for obstacle collisions"""
        s1 = self.game_state.snake1
        s2 = self.game_state.snake2
        obs = self.game_state.obstacles

        if s1.alive and not s1.is_invincible():
            if obs.collides(s1.head):
                s1.alive = False

        if s2.alive and not s2.is_invincible():
            if obs.collides(s2.head):
                s2.alive = False

    def _handle_apple_collection(self):
        """Handle apple collection by snakes"""
        s1 = self.game_state.snake1
        s2 = self.game_state.snake2
        apples_to_remove = []

        for apple in self.game_state.apples:
            if s1.alive and s1.head == apple.position:
                if apple.is_golden:
                    s1.collect_golden_apple()
                else:
                    s1.collect_apple()
                # Play food eaten sound (does not pause background music)
                self._play_food()
                apples_to_remove.append(apple)
            elif s2.alive and s2.head == apple.position:
                if apple.is_golden:
                    s2.collect_golden_apple()
                else:
                    s2.collect_apple()
                # Play food eaten sound (does not pause background music)
                self._play_food()
                apples_to_remove.append(apple)

        for apple in apples_to_remove:
            self.game_state.apples.remove(apple)

    def _spawn_apples(self):
        """Spawn new apples randomly"""
        if random.random() < 0.08 and len(self.game_state.apples) < 50:
            self.game_state.spawn_apple()

    def _update_cameras(self):
        """Update camera positions to follow snakes"""
        # Player 1 camera
        target_camera_p1 = self.game_state.snake1.head[1] - GRID_H * 0.75
        self.game_state.camera_y_p1 += (
            target_camera_p1 - self.game_state.camera_y_p1
        ) * 0.2

        # Player 2 camera
        target_camera_p2 = self.game_state.snake2.head[1] - GRID_H * 0.75
        self.game_state.camera_y_p2 += (
            target_camera_p2 - self.game_state.camera_y_p2
        ) * 0.2

    def _spawn_obstacles(self):
        """Spawn obstacles ahead of snakes"""
        self._spawn_obstacles_for_snake(self.game_state.snake1)
        self._spawn_obstacles_for_snake(self.game_state.snake2)

    def _spawn_obstacles_for_snake(self, snake):
        """Spawn obstacles for a specific snake"""
        if not snake.alive:
            return

        if (
            snake.steps % OBSTACLE_SPAWN_EVERY_STEPS == 0
            and random.random() < OBSTACLE_SPAWN_CHANCE
        ):
            ahead = random.randint(SPAWN_AHEAD_MIN, SPAWN_AHEAD_MAX)
            hx, hy = snake.head
            y = hy - ahead
            span = random.choice([1, 2, 3])
            start_x = random.randint(snake.pane.x0, snake.pane.x1 - (span - 1))

            for i in range(span):
                self.game_state.obstacles.add(start_x + i, y)

    def _check_win_conditions(self):
        """Check if game has ended"""
        # Only check once - prevent duplicate score increments
        if self.game_state.winner_text is not None:
            return

        s1 = self.game_state.snake1
        s2 = self.game_state.snake2

        # Check for finish line
        if s1.alive and s1.head[1] <= FINISH_LINE_DISTANCE:
            self.game_state.winner_text = f"{s1.name.upper()} wins"
            self.game_state.score_p1 += 1
        elif s2.alive and s2.head[1] <= FINISH_LINE_DISTANCE:
            self.game_state.winner_text = f"{s2.name.upper()} wins"
            self.game_state.score_p2 += 1
        # Check for crashes
        elif not s1.alive and s2.alive:
            self.game_state.winner_text = f"{s2.name.upper()} wins"
            self.game_state.score_p2 += 1
        elif not s2.alive and s1.alive:
            self.game_state.winner_text = f"{s1.name.upper()} wins"
            self.game_state.score_p1 += 1
        elif not s1.alive and not s2.alive:
            self.game_state.winner_text = "Draw"
            # No score increment for draws

    # --- Audio helpers -------------------------------------------------

    def _init_audio(self):
        """Initialize mixer and load sounds."""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            # If audio init fails, silently disable audio and clear all sounds
            self.music_muted = True
            self.snd_explosion = None
            self.snd_food = None
            self.snd_start = None
            self.snd_win = None
            return

        # Audio files live in src/slither_sprint/game_sound
        base_dir = Path(__file__).resolve().parent.parent / "game_sound"

        def load_sound(name):
            path = base_dir / name
            try:
                return pygame.mixer.Sound(str(path))
            except pygame.error:
                return None

        # One-shot effects
        self.snd_explosion = load_sound("8-bit-explosion-11-340459.mp3")
        self.snd_food = load_sound("foodeaten.mp3")
        self.snd_start = load_sound("game-start-6104.mp3")
        self.snd_win = load_sound("win-sfx-38507.mp3")

        # Background music
        music_path = base_dir / "gamer-music-140-bpm-355954.mp3"
        try:
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.play(-1)
        except pygame.error:
            self.music_muted = True

    def _toggle_mute(self):
        """Toggle background music mute state."""
        if not pygame.mixer.get_init():
            return
        self.music_muted = not self.music_muted
        if self.music_muted:
            pygame.mixer.music.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(0.6)

    def _duck_music_for_fx(self, sound: pygame.mixer.Sound | None):
        """Pause background music while a one-shot effect plays (except food)."""
        if not pygame.mixer.get_init() or sound is None:
            return

        # Pause music if not muted
        if not self.music_muted:
            pygame.mixer.music.pause()
            self._music_paused_for_fx = True
            length_ms = int(sound.get_length() * 1000)
            self._music_resume_time = pygame.time.get_ticks() + length_ms

        sound.play()

    def _play_start_sound(self):
        """Play game start sound, ducking music."""
        self._duck_music_for_fx(self.snd_start)

    def _play_explosion(self):
        """Play explosion sound, ducking music."""
        self._duck_music_for_fx(self.snd_explosion)

    def _play_win(self):
        """Play win sound, ducking music."""
        self._duck_music_for_fx(self.snd_win)

    def _play_food(self):
        """Play food eaten sound without ducking music."""
        if not pygame.mixer.get_init() or self.snd_food is None:
            return
        self.snd_food.play()

    def _update_music(self):
        """Resume background music after effect finishes, if needed."""
        if (
            pygame.mixer.get_init()
            and self._music_paused_for_fx
            and pygame.time.get_ticks() >= self._music_resume_time
        ):
            self._music_paused_for_fx = False
            if not self.music_muted:
                try:
                    pygame.mixer.music.unpause()
                except pygame.error:
                    pass

    def _check_death_sounds(self):
        """Play explosion sound when a snake dies."""
        s1 = self.game_state.snake1
        s2 = self.game_state.snake2

        if self.prev_alive_p1 and not s1.alive:
            self._play_explosion()
        if self.prev_alive_p2 and not s2.alive:
            self._play_explosion()

        self.prev_alive_p1 = s1.alive
        self.prev_alive_p2 = s2.alive

        # Play win sound when winner text first appears
        current_winner = self.game_state.winner_text
        if self.prev_winner_text is None and current_winner:
            self._play_win()
        self.prev_winner_text = current_winner
