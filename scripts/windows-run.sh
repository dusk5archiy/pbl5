if [ -d ".venv/Scripts" ]; then
  . .venv/Scripts/activate
else
  exit
fi

(
  cd back
  python main.py
) &
(
  cd front
  npm run start
)
