import os
from pathlib import Path

qtile_dir = Path("~/.config/qtile").expanduser()

hostname = os.uname().nodename
laptop = hostname == "tachi"

terminal = "kitty"
file_manager = "pcmanfm"
browser = "firefox"
calendar = "morgen"

widget_style = "powerline"
