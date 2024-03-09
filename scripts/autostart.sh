#!/usr/bin/env bash

feh --no-fehbg --bg-scale $HOME/Pictures/'Saved Pictures'/Wallpapers/camp_fire.jpg &
copyq &

[ -n "$QUICK_START" ] && exit 0

openrgb -p Off &
blueberry-tray &
solaar -w hide &
discord &
steam -silent &
kdeconnect-indicator &
morgen --hidden &
insync start --no-daemon &
firefox &
