# Minimized Ubuntu Server 24.04.3 (LTS)

sudo apt update
sudo apt install --no-install-recommends --no-install-suggests -y python3 python3-venv libgl1

if [[ ! -d ".venv" ]]; then
  python3 -m venv .venv
fi

if [[ -f ".venv/bin/activate" ]]; then
  . .venv/bin/activate
else
  exit
fi

pip install -r requirements.txt

(
  cd back-setup
  python3 main.py
)

(
  . var/env.sh
  PATH=/snap/bin:$PATH

  cd front
  npm install
  npm run build
)
