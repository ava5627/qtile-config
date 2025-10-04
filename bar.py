from datetime import datetime, timedelta

from libqtile import bar, qtile
from libqtile.config import Screen
from libqtile.log_utils import logger
from qtile_extras import widget
from qtile_extras.widget.decorations import PowerLineDecoration

from group_config import get_num_monitors, group_screen, groups_list
from theme import colors, powerline_colors
from variables import laptop, terminal, widget_style


powerline = {"decorations": [PowerLineDecoration(path="arrow_right", size=10)]}

bar_widget_defaults = dict(
    font="Source Code Pro",
    fontsize=12,
    padding=2,
    foreground=colors["foreground"],
    background=colors["background"],
)


def make_widgets(screen):
    if widget_style == "powerline":
        return make_widgets_powerline(screen)
    else:
        logger.error(f"Unknown widget style: {widget_style}")
        bar_widget_defaults["background"] = "#ff0000"
        return make_widgets_powerline(screen)


def make_powerline(widgets):
    powerline = []
    odd = len(widgets) % 2
    for i, w in enumerate(widgets):
        index = (i + 1 - odd) % len(powerline_colors)
        bg = powerline_colors[index]["bg"]
        fg = powerline_colors[index]["fg"]
        if type(w) is list:
            for w2 in w:
                w2.background = bg
                w2.foreground = fg
                powerline.append(w2)
        else:
            w.background = bg
            w.foreground = fg
            powerline.append(w)
    return powerline


def make_widgets_powerline(screen):
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
            **powerline,
        ),
    ]
    pl_list = [
        widget.CPU(
            format="CPU {load_percent}%",
            padding=6,
            **powerline,
        ),
        widget.Memory(
            format="{MemUsed: .0f}{mm} /{MemTotal: .0f}{mm}",
            mouse_callbacks={"Button1": lambda: qtile.spawn(terminal + " -e btop")},
            padding=5,
            **powerline,
        ),
        widget.Net(
            format="{down:.2f}{down_suffix} ↓↑ {up:.2f}{up_suffix}",
            prefix="M",
            padding=5,
            **powerline,
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
            **powerline,
        ),
        widget.CurrentLayout(
            padding=10 if laptop else 5,
            mode='icon' if laptop else 'text',
            **powerline,
        ),
        widget.Clock(
            font="Source Code Pro Bold",
            padding=5,
            format="%A, %B %d - %H:%M ",
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
            **powerline,
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
            **powerline,
        )
        pl_list.insert(3, battery_widget)

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


screen_list = [
    Screen(
        top=bar.Bar(
            widgets=make_widgets(i), size=24, margin=0, background=colors["background"]
        )
    )
    for i in range(get_num_monitors())
]
