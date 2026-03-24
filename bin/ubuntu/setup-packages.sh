#!/bin/bash

# --- Install Ubuntu packages

set -e

sudo apt install -y --no-install-recommends \
  python-is-python3 \
  python3 \
  python3-venv
