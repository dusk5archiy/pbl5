echo [-- START --]

if [ ! -d ".venv" ]; then
  echo [-- INFO --] .venv folder does not exist, attempt create a new one...
  python -m venv .venv
fi

if [ -d ".venv/Scripts" ]; then
  . .venv/Scripts/activate
else
  echo "[-- ERROR --] Failed to create a new venv."
  exit
fi

pip install -r torch-requirements.txt
pip install -r requirements.txt

echo [-- DONE --]
