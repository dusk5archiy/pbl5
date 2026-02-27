$sudo apt install --no-install-recommends --no-install-suggests -y \
  python3 \
  python3-venv \
  libgl1 # For opencv-python

if [[ ! -f ".venv/$task/bin/activate" ]]; then
  python3 -m venv --system-site-packages .venv/$task
fi

if [[ ! -f ".venv/$task/bin/activate" ]]; then
  exit
fi

. .venv/$task/bin/activate
pip install -r config/$task/requirements.txt