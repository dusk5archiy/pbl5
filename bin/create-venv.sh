#!/bin/bash

# --- Create Python virtual environments

set -e

# Params (
TASK_NAME="${1:-deploy}"
# ) Params

bin/ubuntu/setup-packages.sh

mkdir -p .venv

# Execute the task's setup file (
chmod +x "config/$TASK_NAME/create-venv.sh"
"config/$TASK_NAME/create-venv.sh" ".venv/$TASK_NAME"
# )

# Activate the venv
. bin/venv.sh "$TASK_NAME"

# Install dependencies
pip install -r "config/$TASK_NAME/requirements.txt"
