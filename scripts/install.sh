sudo apt update
sudo apt install --no-install-recommends --no-install-suggests -y nodejs npm python3

sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
sudo touch /etc/systemd/system/getty@tty1.service.d/override.conf
sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf >/dev/null <<EOF
[Service]
ExecStart=-/sbin/agetty --autologin $USER --noclear tty1
EOF

sudo systemctl stop kiosk || true
sudo tee /etc/systemd/system/kiosk.service >/dev/null <<EOF
[Unit]
Before=snapd.service

[Service]
WorkingDirectory=/home/$USER/pbl5
ExecStart=/bin/bash /home/$USER/pbl5/scripts/run.sh

[Install]
WantedBy=basic.target
EOF

sudo systemctl enable kiosk
sudo systemctl start kiosk

sudo systemctl enable snapd
sudo systemctl start snapd
sudo snap install ubuntu-frame --classic
sudo snap set ubuntu-frame daemon=true
sudo snap install chromium --classic
sudo snap set chromium url=http://localhost:3000
sudo snap connect chromium:wayland

cd front
if [[ ! -d "node_modules" ]]; then
  npm install
fi
npm run build
