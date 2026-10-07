#!/usr/bin/env bash
cd "$(dirname "$0")/.."
ctags -R --exclude=.venv --exclude=.git --exclude=__pycache__ .
