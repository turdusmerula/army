from army.api.repository import Repository

class LocalGitRepository(Repository):
    TYPE="git-local"
    DEV=True
    
    def __init__(self, path):
        super(LocalGitRepository, self).__init__(uri=path)

    # load package list from repository
    def load(self):
        # load project file
        
