#!/bin/bash

# --- Setup dependencies for running the application in Raspberry Pi
# --- The operating system should be Ubuntu 24.04.3 LTS.

set -e

bin/rpi/setup-service.sh
bin/rpi/setup-packages.sh
