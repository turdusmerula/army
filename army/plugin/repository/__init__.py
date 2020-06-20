from army.api.repository import register_repository
from army.plugin.repository.local_git_repository import LocalGitRepository
from army.plugin.repository.git_repository import GitRepository
from army.plugin.repository.github_repository import GithubRepository
from army.plugin.repository.gitlab_repository import GitlabRepository

# init plugin

# register repository types
register_repository(LocalGitRepository)
register_repository(GitRepository)
register_repository(GithubRepository)
register_repository(GitlabRepository)
