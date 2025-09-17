set shell := ["powershell.exe", "-NoProfile", "-Command"]


default:
    ruff check
    ruff format
    pytest
    ruff clean

run *args:
    uv run src/main.py {{args}}

ruff:
    ruff check
    ruff format
    ruff clean

test:
    pytest