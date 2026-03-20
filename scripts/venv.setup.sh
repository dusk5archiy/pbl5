#!/bin/bash

export task="${1:-deploy}"
export sudo=""

if [[ "$(whoami)" != "root" ]]; then
  export sudo="sudo"
fi

$sudo apt update

mkdir -p .venv

chmod +x config/$task/setup.sh
config/$task/setup.sh
