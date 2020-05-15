from army.api.repository import Repository

class LocalGitRepository(Repository):
    
    def __init__(self, path):
        super(LocalGitRepository, self).__init__(type="git", uri=path)

    # load package list from repository
    def load(self):
        pass
