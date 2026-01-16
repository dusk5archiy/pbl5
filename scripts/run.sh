if [ -d ".venv/bin" ]; then
  . .venv/bin/activate
else
  exit
fi

(
  cd ai
  python api.py
) &
(
  cd front
  npm run start
)
