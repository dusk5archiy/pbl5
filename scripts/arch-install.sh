# NOT FINISHED YET !

sudo pacman -S --needed --noconfirm \
  nodejs npm \
  python \
  firefox

sudo tee /etc/systemd/system/kiosk-pbl5.service >/dev/null <<EOF
[Unit]
Description=kiosk-pbl5

[Service]
WorkingDirectory=/home/$USER/pbl5
ExecStart=/bin/bash /home/$USER/pbl5/scripts/run.sh

[Install]
WantedBy=basic.target
EOF

sudo systemctl enable --now kiosk-pbl5

cd front
if [[ ! -d "node_modules" ]]; then
  npm install
fi
npm run build
