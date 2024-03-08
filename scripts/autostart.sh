#!/usr/bin/env bash
source /etc/os-release
if [ "$ID" != "nixos" ]; then
    nm-applet &
    xfce4-power-manager &
    blueberry-tray &
    picom --config $HOME/.config/qtile/scripts/picom.conf &
    /usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1 &
    dunst &
    playerctld &
    solaar -w hide &
    # starting user applications at boot time
    discord &
    steam -silent &
    openrgb -p Off &
    kdeconnect-indicator &
    morgen --hidden &
    insync start &
    flameshot &
    firefox &
fi

#starting utility applications at boot time
feh --no-fehbg --bg-scale $HOME/Pictures/'Saved Pictures'/Wallpapers/camp_fire.jpg &
copyq &
