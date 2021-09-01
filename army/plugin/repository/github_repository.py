from army.api.repository import IndexedRepository, IndexedRepositoryPackage
from army.api.log import log, get_log_level
import army.api.github
import github
from github.GithubException import BadCredentialsException, UnknownObjectException
from army.api.debugtools import print_stack
import sys
import os
from time import sleep
import requests
import tempfile
import zipfile
import io
import shutil
import keyring
from urllib.parse import urlparse

class GithubRepositoryException(Exception):
    def __init__(self, message):
        self.message = message

class GithubRepositoryPackage(IndexedRepositoryPackage):
    def __init__(self, data, repository):
        super(GithubRepositoryPackage, self).__init__(data=data, repository=repository)

    def load(self):
        # Download package
        try:
            uri, org, project = self.repository._decompose_uri()
            g = github.Github(self.repository._token)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")
        
        try:
            organization = g.get_organization(org)
        except UnknownObjectException as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{org}: not found")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")

        try:
            # get repo
            repo = organization.get_repo(self.name)

            # locate release
            release = None
            for r in repo.get_releases():
                if r.title==f"{self.name}-{self.version}":
                    release = r
                    break 
            
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")
        
        if release is None:
            raise GithubRepositoryException(f"{self.name}-{self.version}: no release found from github repository")
     
        try:
            # search zip file
            asset = None
            for a in release.get_assets():
                if a.name==f"{self.name}-{self.version}.zip":
                    asset = a
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")

        if asset is None:
            raise GithubRepositoryException(f"{self.name}-{self.version}.zip: not found from github repository")

        try:
            # download unzip package
            tmpd = tempfile.mkdtemp()
            tmpf = tempfile.mktemp()

            # TODO: add credentials for private repository
            r = requests.get(asset.browser_download_url, allow_redirects=True)
            with open(tmpf, mode="wb") as f:
                f.write(r.content)
            
            file = zipfile.ZipFile(tmpf)
            file.extractall(path=tmpd, members=file.namelist())
            
            self._source_path = tmpd
        except Exception as e:
            os.remove(tmpf)
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")

        # load army.toml
        try:
            file = os.path.join(tmpd, "army.toml")
            log.info(f"Load package '{file}'")
            self._data = toml.load(file)
            log.debug(f"content: {self._data}")
        except toml.decoder.TomlDecodeError as e:
            os.remove(tmpf)
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")
        
        os.remove(tmpf)

class GithubRepository(IndexedRepository):
    Type="github"
    Editable=False
    Login=['token']
    
    def __init__(self, name, path):
        super(GithubRepository, self).__init__(name=name, uri=path)
        
        # filled at login
        self._token = None

#         if get_log_level()=="debug":
#             github.enable_console_debug_logging()        

    def _decompose_uri(self):
        o = urlparse(str(self._uri))
        uri = o.path
        
        chuncks = []
        # decompose uri
        while os.path.basename(uri)!='':
            chuncks.append(os.path.basename(uri))
            uri = os.path.dirname(uri)
        
        if len(chuncks)!=2:
            raise GithubRepositoryException(f"{self._uri}: invalid uri")

        return (os.path.dirname(self._uri), chuncks[1], chuncks[0])

    def _create_package(self, data):
        return GithubRepositoryPackage(data, self)

    def load_credentials(self):
        try:
            service_id = f"army.{self.name}"
            token = keyring.get_password(service_id, 'token')
            if token is None:
                return False
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            return False
        
        self._token = token
        return True

    def update(self):
        if self.load_credentials()==False:
            log.warning(f"{self.name}: load credentials failed, update may fail due to rate limitation", file=sys.stderr)
            
        try:
            uri, org, project = self._decompose_uri()
            # no need to login for public repo but needed for private repo
            g = github.Github(self._token)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")

        try:
            repo = g.get_repo(f"{org}/{project}")
            # remove previous index state
            self._index_remove_package(repo.name)

            log.debug(f"update repo {repo}")
            for release in repo.get_releases():
                if release.tag_name.startswith("v"):
                    self._index_package(repo.name, release.tag_name[1:], repo.description)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")
    
        super(GithubRepository, self).update()

    def login(self, token):
        service_id = f"army.{self.name}"
        try:
            keyring.get_password(service_id, 'token')
            keyring.delete_password(service_id, 'token')
        except:
            pass

        try:
            g = github.Github(token)
            for repo in g.get_user().get_repos():
                # if it suceeds one time then it means we are logged ok
                name = repo.name
                break
            
            self._token = token
        except BadCredentialsException as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException("invalid token")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException("login failed")
        
        # store token on keyring
        keyring.set_password(service_id, 'token', token)

    def logout(self):
        service_id = f"army.{self.name}"
        
        try:
            keyring.get_password(service_id, 'token')
            keyring.delete_password(service_id, 'token')
        except keyring.errors.PasswordDeleteError as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException("not logged to repository")
        except Exception as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException(f"{e}")
    
    def publish(self, package, file, overwrite=False):
        try:
            uri, org, project = self._decompose_uri()
            g = github.Github(self._token)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")

        try:
            repo = g.get_repo(f"{org}/{project}")
        except UnknownObjectException as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{org}/{project}: repository not found")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")
        
        # download package file
        # check package match repo
        
        release = None
        tag = None
        try:
            # check if release already exists
            for r in repo.get_releases():
                if r.tag_name==f"v{package.version}":
                    release = r
            
            # check if tag already exists
            for t in repo.get_tags():
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
                    repo.delete_tag(f"v{package.version}")
                except Exception as e:
                    print_stack()
                    log.debug(f"{type(e)} {e}")
                    raise GithubRepositoryException(f"{package.name}: {e}")
            else:
                raise GithubRepositoryException(f"tag v{package.version} already exists")
        
        try:
            # create release
            release = repo.create_git_release(f"v{package.version}", f"{package.name}-{package.version}", message="") #, draft=None, prerelease=None, target_commitish=None)
            release.upload_asset(file, f"{package.name}-{package.version}") #, content_type, name)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{package.name}: {e}")
            