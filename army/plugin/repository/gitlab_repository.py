from army.api.repository import IndexedRepository, IndexedRepositoryPackage
from army.api.log import log
from army.api.debugtools import print_stack
import army.api.gitlab
import gitlab
import keyring
import os
import sys
import tempfile
import requests
import zipfile
import toml

class GitlabRepositoryException(Exception):
    def __init__(self, message):
        self.message = message

class GitlabRepositoryPackage(IndexedRepositoryPackage):
    def __init__(self, data, repository):
        super(GitlabRepositoryPackage, self).__init__(data=data, repository=repository)

    def load(self):
        # Download package
        try:
            uri, groupuri = self.repository._decompose_uri()
            g = gitlab.Gitlab(uri, private_token=self.repository._token)

            g.auth()
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")
        
        try:
            group = g.groups.get(groupuri)
            project = None
            for p in group.projects.list(all=True):
                if p.name==self.name:
                    project = g.projects.get(p.id)
                    break
            if project is None:
                raise GitlabRepositoryException(f"{self.name}: project not found inside repository {self.repository.name}")
        except gitlab.exceptions.GitlabGetError as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{self.name}: project not found inside repository {self.repository.name}")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

        try:
            # locate release
            release = None
            for r in project.releases.list():
                if r.tag_name==f"v{self.version}":
                    release = r
                    break 
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")
        
        if release is None:
            raise GitlabRepositoryException(f"{self.name}-{self.version}: no release found from github repository")
     
        try:
            # search zip file
            asset = None
            for link in release.assets['links']:
                if link['name']==f"{self.name}-{self.version}.zip":
                    asset = link
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

        if asset is None:
            raise GitlabRepositoryException(f"{self.name}-{self.version}.zip: not found from github repository")

        try:
            # download unzip package
            tmpd = tempfile.mkdtemp()
            tmpf = tempfile.mktemp()

            # TODO: need this bug to be corrected to make this working
            # https://gitlab.com/gitlab-org/gitlab/-/issues/28978
            headers = {'Private-Token': self.repository._token}
            r = requests.get(asset['url'], headers=headers, allow_redirects=True)
            with open(tmpf, mode="wb") as f:
                f.write(r.content)
            
            file = zipfile.ZipFile(tmpf)
            file.extractall(path=tmpd, members=file.namelist())
            
            self._source_path = tmpd
        except Exception as e:
            os.remove(tmpf)
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

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
            raise GitlabRepositoryException(f"{e}")
        
        os.remove(tmpf)

class GitlabRepository(IndexedRepository):
    TYPE="gitlab"
    DEV=False
    
    def __init__(self, name, path):
        super(GitlabRepository, self).__init__(name=name, uri=path)

        self._token = None
        
    def _decompose_uri(self):
        uri = self._uri
        
        chuncks = []
        # decompose uri
        while os.path.basename(uri)!='':
            chuncks.append(os.path.basename(uri))
            uri = os.path.dirname(uri)
        
        if len(chuncks)<2:
            raise GitlabRepositoryException(f"{self._uri}: invalid uri")
        elif len(chuncks)<3:
            raise GitlabRepositoryException(f"{self._uri}: invalid uri, missing group")
        elif len(chuncks)>3:
            raise GitlabRepositoryException(f"{self._uri}: invalid uri, using a project as a repository is not supported")

        return (os.path.dirname(self._uri), os.path.basename(self._uri))

    def _create_package(self, data):
        return GitlabRepositoryPackage(data, self)

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
        logged = self.load_credentials()
        if logged==False:
            print(f"{self.name}: warning: load credentials failed, update may be incomplete when using private repository", file=sys.stderr)
        try:
            uri, groupuri = self._decompose_uri()
            if logged:
                # no need to login for public repo but needed for private repo
                g = gitlab.Gitlab(uri, private_token=self._token)
                g.auth()
            else:
                g = gitlab.Gitlab(uri)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

        try:
            group = None
            for ig in g.groups.list():
                if ig.name==groupuri:
                    group = ig
        except gitlab.exceptions.GitlabGetError as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{groupuri}: group not found")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")
        if group is None:
            raise GitlabRepositoryException(f"{groupuri}: group not found")

        try:
            # get versions
            projects = {}
            for p in g.projects.list():
                projects[p.name] = p
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")
        
        try:
            for p in group.projects.list(all=True):
                log.debug(f"update repo {p.name}")
                if p.name not in projects:
                    log.error(f"{p.name}: update failed")
                    continue # TODO raise error?
                project = projects[p.name]
                for release in project.releases.list():
                    if release.tag_name.startswith("v"):
                        self._index_package(project.name, release.tag_name[1:], project.description)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")
    
        super(GitlabRepository, self).update()

    def login(self, token=None, **kwargs):
        if token is None:
            raise GitlabRepositoryException("only token auth is supported")
            
        try:
            uri, org = self._decompose_uri()
            g = gitlab.Gitlab(uri, private_token=token)

            g.auth()

            self._token = token
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)}: {e}")
            raise GitlabRepositoryException("invalid token")
        
        service_id = f"army.{self.name}"
        # store token on keyring
        keyring.set_password(service_id, 'token', token)

    def logout(self):
        service_id = f"army.{self.name}"
        
        try:
            keyring.delete_password(service_id, 'token')
        except keyring.errors.PasswordDeleteError as e:
            print_stack()
            log.debug(f"{type(e)}: {e}")
            raise GitlabRepositoryException("not logged to repository")
        except Exception as e:
            print_stack()
            log.debug(type(e), e)
            raise GitlabRepositoryException(f"{e}")

    def publish(self, package, file, overwrite=False):
        try:
            uri, groupuri = self._decompose_uri()
            g = gitlab.Gitlab(uri, private_token=self._token)

            g.auth()
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

        try:
            group = g.groups.get(groupuri)
            project = None
            for p in group.projects.list(all=True):
                if p.name==package.name:
                    project = g.projects.get(p.id)
                    break
            if project is None:
                raise GitlabRepositoryException(f"{package.name}: project not found inside repository {self._name}")
        except gitlab.exceptions.GitlabGetError as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{package.name}: project not found inside repository {self._name}")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

        release = None
        tag = None
        try:
            # check if release already exists
            for r in project.releases.list():
                if r.tag_name==f"v{package.version}":
                    release = r
            
            # check if tag already exists
            for t in project.tags.list():
                if t.name==f"v{package.version}":
                    tag = t
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{package.name}: {e}")
                
        # remove release
        if release is not None:
            if overwrite==True:
                log.info(f"remove release v{package.version}")
                try:
                    project.releases.delete(f"v{package.version}")
                except Exception as e:
                    print_stack()
                    log.debug(f"{type(e)} {e}")
                    raise GitlabRepositoryException(f"{package.name}: {e}")
            else:
                raise GitlabRepositoryException(f"release v{package.version} already exists")

        # remove release
        if tag is not None:
            if overwrite==True:
                log.info(f"remove tag v{package.version}")
                try:
                    project.tags.delete(f"v{package.version}")
                except Exception as e:
                    print_stack()
                    log.debug(f"{type(e)} {e}")
                    raise GitlabRepositoryException(f"{package.name}: {e}")
            else:
                raise GitlabRepositoryException(f"tag v{package.version} already exists")
        
        try:
            # create tag
            tag = project.tags.create({'tag_name': f"v{package.version}", 'ref': 'master'})
            
            # create release
            release = project.releases.create({'name': f"{package.name}-{package.version}", 'tag_name': f"v{package.version}", 'description': ''})
            asset = project.upload(f"{package.name}-{package.version}.zip", filepath=file)
            url = f"{self._uri}/{project.name}{asset['url']}"
            release.add_link(name=f"{package.name}-{package.version}.zip", url=url, type='package')
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{package.name}: {e}")
    