#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail

# Own stuff
cat  > /etc/udev/rules.d/99-garmin-ant2.rules <<EOF
SUBSYSTEM=="tty", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=="1008", MODE="0666", OWNER="tom", GROUP="tom"
SUBSYSTEM=="usb", ATTRS{idVendor}=="0fcf", ATTRS{idProduct}=="1008", MODE="0666", OWNER="tom", GROUP="tom"
EOF
