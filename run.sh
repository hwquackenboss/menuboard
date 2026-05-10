#!/bin/bash
DIR="$HOME/pi/menuboard"
cd "$DIR" && python3 build.py --duration 30 && chromium-browser --kiosk --noerrdialogs --disable-infobars --no-first-run "file://$DIR/index.html"
