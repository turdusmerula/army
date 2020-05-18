from army.api.repository import register_repository
from army.plugin.repository.local_git_repository import LocalGitRepository
from army.plugin.repository.git_repository import GitRepository

# init plugin

# register repository types
register_repository(LocalGitRepository)
register_repository(GitRepository)
