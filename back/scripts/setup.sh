if [[ ! -d ".venv" ]]; then
  python -m venv .venv
fi

source scripts/venv.sh

pip install -r requirements.txt
