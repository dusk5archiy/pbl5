if [ -d ".venv/bin" ]; then
  . .venv/bin/activate
else
  exit
fi

(
  cd ai
  python3 api.py
) &
(
  cd back
  python3 api.py
) &
(
  cd front
  npm run start
)
