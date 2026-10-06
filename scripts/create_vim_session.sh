#!/usr/bin/env bash
cd "$(dirname "$0")/.."
nvim config/* docs/* pyproject.toml $(find src/balloon_analysis/ -name "*.py" ! -name "__init__.py") -c "terminal" -c "topleft split | :e README.md" -c "vs | :e scripts/create_vim_session.sh"
