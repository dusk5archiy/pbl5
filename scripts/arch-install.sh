sudo pacman -S --noconfirm \
  nodejs npm \
  python \
  vim \
  which \
  firefox \
  xorg-server \
  xorg-xinit \
  openbox

sudo tee /etc/systemd/system/kiosk-pbl5.service >/dev/null <<EOF
[Unit]
Description=kiosk-pbl5

[Service]
WorkingDirectory=/home/$USER/pbl5
ExecStart=/bin/bash /home/$USER/pbl5/scripts/run.sh

[Install]
WantedBy=basic.target
EOF

sudo tee /etc/systemd/system/kiosk-openbox.service >/dev/null <<EOF
[Unit]
Description=kiosk-openbox

[Service]
ExecStart=/usr/bin/startx /usr/bin/openbox-session -- vt1

[Install]
WantedBy=basic.target
EOF

cd front
if [[ ! -d "node_modules" ]]; then
  npm install
fi
npm run build
