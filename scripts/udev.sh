#!/bin/bash

if [ -d ".venv/bin" ]; then
  . .venv/bin/activate
else
  exit
fi

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
  PATH=/snap/bin:$PATH
  PORT=$FRONTEND_PORT

  cd front
  npm run dev
)
