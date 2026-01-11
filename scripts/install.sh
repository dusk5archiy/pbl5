sudo apt update
sudo apt install --no-install-recommends --no-install-suggests -y nodejs npm python3

sudo systemctl stop kiosk || true
cat >~/kiosk.service <<EOF
[Unit]
Before=snapd.service

[Service]
WorkingDirectory=/home/$USER/pbl5
ExecStart=/bin/bash /home/$USER/pbl5/scripts/run.sh

[Install]
WantedBy=basic.target
EOF

mv ~/kiosk.service /etc/systemd/system/kiosk.service

sudo systemctl enable kiosk
sudo systemctl start kiosk

cd front
if [[ ! -d "node_modules" ]]; then
  npm install
fi
npm run build
