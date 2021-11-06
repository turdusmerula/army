from army.api.debugtools import print_stack
from army.api.dict_file import load_dict
import army.api.gitlab
from army.api.log import log, get_log_level
from army.api.repository import IndexedRepository, IndexedRepositoryPackage, AuthToken
import gitlab
import keyring
import os
import requests
import sys
import tempfile
from urllib.parse import urlparse
import zipfile

class GitlabRepositoryException(Exception):
    def __init__(self, message):
        self.message = message

class GitlabRepositoryPackage(IndexedRepositoryPackage):
    def __init__(self, data, repository):
        super(GitlabRepositoryPackage, self).__init__(data=data, repository=repository)

    def load(self):
        if self.source_path is not None:
            return

        try:
            uri, groups, project = self.repository._decompose_uri()
            g = self.repository._get_gitlab(uri)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")
        
        _, gitlab_project = self.repository._get_gitlab_project(g, '/'.join(groups), self.name)

        gitlab_release, gitlab_tag = self.repository._get_gitlab_release(self, gitlab_project)
        
        if gitlab_release is None:
            raise GitlabRepositoryException(f"{self.name}-{self.version}: release not found in repository")

        # download package
        data = gitlab_project.generic_packages.download(
            package_name=self.name,
            package_version=self.version,
            file_name=f"{self.name}-{self.version}.zip",
        )
        
        if data is None:
            raise GitlabRepositoryException(f"{self.name}-{self.version}: package found found in repository")
            
        try:
            # download unzip package
            tmpd = tempfile.mkdtemp()
            tmpf = tempfile.mktemp()
        
            with open(tmpf, mode="wb") as f:
                f.write(data)
        
            file = zipfile.ZipFile(tmpf)
            file.extractall(path=tmpd, members=file.namelist())
        
            self._source_path = tmpd
            print("####", self._source_path)
        except Exception as e:
            os.remove(tmpf)
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

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
        #     raise GitlabRepositoryException(f"{e}")
        #
        # os.remove(tmpf)

class GitlabRepository(IndexedRepository):
    Type="gitlab"
    Editable=False
    Login=[AuthToken]
    
    def __init__(self, name, path):
        super(GitlabRepository, self).__init__(name=name, uri=path)
        
    def _decompose_uri(self):
        o = urlparse(str(self._uri))
        uri = o.path

        chuncks = []
        # decompose uri
        while os.path.basename(uri)!='':
            chuncks.append(os.path.basename(uri))
            uri = os.path.dirname(uri)
        
        if len(chuncks)<2:
            raise GitlabRepositoryException(f"{self._uri}: invalid uri")

        groups = []
        if len(chuncks)>0:
            for chunck in chuncks[1:]:
                groups.insert(0, chunck)
                
        return (f"{o.scheme}://{o.netloc}", groups, chuncks[0])
    
    def _get_gitlab(self, uri):
        self.load_credentials()
        if self.credentials is not None:
            # no need to login for public repo but needed for private repo
            g = gitlab.Gitlab(uri, private_token=self.credentials.token)
            g.auth()
        else:
            g = gitlab.Gitlab(uri)
        
        if get_log_level()=='debug':
            g.enable_debug()

        return g
    
    def _get_gitlab_project(self, g, group_path, project_name):
        try:
            gitlab_group = g.groups.get(group_path)
            
            # search project
            gitlab_project = None
            for p in gitlab_group.projects.list(all=True):
                # if p.name==package.name:
                if p.path_with_namespace==f"{group_path}/{project_name}":
                    gitlab_project = g.projects.get(p.id)
                    break
                
            if gitlab_project is None:
                raise GitlabRepositoryException(f"{project_name}: project not found inside repository {self._name}")
        except gitlab.exceptions.GitlabGetError as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{project_name}: project not found inside repository {self._name}")
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")
        
        return gitlab_group, gitlab_project
    
    def _get_gitlab_release(self, package, gitlab_project):
        gitlab_release = None
        gitlab_tag = None
        try:
            # check if release already exists
            for r in gitlab_project.releases.list():
                if r.tag_name==f"v{package.version}":
                    gitlab_release = r
            
            # check if tag already exists
            for t in gitlab_project.tags.list():
                if t.name==f"v{package.version}":
                    gitlab_tag = t
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{package.name}: {e}")
        
        return gitlab_release, gitlab_tag
    
    def _get_gitlab_package(self, package, gitlab_project):
        gitlab_package = None
        try:
            # check if release already exists
            for p in gitlab_project.packages.list():
                if p.name==package.name and p.version==str(package.version):
                    gitlab_package = p
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{package.name}: {e}")
        
        return gitlab_package
    
    def _create_package(self, data):
        return GitlabRepositoryPackage(data, self)

    def get_data(self, gitlab_project, gitlab_release):
        data = None
        
        version = gitlab_release.tag_name.replace('v', '')
        package = gitlab_release.name.replace(f'-{version}', '')
        
        data = gitlab_project.generic_packages.download(
            package_name=package,
            package_version=version,
            file_name="army.yaml",
        )

        if data is None:
            raise GitlabRepositoryException(f"army.yaml missing for release {gitlab_release.name}-{gitlab_release.version}")
    
        return load_dict(data.decode('utf-8'))
    
    def update_index(self):
        try:
            uri, groups, project = self._decompose_uri()
            g = self._get_gitlab(uri)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

        if self.credentials is None:
            print(f"{self.name}: warning: no credential found, update may be incomplete when using private repository", file=sys.stderr)
        
        _, gitlab_project = self._get_gitlab_project(g, '/'.join(groups), project)

        for r in gitlab_project.releases.list():
            try:
                if r.tag_name.startswith("v"):
                    data = self.get_data(gitlab_project, r)
                    self._index_package(project, r.tag_name[1:], data.to_dict())
            except Exception as e:
                print_stack()
                log.debug(f"{type(e)} {e}")
                raise GitlabRepositoryException(f"{e}")

    def login(self, token):
        try:
            uri, _, _ = self._decompose_uri()
            g = self._get_gitlab(uri)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)}: {e}")
            raise GitlabRepositoryException("invalid token")

        self.save_credentials(AuthToken, token=token)

    def logout(self):
        if self.credentials is None:
            raise GitlabRepositoryException(f"no credential found")

        try:
            self.credentials.delete()
        except Exception as e:
            print_stack()
            log.debug(type(e), e)
            raise GitlabRepositoryException(f"{e}")

    def publish(self, package, file, overwrite=False):
        try:
            uri, groups, project = self._decompose_uri()
            g = self._get_gitlab(uri)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

        if self.credentials is None and len(self.Login)>0:
            log.warning(f"{self.name}: no credentials found")
        
        _, gitlab_project = self._get_gitlab_project(g, '/'.join(groups), package.name)

        gitlab_release, gitlab_tag = self._get_gitlab_release(package, gitlab_project)
        
        gitlab_package = self._get_gitlab_package(package, gitlab_project)

        if overwrite==True:
            self.unpublish(package, force=True)
        else:
            if gitlab_release is not None:
                raise GitlabRepositoryException(f"release v{package.version} already exists")
            if gitlab_tag is not None:
                raise GitlabRepositoryException(f"tag v{package.version} already exists")
            if gitlab_package is not None:
                raise GitlabRepositoryException(f"package {package.version}-{package.version} already exists")
        
        try:
            # create tag
            gitlab_tag = gitlab_project.tags.create({'tag_name': f"v{package.version}", 'ref': 'master'})

            # create release
            gitlab_release = gitlab_project.releases.create({'name': f"{package.name}-{package.version}", 'tag_name': f"v{package.version}", 'description': ''})
            
            # add zip content
            gitlab_project.generic_packages.upload(
                package_name=package.name,
                package_version=f"{package.version}",
                file_name=f"{package.name}-{package.version}.zip",
                path=file
            )
            url = f"{uri}/api/v4/projects/{gitlab_project.id}/packages/generic/{package.name}/{package.version}/{package.name}-{package.version}.zip"
            gitlab_release.add_link(name=f"{package.name}-{package.version}.zip", url=url, type='package')
            
            # add army.yaml content
            gitlab_project.generic_packages.upload(
                package_name=package.name,
                package_version=f"{package.version}",
                file_name="army.yaml",
                path="army.yaml"
            )
            url = f"{uri}/api/v4/projects/{gitlab_project.id}/packages/generic/{package.name}/{package.version}/army.yaml"
            gitlab_release.add_link(name=f"army.yaml", url=url, type='package')
            
            # assets can't be downloaded with a token bearer, this solution was discarded
            # # add zip content
            # asset = project.upload(f"{package.name}-{package.version}.zip", filepath=file)
            # url = f"{self._uri}/{asset['url']}"
            # release.add_link(name=f"{package.name}-{package.version}.zip", url=url, type='package')
            #
            # # add army.yaml content
            # asset = project.upload(f"army.yaml", filepath="army.yaml")
            # url = f"{self._uri}/{asset['url']}"
            # release.add_link(name=f"army.yaml", url=url, type='file')
            
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{package.name}: {e}")

    def unpublish(self, package, force=False):
        try:
            uri, groups, project = self._decompose_uri()
            g = self._get_gitlab(uri)
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise GitlabRepositoryException(f"{e}")

        _, gitlab_project = self._get_gitlab_project(g, '/'.join(groups), self.name)

        gitlab_release, gitlab_tag = self._get_gitlab_release(package, gitlab_project)
        
        gitlab_package = self._get_gitlab_package(package, gitlab_project)
        
        if force==False:
            if gitlab_release is None and gitlab_tag is None:
                raise GitlabRepositoryException(f"{package}: release not found inside repository {self._name}")
            if gitlab_release is None:
                log.warning(f"{package}: release missing inside repository {self._name}")
            if gitlab_tag is None:
                log.warning(f"{package}: tag missing inside repository {self._name}")
            if gitlab_package is None:
                log.warning(f"{package}: package missing inside repository {self._name}")

        # remove release
        if gitlab_release is not None:
            log.info(f"remove release v{package.version}")
            try:
                gitlab_project.releases.delete(f"v{package.version}")
            except Exception as e:
                print_stack()
                log.debug(f"{type(e)} {e}")
                raise GitlabRepositoryException(f"{package.name}: {e}")

        # remove release
        if gitlab_tag is not None:
            log.info(f"remove tag v{package.version}")
            try:
                gitlab_project.tags.delete(f"v{package.version}")
            except Exception as e:
                print_stack()
                log.debug(f"{type(e)} {e}")
                raise GitlabRepositoryException(f"{package.name}: {e}")

        # remove package
        if gitlab_package is not None:
            log.info(f"remove package {package.name}-{package.version}")
            try:
                gitlab_project.packages.delete(gitlab_package.id)
            except Exception as e:
                print_stack()
                log.debug(f"{type(e)} {e}")
                raise GitlabRepositoryException(f"{package.name}: {e}")
