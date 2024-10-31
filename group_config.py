from libqtile.config import Group, Match
from libqtile.lazy import lazy
from libqtile.log_utils import logger


def get_num_monitors():
    num_monitors = 0
    try:
        from Xlib import display as xdisplay

        display = xdisplay.Display()
        screen = display.screen()
        resources = screen.root.xrandr_get_screen_resources()

        for output in resources.outputs:
            monitor = display.xrandr_get_output_info(output, resources.config_timestamp)
            preferred = False
            if hasattr(monitor, "preferred"):
                preferred = monitor.preferred
            elif hasattr(monitor, "num_preferred"):
                preferred = monitor.num_preferred
            if preferred:
                num_monitors += 1
    except ImportError:
        logger.error("Xlib is not installed")
    except Exception as e:
        # always setup at least one monitor
        logger.error(f"Exception while getting num monitors: {e}")
    finally:
        return max(1, num_monitors)


def _go_to_group(name):

    @lazy.function
    def _inner(qtile):
        go_to_group(qtile, name)

    return _inner


def go_to_group(qtile, name):
    old = qtile.current_screen
    group = qtile.groups_map[name]
    screen = group_screen(group)
    group.toscreen(screen)
    qtile.focus_screen(screen, warp=True)
    if qtile.current_screen != old:
        qtile.warp_to_screen()
    if qtile.current_window:
        qtile.current_window.focus(False)


def group_screen(group):
    screen = 0
    if group.name in "123456":
        screen = 0
    elif group.name in "asduio":
        screen = 1
    elif group.name in "zxc7890":
        screen = 2
    return screen % get_num_monitors()


def switch_group(direction):

    @lazy.function
    def _switch_group(qtile):
        cg = qtile.current_screen.group
        next = cg
        screen = -2
        while screen != group_screen(cg):
            next = next._get_group(direction, False, False)
            screen = group_screen(next)
        next.toscreen()

    return _switch_group


def group_key(name, alt=False):
    if alt:
        key = "A-" + infrequent_groups_name_map[name]
    else:
        key = name
    return [
        # mod1 + key of group = switch to group
        ["M-" + key, _go_to_group(name), f"Switch to group {name}"],
        # mod1 + shift + key of group = move focused window to group
        [
            "M-S-" + key,
            lazy.window.togroup(name),
            f"Move window to group {name}",
        ],
        # mod1 + control + key of group = move focused window and switch to group
        [
            "M-C-" + key,
            lazy.window.togroup(name),
            _go_to_group(name),
            f"Move and switch to group {name}",
        ],
    ]


original_groups = {}

groups_list = [
    Group("1", matches=[], layout="max"),
    Group("2", matches=[]),
    Group("3", matches=[]),
    Group("4", matches=[]),
    Group("5", matches=[]),
    Group("6", matches=[]),
    Group("a", matches=[Match(wm_class="discord")]),
    Group("s", matches=[]),
    Group("d", matches=[]),
    Group("u", matches=[]),
    Group("i", matches=[]),
    Group("o", matches=[]),
    Group("z", matches=[]),
    Group("x", matches=[]),
    Group("c", matches=[]),
    Group("7", matches=[]),
    Group("8", matches=[]),
    Group("9", matches=[]),
    Group("0", matches=[]),
]

infrequent_groups_name_map = {
    "4": "1",
    "5": "2",
    "6": "3",
    "u": "a",
    "i": "s",
    "o": "d",
    "7": "z",
    "8": "x",
    "9": "c",
}

group_keys = []
for i in groups_list:
    group_keys.extend(group_key(i.name))
    # make M-A-...-<key> switch to group infrequent_groups_name_map[<key>]
    if i.name in infrequent_groups_name_map:
        group_keys.extend(group_key(i.name, alt=True))

group_keys.extend(
    [
        [
            "M-<period>",
            switch_group(direction=1),
            "Switch to next group",
        ],
        [
            "M-<comma>",
            switch_group(direction=-1),
            "Switch to previous group",
        ],
        # ["M-<backspace>", hide_workspace, "Hide workspace"],
        # ["M-S-<backspace>", restore_workspace, "Restore workspace"],
    ]
)
