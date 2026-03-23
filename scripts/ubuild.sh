#!/bin/bash

# Minimized Ubuntu Server 24.04.3 (LTS)

scripts/venv.setup.sh

sudo snap install node --classic

. scripts/venv.sh

(
  cd back-setup
  python3 main.py
)

(
  . var/env.sh
  PATH=/snap/bin:$PATH

  cd front
  chmod -R +x node_modules/.bin
  npm install
  npm run build
)
