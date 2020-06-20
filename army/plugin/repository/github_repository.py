from army.api.repository import Repository
from army.api.log import log
import github
from github.GithubException import BadCredentialsException
from army.api.debugtools import print_stack
import sys

class GithubRepositoryException(Exception):
    def __init__(self, message):
        self.message = message

class GithubRepository(Repository):
    TYPE="github"
    DEV=False
    
    def __init__(self, name, path):
        super(GithubRepository, self).__init__(name=name, uri=path)
        
        self._packages = []
        
        self.load()

    # load package list from repository
    def load(self):
        pass

    def update(self):
        g = github.Github()
        o = g.get_organization("FirmwareArmy")
        print(o.get_repos())
        for r in o.get_repos():
            try:
                print("-", r)
            except Exception as e:
                print(e)
        
    def packages(self):
        return self._packages 

    def login(self, user, password):
        try:
            g = github.Github(user, password)
            for repo in g.get_user().get_repos():
                # if it suceeds one time then it means we are logged ok
                name = repo.name
                return
        except BadCredentialsException as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException("invalid username/password")
        except Exception as e:
            print_stack()
            log.debug(type(e), e)
            raise GithubRepositoryException("login failed")
