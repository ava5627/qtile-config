from libqtile.config import Group, Match
from libqtile.lazy import lazy

from config import get_num_monitors


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


original_groups = {}


groups_list = [
    Group("1", layout="max", matches=[]),
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

group_keys = []
for i in groups_list:
    group_keys.extend(
        [
            # mod1 + key of group = switch to group
            ["M-" + i.name, _go_to_group(i.name), f"Switch to group {i.name}"],
            # mod1 + shift + key of group = move focused window to group
            [
                "M-S-" + i.name,
                lazy.window.togroup(i.name),
                f"Move window to group {i.name}",
            ],
            # mod1 + control + key of group = move focused window and switch to group
            [
                "M-C-" + i.name,
                lazy.window.togroup(i.name),
                _go_to_group(i.name),
                f"Move and switch to group {i.name}",
            ],
        ]
    )

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
