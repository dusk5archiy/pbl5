sudo pacman -S --needed --noconfirm \
  nodejs npm \
  python \
  python-pyxdg \
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

sudo systemctl enable --now kiosk-pbl5

sudo tee /etc/systemd/system/kiosk-openbox.service >/dev/null <<EOF
[Unit]
Description=kiosk-openbox

[Service]
User=$USER
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/$USER/.Xauthority"
ExecStart=/usr/bin/startx /usr/bin/openbox-session -- vt1
ExecStart=/bin/sh -c '/usr/bin/startx /usr/bin/firefox --kiosk --no-remote http://localhost:3000 -- :0 vt1'

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now kiosk-openbox

cd front
if [[ ! -d "node_modules" ]]; then
  npm install
fi
npm run build
