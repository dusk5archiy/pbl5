echo [-- START --]

if [ ! -d ".venv" ]; then
  echo [-- INFO --] .venv folder does not exist, attempt create a new one...
  python -m venv .venv
fi

if [ -d ".venv/Scripts" ]; then
  . .venv/Scripts/activate
else
  exit
fi

pip install -r requirements.txt

(
  cd front
  npm install
  npm run build
)

echo [-- DONE --]
