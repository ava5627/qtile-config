#!/usr/bin/env bash

feh --no-fehbg --bg-scale $HOME/Pictures/Wallpapers/camp_fire.jpg &
flameshot &
copyq &

[ -n "$QUICK_START" ] && exit 0

openrgb -p Off &
blueberry-tray &
solaar -w hide &
discord &
steam -silent &
systemctl restart --user kdeconnect-indicator &
morgen --hidden &
insync start --no-daemon &
firefox &
