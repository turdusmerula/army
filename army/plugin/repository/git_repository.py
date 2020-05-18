from army.api.repository import Repository

class GitRepository(Repository):
    TYPE="git"
    DEV=True
    
    def __init__(self, path):
        super(GitRepository, self).__init__(uri=path)

    # load package list from repository
    def load(self):
        pass
