# Minimized Ubuntu Server 24.04.3 (LTS)
# Installed: OpenSSH

sudo apt update
sudo apt install --no-install-recommends --no-install-suggests -y python3
sudo snap install node --classic

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

sudo systemctl enable snapd
sudo systemctl start snapd

sudo systemctl enable kiosk
sudo systemctl start kiosk

sudo snap install ubuntu-frame
sudo snap install chromium
sudo snap connect chromium:wayland

sudo snap enable ubuntu-frame
sudo snap set ubuntu-frame daemon=true
sudo snap start ubuntu-frame

sudo snap enable chromium
sudo snap set chromium url=http://localhost:3000
sudo snap set chromium daemon=true
sudo snap start chromium

cd front
if [[ ! -d "node_modules" ]]; then
  npm install
fi
npm run build
