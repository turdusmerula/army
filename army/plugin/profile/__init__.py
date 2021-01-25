import army.api.command


profile_group = army.api.command.get_army_parser().add_group(name="profile", help="Profile Management Commands")
profile_command = profile_group.add_command(name="profile", help="Manage profile")

import army.plugin.profile.current
import army.plugin.profile.inspect
import army.plugin.profile.list
import army.plugin.profile.search
import army.plugin.profile.set
