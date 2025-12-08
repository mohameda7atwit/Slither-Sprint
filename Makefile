run:
	PYTHONPATH=./src/slither_sprint uv run slither-sprint

format:
	uv run ruff format .

lint:
	uv run ruff check .

package:
	cd src/slither_sprint && uv run pyinstaller SlitherSprintGame.spec

test:
	uv run pytest tests/