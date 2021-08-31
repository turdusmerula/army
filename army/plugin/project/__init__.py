import army.api.command


project_group = army.api.command.get_army_parser().add_group(name="project", help="Project Management Commands")
project_command = project_group.add_command(name="project", help="Manage project")

import army.plugin.project.inspect
