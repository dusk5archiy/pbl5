#!/bin/bash

. scripts/venv.sh

(
  cd back-setup
  python3 main.py
)

(
  cd ai
  python3 main.py
) &

(
  cd back
  python3 main.py
) &

(
  . var/env.sh
  cd front
  PORT=$FRONTEND_PORT
  PATH=/snap/bin:$PATH
  npm run dev
)
