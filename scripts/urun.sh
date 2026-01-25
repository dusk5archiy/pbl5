if [ -d ".venv/bin" ]; then
  . .venv/bin/activate
else
  exit
fi

(
  cd back
  python3 api.py
) &

(
  cd front
  npm run start
)
