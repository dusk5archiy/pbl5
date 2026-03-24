#!/bin/bash

set -e

# Imports
. bin/_logging.sh

# --- Get started for working with the project.

# OS: Minimized Ubuntu Server 24.04.3 (LTS)
# Installed dependencies: OpenSSH

# Params (

MODE=$1
## Literal["rpi", "ai"] | null = null
## Whether to install Raspberry Pi deployment dependencies.

# ) Params

# Parsing arguments (

use_dev=0
use_ai=0
use_rpi=0

case "$MODE" in
rpi)
  use_rpi=1
  ;;
ai)
  use_ai=1
  ;;
"") ;;
*)
  echoError "Invalid option: $arg"
  exit 1
  ;;
esac

# ) Parsing arguments

# Ensure that the script is run with sudo
if [[ $USER != "root" ]]; then
  echoError "Please run the script with sudo."
  exit 1
fi

echoStart "Start bootstrapping..."

# Update apt
apt update
bin/ubuntu/setup-packages.sh

if [[ $use_ai == 1 ]]; then
  bin/_bootstrap-ai.sh
else
  bin/_bootstrap-deploy.sh
fi

echoSuccess "Finished bootstrapping."
