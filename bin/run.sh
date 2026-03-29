#!/bin/bash

set -e

# -----------------------------------------------------------------------------

# Imports
. bin/_logging.sh
. bin/_port.sh

# -----------------------------------------------------------------------------

# Params
NPM_TASK=${1:-"start"}
if [[ ! "$NPM_TASK" =~ ^(start|dev|build)$ ]]; then
  echoError "Invalid argument: '$NPM_TASK'."
  exit 1
fi

if [[ $USER != "root" ]]; then
  echoError "Please run the script with sudo."
  exit 1
fi

# -----------------------------------------------------------------------------

. bin/venv.sh deploy
(
  cd back-setup
  python main.py
)

. var/env.sh

# -----------------------------------------------------------------------------

if [[ "$NPM_TASK" =~ ^(start|dev)$ ]]; then
  (
    kill_port "$AI_PORT"
    cd ai
    python main.py
  ) &

  (
    kill_port "$BACKEND_PORT"
    cd back
    python main.py
  ) &
fi

# -----------------------------------------------------------------------------

(
  kill_port "$FRONTEND_PORT"
  export NEXT_PUBLIC_BACKEND_PORT="$BACKEND_PORT"
  export NEXT_PUBLIC_AI_PORT="$AI_PORT"
  cd front
  PORT="$FRONTEND_PORT"
  PATH=/snap/bin:$PATH
  npm run "$NPM_TASK"
)
