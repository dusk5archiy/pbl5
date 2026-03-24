#!/bin/bash

set -e

# Imports
. bin/_logging.sh

# Params
NPM_TASK=${1:-"start"}
if [[ ! "$NPM_TASK" =~ ^(start|dev)$ ]]; then
  echoError "Invalid argument: '$NPM_TASK'."
  exit 1
fi

if [[ $USER != "root" ]]; then
  echoError "Please run the script with sudo."
  exit 1
fi

. bin/_run-python-backends.sh

(
  . var/env.sh
  cd front
  PORT=$FRONTEND_PORT
  PATH=/snap/bin:$PATH
  npm run $NPM_TASK
)
