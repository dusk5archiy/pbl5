#!/bin/bash

if [ -d ".venv/Scripts" ]; then
  . .venv/Scripts/activate
else
  exit
fi

(
  cd ai
  python api.py
) &
(
  cd back
  python api.py
) &

cd front npm run dev
