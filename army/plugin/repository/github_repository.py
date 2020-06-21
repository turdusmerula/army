from army.api.repository import Repository
from army.api.log import log, get_log_level
import army.api.github
import github
from github.GithubException import BadCredentialsException, UnknownObjectException
from army.api.debugtools import print_stack
import sys
import os
from time import sleep

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
        
        # filled at login
        self._user = None
        self._password = None
        
#         if get_log_level()=="debug":
#             github.enable_console_debug_logging()        
    
    def _decompose_uri(self):
        uri = self._uri
        
        chuncks = []
        # decompose uri
        while os.path.basename(uri)!='':
            chuncks.append(os.path.basename(uri))
            uri = os.path.dirname(uri)
        
        if len(chuncks)<2:
            raise GithubRepositoryException(f"{self._uri}: invalid uri")
        elif len(chuncks)<3:
            raise GithubRepositoryException(f"{self._uri}: invalid uri, missing organization")
        elif len(chuncks)>3:
            raise GithubRepositoryException(f"{self._uri}: invalid uri, using a project as a repository is not supported")

        return (os.path.dirname(self._uri), os.path.basename(self._uri))
    
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
    
    @property
    def packages(self):
        return self._packages 

    def login(self, user, password):
        try:
            g = github.Github(user, password)
            for repo in g.get_user().get_repos():
                # if it suceeds one time then it means we are logged ok
                name = repo.name
                break
            
            self._user = user
            self._password = password
        except BadCredentialsException as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException("invalid username/password")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException("login failed")

    def publish(self, package, file, overwrite=False):
        try:
            uri, org = self._decompose_uri()
            g = github.Github(self._user, self._password)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")

        try:
            project = g.get_organization(org).get_repo(f"{package.name}")
        except UnknownObjectException as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{package.name}: project not found inside repository {self._name}")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")
        
        release = None
        tag = None
        try:
            # check if release already exists
            for r in project.get_releases():
                print("--", r.tag_name)
                if r.tag_name==f"v{package.version}":
                    release = r
            
            # check if tag already exists
            for t in project.get_tags():
                if t.name==f"v{package.version}":
                    tag = t
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{package.name}: {e}")
            
        # remove release
        if release is not None:
            if overwrite==True:
                log.info(f"remove release v{package.version}")
                try:
                    release.delete_release()
                except Exception as e:
                    print_stack()
                    log.debug(f"{type(e)} {e}")
                    raise GithubRepositoryException(f"{package.name}: {e}")
            else:
                raise GithubRepositoryException(f"release v{package.version} already exists")

        # remove release
        if tag is not None:
            if overwrite==True:
                log.info(f"remove tag v{package.version}")
                try:
                    print("+++", type(project), project.__dict__)
                    project.delete_tag(f"v{package.version}")
                except Exception as e:
                    print_stack()
                    log.debug(f"{type(e)} {e}")
                    raise GithubRepositoryException(f"{package.name}: {e}")
            else:
                raise GithubRepositoryException(f"tag v{package.version} already exists")
        
        try:
            # create release
            release = project.create_git_release(f"v{package.version}", f"{package.name}-{package.version}", message="") #, draft=None, prerelease=None, target_commitish=None)
            release.upload_asset(file, f"{package.name}-{package.version}") #, content_type, name)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{package.name}: {e}")
            