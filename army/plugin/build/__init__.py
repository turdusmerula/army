from army.api.command import CommandGroup
from army.plugin.build.clean import CleanCommand
from army.plugin.build.compile import CompileCommand

# init plugin

# get package command group
package_group = CommandGroup.root().get_subgroup("build")
if package_group is None:
    package_group = CommandGroup.root().add_subgroup(CommandGroup("build", "Build commands"))


# load commands
clean_command = CleanCommand(package_group)
clean_command.add_subcommand('compile')

compile_command = CompileCommand(package_group)