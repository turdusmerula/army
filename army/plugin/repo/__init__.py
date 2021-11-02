import army.api.command

repo_group = army.api.command.get_army_parser().add_group(name="repo", help="Repository Management Commands")
repo_command = repo_group.add_command(name="repo", help="Manage repository")

import army.plugin.repo.add
import army.plugin.repo.list
import army.plugin.repo.login
import army.plugin.repo.logout
import army.plugin.repo.registered
import army.plugin.repo.remove
import army.plugin.repo.update
