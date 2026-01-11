sudo apt update
sudo apt install --no-install-recommends --no-install-suggests -y install nodejs npm python3

sudo cat >/etc/systemd/system/kiosk.service <<EOF
[Unit]
Before=snapd.service

[Service]
WorkingDirectory=/home/s7usr/pbl5
ExecStart=/bin/bash /home/s7usr/pbl5/scripts/run.sh

[Install]
WantedBy=basic.target
EOF

sudo systemctl enable kiosk
sudo systemctl start kiosk

cd front
if [[ ! -d "node_modules" ]]; then
  npm install
fi
npm run build
