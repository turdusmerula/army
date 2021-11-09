from army.api.debugtools import print_stack
from army.api.dict_file import load_dict
from army.api.log import log, get_log_level
from army.api.repository import IndexedRepository, IndexedRepositoryPackage, AuthToken
import army.api.github
from github.GithubException import BadCredentialsException, UnknownObjectException
from army.api.debugtools import print_stack
import github
from io import StringIO
import os
import requests
import sys
import tempfile
from urllib.parse import urlparse
import zipfile

class GithubRepositoryException(Exception):
    def __init__(self, message):
        self.message = message

class GithubRepositoryPackage(IndexedRepositoryPackage):
    def __init__(self, data, repository):
        super(GithubRepositoryPackage, self).__init__(data=data, repository=repository)

    def load(self):
        try:
            uri, groups, project = self.repository._decompose_uri()
            g = self._get_github(uri)
        except BadCredentialsException as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException("invalid token")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException("login failed")

        if self.credentials is None and len(self.Login)>0:
            log.warning(f"{self.name}: no credentials found")

        github_repo = self.repository._get_github_repo(g, '/'.join(groups), self.name)

        github_release, github_tag = self.repository._get_github_release(self, github_repo)

        if github_release is None:
            raise GithubRepositoryException(f"{self.name}-{self.version}: release not found in repository")

        github_asset = None
        for a in github_release.get_assets():
            if a.name==f"{self.name}-{self.version}.zip":
                github_asset = a
        if github_asset is None:
            raise GithubRepositoryException(f"{self.name}-{self.version}: asset not found in release")

        data = self.repository._download_asset(github_asset)
        if data is None:
            raise GithubRepositoryException(f"{self.name}-{self.version}: package found found in repository")

        try:
            # download unzip package
            tmpd = tempfile.mkdtemp()
            tmpf = tempfile.mktemp()
        
            with open(tmpf, mode="wb") as f:
                f.write(data)
        
            file = zipfile.ZipFile(tmpf)
            file.extractall(path=tmpd, members=file.namelist())
        
            self._source_path = tmpd
        except Exception as e:
            os.remove(tmpf)
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")

        # # Download package
        # try:
        #     uri, org, project = self.repository._decompose_uri()
        #     g = github.Github(self.repository._token)
        # except Exception as e:
        #     print_stack()
        #     log.debug(f"{type(e)} {e}")
        #     raise GithubRepositoryException(f"{e}")
        #
        # try:
        #     organization = g.get_organization(org)
        # except UnknownObjectException as e:
        #     print_stack()
        #     log.debug(f"{type(e)} {e}")
        #     raise GithubRepositoryException(f"{org}: not found")
        # except Exception as e:
        #     print_stack()
        #     log.debug(f"{type(e)} {e}")
        #     raise GithubRepositoryException(f"{e}")
        #
        # try:
        #     # get repo
        #     repo = organization.get_repo(self.name)
        #
        #     # locate release
        #     release = None
        #     for r in repo.get_releases():
        #         if r.title==f"{self.name}-{self.version}":
        #             release = r
        #             break 
        #
        # except Exception as e:
        #     print_stack()
        #     log.debug(f"{type(e)} {e}")
        #     raise GithubRepositoryException(f"{e}")
        
        # if release is None:
        #     raise GithubRepositoryException(f"{self.name}-{self.version}: no release found from github repository")
        #
        # try:
        #     # search zip file
        #     asset = None
        #     for a in release.get_assets():
        #         if a.name==f"{self.name}-{self.version}.zip":
        #             asset = a
        # except Exception as e:
        #     print_stack()
        #     log.debug(f"{type(e)} {e}")
        #     raise GithubRepositoryException(f"{e}")
        #
        # if asset is None:
        #     raise GithubRepositoryException(f"{self.name}-{self.version}.zip: not found from github repository")
        #
        # try:
        #     # download unzip package
        #     tmpd = tempfile.mkdtemp()
        #     tmpf = tempfile.mktemp()
        #
        #     # TODO: add credentials for private repository
        #     r = requests.get(asset.browser_download_url, allow_redirects=True)
        #     with open(tmpf, mode="wb") as f:
        #         f.write(r.content)
        #
        #     file = zipfile.ZipFile(tmpf)
        #     file.extractall(path=tmpd, members=file.namelist())
        #
        #     self._source_path = tmpd
        # except Exception as e:
        #     os.remove(tmpf)
        #     print_stack()
        #     log.debug(f"{type(e)} {e}")
        #     raise GithubRepositoryException(f"{e}")
        #
        # # load army.toml
        # try:
        #     file = os.path.join(tmpd, "army.toml")
        #     log.info(f"Load package '{file}'")
        #     self._data = toml.load(file)
        #     log.debug(f"content: {self._data}")
        # except toml.decoder.TomlDecodeError as e:
        #     os.remove(tmpf)
        #     print_stack()
        #     log.debug(f"{type(e)} {e}")
        #     raise GithubRepositoryException(f"{e}")
        #
        # os.remove(tmpf)

class GithubRepository(IndexedRepository):
    Type="github"
    Editable=False
    Login=[AuthToken]
    
    def __init__(self, name, path):
        super(GithubRepository, self).__init__(name=name, uri=path)

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

        groups = []
        if len(chuncks)>0:
            for chunck in chuncks[1:]:
                groups.insert(0, chunck)
                

        return (f"{o.scheme}://{o.netloc}", groups, chuncks[0])

    def _get_github(self, uri):
        # TODO allow connexion to a github ee instance
        
        self.load_credentials()
        if self.credentials is not None:
            # no need to login for public repo but needed for private repo
            g = github.Github(login_or_token=self.credentials.token)

            # if it suceeds one time then it means we are logged ok
            u = g.get_user() #.get_repos():
        else:
            g = github.Github() #base_url=uri)
        
        if get_log_level()=='debug':
            github.enable_console_debug_logging()        
            # github.Requester.DEBUG_FLAG = True

        return g

    def _get_github_repo(self, g, group_path, repo_name):
        try:
            github_repo = g.get_repo(f"{group_path}/{repo_name}")
        except UnknownObjectException as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{group_path}/{repo_name}: repository not found")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{e}")
                        
        return github_repo

    def _get_github_release(self, package, github_repo):
        github_release = None
        github_tag = None
        
        try:
            # check if release already exists
            for r in github_repo.get_releases():
                if r.tag_name==f"v{package.version}":
                    github_release = r
        
            # check if tag already exists
            for t in github_repo.get_tags():
                if t.name==f"v{package.version}":
                    github_tag = t
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{package.name}: {e}")

        return github_release, github_tag

    def _create_package(self, data):
        return GithubRepositoryPackage(data, self)

    def _download_asset(self, gitlab_asset):
        
        headers = {'Accept': 'application/octet-stream'}
        
        if self.credentials is not None:
            headers['Authorization'] = 'token '+self.credentials.token
            
        session = requests.Session()
        
        df_response = session.get(gitlab_asset.url, headers=headers)
        data = StringIO(df_response.text)
        
        return data.read()
        
    def get_data(self, gitlab_project, github_release):
        data = None
        
        version = github_release.tag_name.replace('v', '')
        package = github_release.title.replace(f'-{version}', '')
        
        for a in github_release.get_assets():
            if a.name=="army.yaml":
                data = self._download_asset(a)

        if data is None:
            raise GithubRepositoryException(f"army.yaml missing for release {package}-{version}")
    
        return load_dict(data)
    
    def update_index(self):
        try:
            uri, groups, project = self._decompose_uri()
            g = self._get_github(uri)
        except BadCredentialsException as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException("invalid token")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException("login failed")

        if self.credentials is None and len(self.Login)>0:
            print(f"{self.name}: warning: no credential found, update may be incomplete when using private repository", file=sys.stderr)

        github_repo = self._get_github_repo(g, '/'.join(groups), project)

        for r in github_repo.get_releases():
            try:
                if r.tag_name.startswith("v"):
                    data = self.get_data(github_repo, r)
                    self._index_package(project, r.tag_name[1:], data.to_dict())
            except Exception as e:
                print_stack()
                log.debug(f"{type(e)} {e}")
                raise GithubRepositoryException(f"{e}")
            

    def login(self, token):
        try:
            uri, _, _ = self._decompose_uri()
            g = self._get_github(uri)
        except BadCredentialsException as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException("invalid token")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException("login failed")

        self.save_credentials(AuthToken, token=token)

    def logout(self):
        if self.credentials is None:
            raise GithubRepositoryException(f"no credential found")

        try:
            self.credentials.delete()
        except Exception as e:
            print_stack()
            log.debug(type(e), e)
            raise GithubRepositoryException(f"{e}")
            
    def publish(self, package, file, overwrite=False):
        try:
            uri, groups, project = self._decompose_uri()
            g = self._get_github(uri)
        except BadCredentialsException as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException("invalid token")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException("login failed")

        if self.credentials is None and len(self.Login)>0:
            log.warning(f"{self.name}: no credentials found")

        github_repo = self._get_github_repo(g, '/'.join(groups), package.name)

        github_release, github_tag = self._get_github_release(package, github_repo)

        if overwrite==True:
            self.unpublish(package, force=True)
        else:
            if github_release is not None:
                raise GithubRepositoryException(f"release v{package.version} already exists")
            if github_release is not None:
                raise GithubRepositoryException(f"tag v{package.version} already exists")

        try:
            # create release
            release = github_repo.create_git_release(f"v{package.version}", f"{package.name}-{package.version}", message="") #, draft=None, prerelease=None, target_commitish=None)
            release.upload_asset("army.yaml", "army.yaml") #, content_type, name)
            release.upload_asset(file, f"{package.name}-{package.version}.zip") #, content_type, name)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException(f"{package.name}: {e}")

    def unpublish(self, package, force=False):
        try:
            uri, groups, project = self._decompose_uri()
            g = self._get_github(uri)
        except BadCredentialsException as e:
            print_stack()
            log.debug(e)
            raise GithubRepositoryException("invalid token")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GithubRepositoryException("login failed")

        if self.credentials is None and len(self.Login)>0:
            log.warning(f"{self.name}: no credentials found")

        github_repo = self._get_github_repo(g, '/'.join(groups), package.name)

        github_release, github_tag = self._get_github_release(package, github_repo)
        
        if force==False:
            if github_release is None and github_tag is None:
                raise GithubRepositoryException(f"{package}: release not found inside repository {self._name}")
            if github_release is None:
                log.warning(f"{package}: release missing inside repository {self._name}")
            if github_tag is None:
                log.warning(f"{package}: tag missing inside repository {self._name}")

        # remove release
        if github_release is not None:
            log.info(f"remove release v{package.version}")
            try:
                github_release.delete_release()
            except Exception as e:
                print_stack()
                log.debug(f"{type(e)} {e}")
                raise GithubRepositoryException(f"{package.name}: {e}")

        # remove release
        if github_tag is not None:
            log.info(f"remove tag v{package.version}")
            try:
                github_repo.delete_tag(f"v{package.version}")
            except Exception as e:
                print_stack()
                log.debug(f"{type(e)} {e}")
                raise GithubRepositoryException(f"{package.name}: {e}")

