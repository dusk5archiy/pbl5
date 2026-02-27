export task="${1:-deploy}"
export sudo=""

if [[ "$(whoami)" != "root" ]]; then
  export sudo="sudo"
fi

$sudo apt update

mkdir -p .venv

config/$task/setup.sh