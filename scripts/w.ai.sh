#!/bin/bash

if [ -d ".venv/Scripts" ]; then
  . .venv/Scripts/activate
else
  exit
fi

cd ai
python api.py
