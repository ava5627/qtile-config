#!/usr/bin/env bash
source /etc/os-release
if [ "$ID" != "nixos" ]; then
    nm-applet &
    xfce4-power-manager &
    picom --config $HOME/.config/qtile/scripts/picom.conf &
    /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
    dunst &
    playerctld &
    flameshot &
fi

#starting utility applications at boot time
openrgb -p Off &
blueberry-tray &
feh --no-fehbg --bg-scale $HOME/Pictures/'Saved Pictures'/Wallpapers/camp_fire.jpg &
copyq &
solaar -w hide &
discord &
steam -silent &
kdeconnect-indicator &
morgen --hidden &
insync start --no-daemon &
firefox &
