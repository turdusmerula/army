import sys
import os

# add plugin to python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from army.api.command import CommandGroup
from plugin1.hello import HelloCommand

# init plugin

# get package command group
plugins_group = CommandGroup.root().get_subgroup("dummy")
if plugins_group is None:
    plugins_group = CommandGroup.root().add_subgroup(CommandGroup("dummy", "Plugin dummy test commands"))

# load commands
plugin1_command = HelloCommand(plugins_group)
