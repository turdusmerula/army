import army.api.command


profile_group = army.api.command.get_army_parser().add_group(name="target", help="Target Management Commands")
profile_command = profile_group.add_command(name="target", help="Manage target")

import army.plugin.target.current
import army.plugin.target.inspect
import army.plugin.target.list
# TODO
# import army.plugin.target.search
import army.plugin.target.set
