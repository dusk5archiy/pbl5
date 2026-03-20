#!/bin/bash

if [ -d ".venv/Scripts" ]; then
  . .venv/Scripts/activate
else
  exit
fi

(
  cd back-setup
  python main.py
)

(
  cd back
  python main.py
) &

(
  . var/env.sh
  cd front
  PORT=$FRONTEND_PORT npm run start
)
