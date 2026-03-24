#!/bin/bash

set -e

sudo systemctl enable snapd
sudo systemctl start snapd

sudo systemctl enable kiosk
sudo systemctl start kiosk

sudo snap install ubuntu-frame
sudo snap enable ubuntu-frame
sudo snap set ubuntu-frame daemon=true
sudo snap start ubuntu-frame

sudo snap install chromium
sudo snap connect chromium:wayland
sudo snap connect chromium:camera :camera
sudo snap enable chromium
sudo snap set chromium url=http://localhost:3000
sudo snap set chromium daemon=true
sudo snap start chromium
