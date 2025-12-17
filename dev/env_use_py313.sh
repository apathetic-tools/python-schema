#!/bin/bash
set -euo pipefail
# Switch Poetry environment to Python 3.13
# Tries system Python 3.13 first, then falls back to mise

# Try system python3.13 first (avoid mise-managed paths), then mise
PY313_PATH=""
# Check common system locations
for POSSIBLE_PATH in /usr/bin/python3.13 /usr/local/bin/python3.13; do
  if [ -x "$POSSIBLE_PATH" ] && "$POSSIBLE_PATH" --version 2>&1 | grep -q "3.13"; then
    PY313_PATH="$POSSIBLE_PATH"
    break
  fi
done
# If not in system locations, check PATH but exclude mise-managed paths
if [ -z "$PY313_PATH" ]; then
  CMD_PATH=$(command -v python3.13 2>/dev/null || true)
  if [ -n "$CMD_PATH" ] && ! echo "$CMD_PATH" | grep -qE "(mise|\.mise)"; then
    if "$CMD_PATH" --version 2>&1 | grep -q "3.13"; then
      PY313_PATH="$CMD_PATH"
    fi
  fi
fi
# Use system Python if found
if [ -n "$PY313_PATH" ]; then
  poetry env use "$PY313_PATH" && poetry install
# Fall back to mise
elif command -v mise >/dev/null 2>&1; then
  # Try to find Python 3.13 via mise (check in standard mise install locations)
  MISE_PYTHON=""
  for MISE_BASE in "${HOME}/.local/share/mise" "${HOME}/.mise"; do
    if [ -x "$MISE_BASE/installs/python/3.13/bin/python3.13" ]; then
      MISE_PYTHON="$MISE_BASE/installs/python/3.13/bin/python3.13"
      break
    fi
  done
  if [ -n "$MISE_PYTHON" ] && [ -x "$MISE_PYTHON" ]; then
    poetry env use "$MISE_PYTHON" && poetry install
  else
    echo "❌ Python 3.13 not found via mise." >&2
    echo "   Install with: mise install python@3.13" >&2
    echo "   Or run: poetry run poe setup:python:check" >&2
    exit 1
  fi
else
  echo "❌ Python 3.13 not found. Run: poetry run poe setup:python:check" >&2
  exit 1
fi

