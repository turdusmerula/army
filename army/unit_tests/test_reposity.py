from army.api.log import log
from army.api.config import load_configuration
from army.api.repository import load_repositories
import os

# get current file path to find ressource files
path = os.path.dirname(__file__)
log.setLevel('DEBUG') # default log mode warning

print(f"load test files from {path}")
config=load_configuration(prefix=os.path.join(path, "test_data"))
print("config", config.expand())

# load repository plugin
import army.plugin.repository
from army.plugin.repository.local_git_repository import LocalGitRepository

r1 = LocalGitRepository(name="project1", path=os.path.join(path, "test_data/~/git/project1"))
r1.load()
assert r1.TYPE=="git-local"
assert r1.DEV==True
assert len(r1.packages())==1
print(r1.search("project1"))
print(r1.search("project1:1"))

# load test repositories
repositories = load_repositories(config)
print(repositories)


# load search plugin
import army.plugin.package
from army.plugin.package.search import SearchCommand

args = object()
args.NAME = "project1"
c1 = SearchCommand(None)
c1.execute(config, args)
