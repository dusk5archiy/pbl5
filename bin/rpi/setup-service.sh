#!/bin/bash

set -e

# In case of runing this script with sudo
usr=${SUDO_USER:$USER}

mkdir -p /etc/systemd/system/getty@tty1.service.d
touch /etc/systemd/system/getty@tty1.service.d/override.conf
tee /etc/systemd/system/getty@tty1.service.d/override.conf >/dev/null <<EOF
[Service]
ExecStart=-/sbin/agetty --autologin $usr --noclear tty1
EOF

systemctl stop kiosk || true
tee /etc/systemd/system/kiosk.service >/dev/null <<EOF
[Unit]
Before=snapd.service

[Service]
WorkingDirectory=/home/$usr/pbl5
ExecStart=/bin/bash /home/$usr/pbl5/bin/run.sh

[Install]
WantedBy=basic.target
EOF
