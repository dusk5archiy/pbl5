#!/bin/bash

# How to run: . scripts/venv.sh

if [ -d ".venv/Scripts" ]; then
  . .venv/Scripts/activate
else
  echo "[-- ERROR --] venv does not exist."
  exit
fi
