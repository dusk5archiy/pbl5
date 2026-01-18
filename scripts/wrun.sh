#!/bin/bash

# For dev, run: scripts/wrun.sh
#           or: scripts/wrun.sh dev
# For production, run: scripts/wrun.sh start

option="${1:-dev}"

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

cd front
if [[ "$option" == "start" ]]; then
  npm run start
elif [[ "$option" == "dev" ]]; then
  npm run dev
fi
