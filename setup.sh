#!/bin/bash
# ──────────────────────────────────────────────────────────────
#  Raspberry Pi Menuboard — One-time Setup Script
#  Run as: bash setup.sh
# ──────────────────────────────────────────────────────────────

MENUBOARD_DIR="/home/pi/menuboard"
AUTOSTART_DIR="/etc/xdg/lxsession/LXDE-pi"
AUTOSTART_FILE="$AUTOSTART_DIR/autostart"

echo "→ Installing Chromium..."
sudo apt update -q
sudo apt install --no-install-recommends -y chromium-browser

echo "→ Creating menuboard directory..."
mkdir -p "$MENUBOARD_DIR/pages"

# Copy files if running from the same directory
for f in build.py; do
  [ -f "./$f" ] && cp "./$f" "$MENUBOARD_DIR/" && echo "→ Copied $f"
done

echo "→ Writing autostart config..."
sudo mkdir -p "$AUTOSTART_DIR"
sudo tee "$AUTOSTART_FILE" > /dev/null <<EOF
@lxpanel --profile LXDE-pi
@pcmanfm --desktop --profile LXDE-pi

# Disable screen blanking
@xset s off
@xset -dpms
@xset s noblank

# Rebuild MENUBOARD from pages/ then launch
@bash -c 'cd $MENUBOARD_DIR && python3 build.py && chromium-browser --kiosk --noerrdialogs --disable-infobars --no-first-run file://$MENUBOARD_DIR/index.html'
EOF

echo ""
echo "✓ Done! Folder structure:"
echo ""
echo "  $MENUBOARD_DIR/"
echo "  ├── build.py        ← run this after changing pages"
echo "  ├── index.html      ← auto-generated, don't edit"
echo "  └── pages/"
echo "      ├── 01-welcome.html"
echo "      ├── 02-info.html"
echo "      └── ...         ← drop your slides here"
echo ""
echo "  Updating slides from your laptop:"
echo "    scp pages/my-slide.html pi@raspberrypi.local:$MENUBOARD_DIR/pages/"
echo "    ssh pi@raspberrypi.local 'cd $MENUBOARD_DIR && python3 build.py'"
echo ""
echo "  Reboot to start:"
echo "    sudo reboot"
