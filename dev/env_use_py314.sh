#!/bin/bash
set -euo pipefail
# Switch Poetry environment to Python 3.14
# Tries system Python 3.14 first, then falls back to mise

# Try system python3.14 first (avoid mise-managed paths), then mise
PY314_PATH=""
# Check common system locations
for POSSIBLE_PATH in /usr/bin/python3.14 /usr/local/bin/python3.14; do
  if [ -x "$POSSIBLE_PATH" ] && "$POSSIBLE_PATH" --version 2>&1 | grep -q "3.14"; then
    PY314_PATH="$POSSIBLE_PATH"
    break
  fi
done
# If not in system locations, check PATH but exclude mise-managed paths
if [ -z "$PY314_PATH" ]; then
  CMD_PATH=$(command -v python3.14 2>/dev/null || true)
  if [ -n "$CMD_PATH" ] && ! echo "$CMD_PATH" | grep -qE "(mise|\.mise)"; then
    if "$CMD_PATH" --version 2>&1 | grep -q "3.14"; then
      PY314_PATH="$CMD_PATH"
    fi
  fi
fi
# Use system Python if found
if [ -n "$PY314_PATH" ]; then
  poetry env use "$PY314_PATH" && poetry install
# Fall back to mise
elif command -v mise >/dev/null 2>&1; then
  # Try to find Python 3.14 via mise (check in standard mise install locations)
  MISE_PYTHON=""
  for MISE_BASE in "${HOME}/.local/share/mise" "${HOME}/.mise"; do
    if [ -x "$MISE_BASE/installs/python/3.14/bin/python3.14" ]; then
      MISE_PYTHON="$MISE_BASE/installs/python/3.14/bin/python3.14"
      break
    fi
  done
  if [ -n "$MISE_PYTHON" ] && [ -x "$MISE_PYTHON" ]; then
    poetry env use "$MISE_PYTHON" && poetry install
  else
    echo "❌ Python 3.14 not found via mise." >&2
    echo "   Install with: mise install python@3.14" >&2
    echo "   Or run: poetry run poe setup:python:check" >&2
    exit 1
  fi
else
  echo "❌ Python 3.14 not found. Run: poetry run poe setup:python:check" >&2
  exit 1
fi

