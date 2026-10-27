CONFIG = config/config.json
MYPY_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs

.PHONY: install run debug clean lint lint-strict test package

install:
	uv sync

run:
	uv run python3 pac-man.py $(CONFIG)

debug:
	uv run python3 -m pdb pac-man.py $(CONFIG)

clean:
	find . -name "__pycache__" -not -path "./.venv/*" -prune -exec rm -rf {} +
	rm -rf .mypy_cache .pytest_cache build dist

lint:
	uv run flake8 . --exclude .venv,maze
	uv run mypy . --exclude '(\.venv|maze)/' --explicit-package-bases \
		--python-executable .venv/bin/python $(MYPY_FLAGS)

lint-strict:
	uv run flake8 . --exclude .venv,maze
	uv run mypy . --exclude '(\.venv|maze)/' --explicit-package-bases \
		--python-executable .venv/bin/python --strict

test:
	uv run pytest

package:
	uv run pyinstaller --noconfirm --clean pacman.spec
