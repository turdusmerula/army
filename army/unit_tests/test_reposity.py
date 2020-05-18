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

repositories = load_repositories(config)
print(repositories)
