#!/bin/bash

# --- Activate Python virtual environments.

set -e

# Params
TASK_NAME="${1:-deploy}"

VENV=".venv/$TASK_NAME"

# Activate the environment
. "$VENV/bin/activate"

# Assert that venv's Python is in PATH
if [[ "$(which python)" != *"$VENV/bin/python" ]]; then
  echoError "Cannot find venv's Python in PATH."
  exit 1
fi
