sudo apt update
sudo apt install --no-install-recommends --no-install-suggests -y install nodejs npm python3

cd front
if [[ ! -d "node_modules" ]]; then
  npm install
fi
npm run build
