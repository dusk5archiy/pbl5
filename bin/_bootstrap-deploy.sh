snap install node --classic

# Setup Raspberry Pi dependencies
if [[ $use_rpi == 1 ]]; then
  bin/rpi/setup.sh
fi

# Create venv for task "deploy"
bin/create-venv.sh deploy

# Enter the venv (
. bin/venv.sh deploy
# )

# Backend variables setup
(
  cd back-setup
  python main.py
)

# Compile frontend application
(
  . var/env.sh
  PATH=/snap/bin:$PATH

  cd front
  npm install
  chmod -R +x node_modules/.bin
  npm run build
)
