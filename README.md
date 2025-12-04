# Slither Sprint

Slither Sprint is a fast-paced, two-player vertical split-screen Snake racing game built with Python and Pygame, using a modern src/ package layout.

## Game Overview

Players compete head-to-head, each controlling a snake that climbs upward in its own half of the screen. The objective is to reach the finish line first or outlast your opponent!

### Features
- **Split-Screen Action:** The window is divided into two panes: Player 1 (left) and Player 2 (right).
- **Vertical Climb:** Snakes always move upward; players can only steer left or right.
- **Scrolling World:** The screen scrolls as snakes climb higher.
- **Collectibles:**
	- Red apples: Score points and gain speed boosts after collecting several.
	- Golden apples: Grant temporary invincibility.
- **Obstacles:** Randomly spawn ahead as you climb, requiring quick reflexes.
- **Power-Ups:** Speed boost and invincibility add strategic depth.
- **Finish Line:** First to reach the top wins! If both crash, it's a draw.
- **Quick Restart:** Press `R` to restart instantly.

## Controls

| Player      | Move Left | Move Right |
|-------------|-----------|------------|
| Player 1    | A         | D          |
| Player 2    | ← (Left)  | → (Right)  |

Other:
- `R` — Restart the game
- `ESC` — Quit

## Requirements
- Python 3.10+
- Pygame

## Setup

Install dependencies (recommended):

```bash
uv pip install -r requirements.txt
```
or
```bash
pip install -r requirements.txt
```

## How to Run

You can run the game using the Makefile:

```bash
make run
```

Or directly with uv:

```bash
uv run slither-sprint
```

## Code Formatting

Format all code using Ruff (via uv):

```bash
make format
```

## Linting

Check code style and lint with Ruff (via uv):

```bash
make lint
```

## Testing

To run the test suite with pytest run: 

```bash
make test
```

## Deploying the Game

We use pyinstaller to package the game as a single file which can run in any computer. 

The latest version of the game will always be provided under `~/Slither-Sprint/SlitherSprintGame`. You can run that just like any other program.

If you are developing and would like to test packaging the game run: 
```
make package
```

## Project Structure

```
src/
	slither_sprint/
		config.py
		controller/
		model/
		view/
		game.py
```

## Credits
Developed by the Slither Sprint team.

Sound Effect by <a href="https://pixabay.com/users/freesound_community-46691455/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=6104">freesound_community</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=6104">Pixabay</a>

Sound Effect by <a href="https://pixabay.com/users/darren_hirst-47836735/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=355954">Darren Hirst</a> from <a href="https://pixabay.com//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=355954">Pixabay</a>