. bin/venv.sh deploy
(
  cd back-setup
  python3 main.py
)

(
  cd ai
  python3 main.py
) &

(
  cd back
  python3 main.py
) &
