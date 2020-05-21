from army.api.command import CommandGroup
from army.plugin.package.search import SearchCommand
from army.plugin.package.install import InstallCommand

# init plugin

# get package command group
package_group = CommandGroup.root().get_subgroup("package")
if package_group is None:
    package_group = CommandGroup.root().add_subgroup(CommandGroup("package", "Package commands"))

# load commands
search_command = SearchCommand(package_group)
install_command = InstallCommand(package_group)
