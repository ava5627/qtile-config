import json
import os
import subprocess
from datetime import datetime, timedelta

from libqtile import bar, hook, layout, qtile, widget
from libqtile.config import Click, Drag, EzKey, Match, Screen
from libqtile.lazy import lazy
from libqtile.log_utils import logger

from group_config import (get_num_monitors, go_to_group, group_keys,
                          group_screen, groups_list)

groups = groups_list

hostname = os.uname().nodename
laptop = hostname == "tachi"

# theme file generated by nixos
theme = os.path.expanduser("~") + "/.config/qtile/colors.json"
if not os.path.exists(theme):
    theme = theme.replace("colors", "default_colors")
with open(theme) as theme_file:
    colors = json.load(theme_file)
powerline_colors = colors["powerline-colors"]

EzKey.modifier_keys = {
    "M": "mod4",
    "A": "mod1",
    "S": "shift",
    "C": "control",
    "H": "mod3",
}
mod = "mod4"
home = os.path.expanduser("~")
terminal = "kitty"
file_manager = "pcmanfm"
browser = "firefox"
calendar = "morgen"


def print_debug(obj):
    odict = obj.__dict__
    ostr = "\n"
    for k in odict:
        if k == "icons":
            continue
        ostr += f"{k}: {odict[k]}\n"
    logger.warning(ostr)


def side(direction):
    @lazy.function
    def _side(qtile):
        layout = qtile.current_layout
        # if not columns layout, just do normal left/right focus
        if layout.name != "columns":
            if direction == -1:
                layout.left()
            elif direction == 1:
                layout.right()
            return

        # get current window position
        current_window = qtile.current_window
        current_top = current_window.get_position()[1]
        current_bottom = current_top + current_window.get_size()[1]
        current_middle = (current_top + current_bottom) / 2

        # focus next column
        if layout.wrap_focus_columns:
            if len(layout.columns) >= 1:
                layout.current = (layout.current + direction) % len(layout.columns)
        else:
            if 0 <= layout.current + direction < len(layout.columns):
                layout.current += direction
            else:
                return

        # get position of previously focused window in next column
        # if there is overlap between the two windows, focus the next window
        next_top = layout.cc.cw.get_position()[1]
        next_bottom = next_top + layout.cc.cw.get_size()[1]
        if (
            current_top <= next_top <= current_bottom
            or current_top <= next_bottom <= current_bottom
        ):
            qtile.current_group.focus(layout.cc.cw, True)
            return

        # if the previously focused window is not next to the current window,
        # loop through all windows in next column
        # and focus the one that is next to the middle of the current window
        for i, win in enumerate(layout.cc.clients):
            next_top = win.get_position()[1] - (layout.margin + layout.border_width) * 2
            next_bottom = (
                next_top + win.get_size()[1] + (layout.margin + layout.border_width) * 2
            )
            if next_top <= current_middle <= next_bottom:
                layout.cc.current_index = i
                qtile.current_group.focus(win, True)
                return

    return _side


@lazy.function
def add_column(qtile):
    layout = qtile.current_layout
    if layout.name != "columns":
        return
    layout.num_columns += 1
    qtile.current_group.layout_all()


@lazy.function
def remove_column(qtile):
    layout = qtile.current_layout
    if layout.name != "columns" or layout.num_columns <= 1:
        return
    layout.num_columns -= 1


@lazy.function
def debug_function(qtile):
    logger.warning(colors)


@lazy.function
def next_window(qtile):
    group = qtile.current_group
    if not group.windows:
        return
    if qtile.current_window.floating and not qtile.current_window.fullscreen:
        next = (
            group.floating_layout.focus_next(qtile.current_window)
            or group.layout.focus_first()
            or group.floating_layout.focus_first(group=group)
        )
    else:
        next = (
            group.layout.focus_next(qtile.current_window)
            or group.floating_layout.focus_first(group=group)
            or group.layout.focus_first()
        )
    if next:
        group.focus(next, True)


@lazy.function
def prev_window(qtile):
    group = qtile.current_group
    if not group.windows:
        return
    if qtile.current_window.floating and not qtile.current_window.fullscreen:
        prev = (
            group.floating_layout.focus_previous(qtile.current_window)
            or group.layout.focus_last()
            or group.floating_layout.focus_last(group=group)
        )
    else:
        prev = (
            group.layout.focus_previous(qtile.current_window)
            or group.floating_layout.focus_last(group=group)
            or group.layout.focus_last()
        )
    if prev:
        group.focus(prev, True)


@lazy.function
def pick_color(qtile):
    try:
        from PIL import Image

        color = subprocess.check_output("xcolor").decode("utf-8").strip()
        image = Image.new("RGB", (100, 100), color)
        image.save("/tmp/color.png")
        qtile.spawn(["dunstify", color, "-i", "/tmp/color.png"])
        qtile.spawn(f"echo -n \\{color} | xclip -sel clip", shell=True)
    except ImportError:
        logger.error("PIL is not installed")


my_keys = [
    # Window keys
    ["M-j", next_window, lazy.window.move_to_top(), "Move focus next"],
    ["M-k", prev_window, lazy.window.move_to_top(), "Move focus prev"],
    ["M-h", side(direction=-1), "Move focus left"],
    ["M-l", side(direction=1), "Move focus right"],
    ["M-S-h", lazy.layout.shuffle_left().when(layout="columns"), "Move window left"],
    ["M-S-l", lazy.layout.shuffle_right().when(layout="columns"), "Move window right"],
    ["M-S-j", lazy.layout.shuffle_down().when(layout="columns"), "Move window down"],
    ["M-S-k", lazy.layout.shuffle_up().when(layout="columns"), "Move window up"],
    ["M-C-h", lazy.layout.grow_left().when(layout="columns"), "Grow window left"],
    ["M-C-l", lazy.layout.grow_right().when(layout="columns"), "Grow window right"],
    ["M-C-j", lazy.layout.grow_down().when(layout="columns"), "Grow window down"],
    ["M-C-k", lazy.layout.grow_up(), "Grow window up"],
    ["M-<bracketright>", add_column, "Add column"],
    ["M-<bracketleft>", remove_column, "Remove column"],
    # Layout keys
    ["M-<Tab>", lazy.next_layout(), "Toggle between layouts"],
    ["M-f", lazy.window.toggle_floating(), "toggle floating"],
    ["M-S-f", lazy.window.toggle_fullscreen(), "toggle fullscreen"],
    # Launch keys
    ["M-e", lazy.spawn(terminal), "Launch Terminal"],
    ["M-b", lazy.spawn(terminal + " -e btop"), "Launch BTOP"],
    ["M-m", lazy.spawn(file_manager), "Launch File manager"],
    ["M-y", lazy.spawn("steam steam://open/friends"), "Launch Steam Friends"],
    ["M-w", lazy.spawn("firefox"), "Launch Firefox"],
    ["M-S-w", lazy.spawn("firefox -private-window"), "Launch Private Firefox"],
    ["M-g", lazy.spawn("qalculate-gtk"), "Launch Calculator"],
    ["M-S-e", lazy.spawn("copyq toggle"), "toggle Copyq"],
    ["M-r", lazy.spawn("rofi -show run -i", shell=True), "Run Launcher"],
    [
        "M-S-r",
        lazy.spawn("rofi -show drun -i", shell=True),
        "Application Launcher",
    ],
    ["M-v", lazy.spawn("edit_configs"), "Config Launcher"],
    ["<Print>", lazy.spawn("flameshot gui"), "Take Screenshot"],
    ["M-<XF86Copy>", pick_color, "Pick color"],
    # Command keys
    ["M-C-r", lazy.reload_config(), "Reload Qtile config"],
    ["M-A-r", lazy.restart(), "Restart Qtile"],
    ["M-q", lazy.window.kill(), "Kill focused window"],
    ["M-C-q", lazy.spawn("xkill"), "Kill focused window"],
    ["M-<F1>", lazy.spawn("powermenu"), "Logout Menu"],
    ["M-<F2>", lazy.spawn("systemctl suspend"), "Suspend"],
    # Media keys
    [
        "<XF86AudioRaiseVolume>",
        lazy.spawn("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+"),
        "Raise volume by 5%",
    ],
    [
        "<XF86AudioLowerVolume>",
        lazy.spawn("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-"),
        "Lower volume by 5%",
    ],
    [
        "<XF86AudioMute>",
        lazy.spawn("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
        "Toggle Mute",
    ],
    [
        "S-<XF86AudioPlay>",
        lazy.spawn("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"),
        "Toggle Mute",
    ],
    [
        "<XF86AudioPlay>",
        lazy.spawn("playerctl --player playerctld play-pause"),
        "Play/Pause",
    ],
    [
        "<XF86AudioPause>",
        lazy.spawn("playerctl --player playerctld play-pause"),
        "Play/Pause",
    ],
    ["<XF86AudioNext>", lazy.spawn("playerctl --player playerctld next"), "Next"],
    ["<XF86AudioPrev>", lazy.spawn("playerctl --player playerctld previous"), "Next"],
    # ["<XF86AudioNext>", lazy.spawn("xdotool key ctrl+alt+period"), "Mute discord"],
    # ["<XF86AudioPrev>", lazy.spawn("xdotool key ctrl+alt+comma"), "Deafen discord"],
    ["M-p", lazy.spawn("playerctl --player playerctld play-pause"), "Play/Pause"],
    ["M-n", lazy.spawn("playerctl --player playerctld next"), "Next"],
    # debug keys
    ["M-S-g", debug_function, "Debug function"],
    # autoclicker
    ["M-S-p", lazy.spawn("xdotool click --repeat 1000 --delay 1 1"), "Autoclick"],
    ["M-C-n", lazy.spawn("dunstctl close"), "Close notification"],
    ["M-C-m", lazy.spawn("dunstctl history-pop"), "Open last notification"],
]


my_keys += group_keys

keys = [EzKey(bind, *cmd, desc=desc) for bind, *cmd, desc in my_keys]

layout_theme = {
    "border_width": 2,
    "margin": 2,
    "border_focus": colors["active"],
    "border_normal": colors["inactive"],
    "border_on_single": True,
}

layouts = [
    layout.Columns(**layout_theme, insert_position=1, fair=True, num_columns=2),
    layout.Max(),
]

widget_defaults = dict(
    font="Source Code Pro",
    fontsize=12,
    padding=2,
    foreground=colors["foreground"],
    background=colors["background"],
)
extension_defaults = widget_defaults.copy()


def make_powerline(widgets):
    powerline = []
    odd = len(widgets) % 2
    for i, w in enumerate(widgets):
        index = (i + 1 - odd) % len(powerline_colors)
        next_index = (index - 1) % len(powerline_colors)
        bg = powerline_colors[index]["bg"]
        text_fg = powerline_colors[index]["fg"]
        fg = powerline_colors[next_index]["bg"]
        if i == 0:
            fg = colors["background"]
        powerline.append(
            widget.TextBox(
                font="Source Code Pro",
                foreground=bg,
                background=fg,
                text="",  # Icon: nf-oct-triangle_left
                fontsize=22,
                padding=0,
            )
        )
        if type(w) is list:
            for w2 in w:
                w2.background = bg
                w2.foreground = text_fg
                powerline.append(w2)
        else:
            w.background = bg
            w.foreground = text_fg
            powerline.append(w)
    return powerline


def make_widgets(screen):
    widget_list = [
        widget.Sep(linewidth=0, padding=6),
        widget.GroupBox(
            font="Source Code Pro Bold",
            margin_y=3,
            margin_x=0,
            padding_y=5,
            padding_x=3,
            borderwidth=3,
            active=colors["active-group-foreground"],
            inactive=colors["active-group-foreground"],
            rounded=False,
            highlight_method="block",
            this_current_screen_border=colors["current-group-background"],
            this_screen_border=colors["other-screen-group-background"],
            other_current_screen_border=colors["current-group-background"],
            other_screen_border=colors["other-screen-group-background"],
            use_mouse_wheel=False,
            hide_unused=True,
            disable_drag=True,
            toggle=False,
            visible_groups=[
                group.name for group in groups_list if group_screen(group) == screen
            ],
        ),
        widget.TaskList(
            rounded=False,
            highlight_method="block",
            margin_y=0,
            margin_x=0,
            padding_y=4,
            padding_x=3,
            borderwidth=3,
            icon_size=0,
            border=colors["active"],
        ),
        widget.Sep(
            linewidth=0,
            padding=6,
        ),
        # widget.Prompt(),
        # widget.WindowName(),
    ]
    pl_list = [
        widget.CPU(
            format="CPU {load_percent}%",
            padding=6,
        ),
        widget.Memory(
            format="{MemUsed: .0f}{mm} /{MemTotal: .0f}{mm}",
            mouse_callbacks={"Button1": lambda: qtile.spawn(terminal + " -e btop")},
            padding=5,
        ),
        widget.Net(
            format="{down:.2f}{down_suffix} ↓↑ {up:.2f}{up_suffix}",
            prefix="M",
            padding=5,
        ),
        # widget.GenPollUrl(
        #     url="http://localhost:1337/api/v1/entries/sgv?count=1",
        #     headers={"accept": "application/json"},
        #     parse=parse_nightscout,
        #     update_interval=150,
        #     json=True,
        # ),
        widget.PulseVolume(
            unmute_format="  {volume}%",
            mute_format="  0%",
            padding=5,
            mouse_callbacks={
                "Button1": lambda: qtile.spawn("pavucontrol"),
                "Button3": lambda: qtile.spawn(
                    "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle"
                ),
            },
            step=5,
        ),
        widget.Clock(
            font="Source Code Pro Bold",
            padding=5,
            format="%A, %B %d - %H:%M ",
            mouse_callbacks={"Button1": lambda: qtile.spawn(calendar)},
        ),
    ]

    systray = [
        widget.Systray(
            icon_size=20,
            padding=5,
        ),
        widget.Sep(
            linewidth=0,
            padding=6,
        ),
    ]

    if screen == get_num_monitors() - 1:
        pl_list.insert(-1, systray)
    if laptop:
        battery_widget = widget.Battery(
            format="  {percent:2.0%} {char}{hour:d}:{min:02d}",
            charge_char="+",
            discharge_char="-",
            empty_char="x",
            notify_below=10,
        )
        current_layout = widget.CurrentLayoutIcon(
            padding=5,
            scale=0.7,
        )
        pl_list.insert(3, battery_widget)
        pl_list.insert(5, current_layout)
    else:
        current_layout = widget.CurrentLayout(
            padding=5,
        )
        pl_list.insert(4, current_layout)

    widget_list += make_powerline(pl_list)
    return widget_list


def parse_nightscout(data):
    dtime = datetime.now() - datetime.fromtimestamp(data[0]["date"] / 1000)
    if dtime > timedelta(minutes=15):
        return "-- No data"
    glucose = data[0]["sgv"]
    direction = data[0]["direction"]
    delta = data[0]["delta"]
    if direction == "Flat":
        arrow = "󰁕"
    elif direction == "FortyFiveUp":
        arrow = "󰧆"
    elif direction == "SingleUp":
        arrow = "󰁞"
    elif direction == "FortyFiveDown":
        arrow = "󰦺"
    elif direction == "SingleDown":
        arrow = "󰁆"
    elif direction == "DoubleUp":
        arrow = "󰁞󰁞"
    elif direction == "DoubleDown":
        arrow = "󰁆󰁆"

    if delta >= 0:
        delta_s = f"+{delta:.0f}mg/dL "
    elif delta < 0:
        delta_s = f"{delta:.0f}mg/dL "
    else:
        delta_s = ""

    return f"{arrow} {glucose} {delta_s}"


num_monitors = get_num_monitors()


screens = [
    Screen(top=bar.Bar(widgets=make_widgets(i), size=24)) for i in range(num_monitors)
]

# Drag floating layouts.
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floats_kept_above = True
floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="copyq"),
        Match(wm_class="qalculate-gtk"),
        Match(title="Friends List", wm_class="steam"),
        # Match(wm_class="pavucontrol"),
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(wm_class="Arandr"),
        Match(wm_class="feh"),
    ],
    border_focus=colors["active"],
    border_normal=colors["inactive"],
    border_width=2,
)
auto_fullscreen = True
focus_on_window_activation = "urgent"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = False


@hook.subscribe.startup_once
def start_once():
    qtile.groups_map["1"].toscreen(0)
    if len(qtile.screens) > 1:
        qtile.groups_map["a"].toscreen(1)
    if len(qtile.screens) > 2:
        qtile.groups_map["z"].toscreen(2)
    autostart = home + "/.config/qtile/autostart.sh"
    if os.path.exists(autostart):
        # auto start file generated by nixos
        subprocess.call([autostart])
    # go_to_group(qtile, "1")


@hook.subscribe.client_new
def set_floating(window):
    if window.window.get_wm_transient_for():
        window.floating = True


@hook.subscribe.client_new
def fix_group(window):
    if "discord" not in window.get_wm_class():
        group = qtile.current_group
        if window.group != group and window.floating:
            window.togroup(group.name)


@hook.subscribe.client_urgent_hint_changed
def urgent_hint_changed(window):
    if window.urgent:
        go_to_group(qtile, window.group.name)
        window.focus(False)


# Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
