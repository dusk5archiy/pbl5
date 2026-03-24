#!/bin/bash

set -e

systemctl enable snapd
systemctl start snapd

systemctl enable kiosk
systemctl start kiosk

snap install ubuntu-frame
snap enable ubuntu-frame
snap set ubuntu-frame daemon=true
snap start ubuntu-frame

snap install chromium
snap connect chromium:wayland
snap connect chromium:camera :camera
snap enable chromium
snap set chromium url=http://localhost:3000
snap set chromium daemon=true
snap start chromium
