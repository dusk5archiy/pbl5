#!/bin/bash

# Imports
. bin/_logging.sh

# Params (
VENV_FOLDER=$1
# )

if [[ -z "$VENV_FOLDER" ]]; then
  echoError "Venv folder is missing."
  exit 1
fi

# libgl1 for opencv-python 
apt install --no-install-recommends --no-install-suggests -y \
  libgl1 \
  python3-tk

python -m venv --system-site-packages "$VENV_FOLDER"
