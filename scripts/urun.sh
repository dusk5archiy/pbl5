if [ -d ".venv/bin" ]; then
  . .venv/bin/activate
else
  exit
fi

(
  cd back-setup
  python3 main.py
)

(
  cd back
  python3 main.py
) &

(
  . var/env.sh
  cd front
  PORT=$FRONTEND_PORT BACKEND_PORT=$BACKEND_PORT npm run start
)
