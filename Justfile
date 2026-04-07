default:
  @just --list

analyze:
  uv run ruff check src/wikisrv tests
  uv run ruff format --check src/wikisrv tests
  uv run pyright

format:
  uv run ruff check --fix src/wikisrv tests
  uv run ruff format src/wikisrv tests

test *args:
  uv run pytest tests {{args}}

build:
  uv build

release-check:
  just analyze
  just test
  just build
