from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, find_dict_files, save_dict_file
from army.api.log import log
from army.api.package import Package, PackageException
from army.api.path import prefix_path
from army.api.version import Version, VersionRange
import datetime
import getpass
import keyring
import os
import shutil
import subprocess
import tempfile
import yaml

repository_types = {}

repository_cache = {}

# register a repository type
def register_repository(repository_class):
    global repository_types
    
    if repository_class.Type:
        repository_types[repository_class.Type] = repository_class
        log.info(f"registered '{repository_class.Type}' repository type")


# build repository list from configuration
def load_repositories(config, profile=None):
    global repository_types
    global repository_cache
    
    repositories = []
    
    log.debug(f"load repositories")

    repos = {}
    try:
        repos = config.repositories
    except Exception as e:
        print_stack()
        log.debug(f"{e}")
        log.warning("No repository found")
    
    for repo_name in repos:
        if repo_name in repository_cache:
            repositories.append(repository_cache[repo_name])
        else:
            try:
                repo_type_name = repos[repo_name].type
    
                if repo_type_name in repository_types:
                        
                    repo_type = repository_types[repo_type_name]
                    
                    # instanciate repository and load it
                    repo = repo_type(name=repo_name, path=prefix_path(repos[repo_name].uri))
                    repo.load()
                    repositories.append(repo)
                    
                    repository_cache[repo_name] = repo
                else:
                    log.warning(f"{repo_type_name}: unhandheld repository type")
            except Exception as e:
                print_stack()
                log.error(f"{e}")
                log.error(f"{repo_name}: load repository failed")
    return repositories

def load_repository_package():
    pass


class RepositoryException(Exception):
    def __init__(self, message):
        self.message = message

class Repository(object):
    Type=None
    Editable=False
    
    # list of login methods available
    # available:
    # - token
    # - user
    Login=[]


    def __init__(self, name, uri):
        self._name = name
        self._uri = uri
        self._credentials = None
        
    @property
    def name(self):
        return self._name
    
    @property
    def uri(self):
        return self._uri
    
    @property
    def credentials(self):
        return self._credentials
    
    # override to return package list
    @property
    def packages(self):
        return [] 
    
    @property
    def type(self):
        return self.Type

    @property
    def editable(self):
        return self.Editable
    
    def load_credentials(self):
        credentials = None
        for method in self.Login:
            try:
                auth = method(id=self._name)
                auth.load()
                credentials = auth
            except Exception as e:
                pass

        # if credentials is None and len(self.Login)>0:
        #     raise RepositoryException(f"{self.name}: no credentials found")
        self._credentials = credentials

    def save_credentials(self, method, *args, **kwargs):
        # remove any saved credential
        for method in self.Login:
            try:
                auth = method(id=self._name)
                auth.delete()
            except Exception as e:
                pass

        try:
            auth = method(id=self._name, *args, **kwargs)
            auth.save()
            self._credentials = auth
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            raise RepositoryException("invalid credentials")

    # load package list from repository
    def load(self):
        pass

    # if repository has an internal cache this is where it should be reconstructed
    def update(self):
        pass
    
    # search for a package inside the package list
    # @param fullname if True then package name must match exactly, if version is given then fullname is True
    def search(self, name, version=None, fullname=False):
        res = {}
        
        packages = self.packages

        if version is not None:
            fullname = True
        
        name = name.lower()
        # select packages matching name criteria in package list
        for package in packages:
            match_name = False
            match_version = False
            
            if fullname==False and name in package.description.lower():
                match_name = True
                
            if fullname==True and name==package.name:
                match_name = True
            elif fullname==False and name in package.name:
                match_name = True
            
            if match_name:
                if version is None:
                    match_version = True
                else:
                    versions = VersionRange(versions=[package.version]).select(version)
                    if versions is not None:
                        match_version = True

            if match_name==True and match_version==True:
                if package.name not in res:
                    res[package.name] = [package]
                else:
                    res[package.name].append(package)

        return res

    def publish(self, package, overwrite=False):
        pass
    
    def unpublish(self, package, force=False):
        pass
    
    def login(self):
        pass

    def logout(self):
        pass

class RepositoryPackage(Package):
    def __init__(self, data, repository):
        super(RepositoryPackage, self).__init__(data=data)
        self._repository = repository
        
        self._source_path = repository._uri
        
    @property
    def repository(self):
        return self._repository
    
    @property
    def source_path(self):
        return self._source_path

    def _rmtree_error(self, func, path, exc_info):
        raise RepositoryException(exc_info)

    def _preinstall(self, path, edit):
        includes = self.packaging.include
        # check that all files exists
        for include in includes:
            source = os.path.join(self._source_path, include)
            if os.path.exists(os.path.expanduser(source))==False:
                raise PackageException(f"{include}: file not found")

        # create destination tree
        package_path = os.path.join(path, 'dist', self.name, str(self.version))
        if os.path.exists(package_path)==False:
            os.makedirs(package_path)

        # execute preinstall step
        if os.path.exists(os.path.expanduser(os.path.join(self._source_path, 'pkg', 'preinstall'))):
            log.info("execute preinstall script")
            subprocess.check_call([os.path.join(os.path.expanduser(self._source_path), 'pkg', 'preinstall')])
    
    def _install_packages_files(self, path, force, edit):
        package_path = os.path.join(path, 'dist', self.name, str(self.version))
        
        # TODO manage excludes
        includes = self.packaging.include
        for include in includes:
            source = os.path.join(self._source_path, include)
            if edit==True:
                self._link(source, package_path, force=force)
            else:
                self._copy(source, package_path, force=force)

    def _install_plugins_files(self, path, force, edit):
        package_path = os.path.join(path, 'dist', self.name, str(self.version))
        
        plugins = self.plugins
        for plugin in plugins:
            source = os.path.join(self._source_path, plugin)
            if edit==True:
                self._link(source, package_path, force=force)
            else:
                self._copy(source, package_path, force=force)
        
    def _install_profiles(self, path, force, edit):
        package_path = os.path.join(path, 'dist', self.name, str(self.version))
        profile_path = os.path.join(path, 'profile')
        
        # copy profiles
        source = os.path.join(self._source_path, 'profile')
        if os.path.exists(source):
            if edit==True:
                self._link(source, package_path, force=force)
            else:
                self._copy(source, package_path, force=force)
        
        if len(self.profiles)>0 and os.path.exists(profile_path)==False:
            os.makedirs(profile_path)
            
        for profile in self.profiles:
            profile_name = f"{profile}@{self.version}"
            dest_path = os.path.join(profile_path, f"{profile_name}.yaml")
            if os.path.exists(dest_path) or os.path.islink(dest_path):
                if force==True:
                    self._rm(dest_path)
                else:
                    raise RepositoryException(f"{dest_path}: profile already installed")
            source_path = os.path.join(self._source_path, 'profile', f"{profile}.yaml")
            if os.path.exists(os.path.expanduser(source_path))==False:
                raise RepositoryException(f"{source_path}: profile not found")
            self._link_file(source_path, dest_path)
            
    
    def _install(self, path, force, edit):
        error = None
        try:
            self._install_packages_files(path, force=force, edit=edit)
            self._install_profiles(path, force=force, edit=edit)
            self._install_plugins_files(path, force=force, edit=edit)
        except Exception as e:
            error = e
        
        package_path = os.path.join(path, 'dist', self.name, str(self.version))

        # load source defintion
        content = load_dict_file(self._source_path, "army")
        
        try:
            # try to load installed package definition
            # if package is already installed then it will be modified
            installed_content = load_dict_file(package_path, "army")
            content['repository'] = installed_content['repository']
            if 'installed_user' in installed_content:
                content['installed_user'] = installed_content['installed_user']
            if 'installed_by' in installed_content:
                content['installed_by'] = installed_content['installed_by']
        except Exception as e:
            pass
    
        # add package install source
        content['repository'] = {
            'uri': str(self._repository._uri),
            'name': self._repository._name
        }

        save_dict_file(package_path, "army", content)
        
        if error is not None:
            raise error

    def _postinstall(self, path, edit):
        #execute postinstall command
        if os.path.exists(os.path.expanduser(os.path.join(self._source_path, 'pkg', 'postinstall'))):
            log.info("execute postinstall script")
            subprocess.check_call([os.path.join(os.path.expanduser(self._source_path), 'pkg', 'postinstall')])
        

    def install(self, path, force=False, edit=False):
        self._preinstall(path=path, edit=edit)
        
        self._install(path=path, force=force, edit=edit)
        
        self._postinstall(path=path, edit=edit)

#         if os.path.exists(path):
#             log.debug(f"rm {path}")
#             shutil.rmtree(path, onerror=self.rmtree_error)


            
        
    def _copy(self, source, dest, force=False):
        log.debug(f"copy {source} -> {dest}")
        source = os.path.expanduser(source)
        dest = os.path.join(dest, os.path.basename(source))
        
        if force==True and os.path.exists(dest):
            self._rm(dest)
            
        if os.path.isfile(source):
            shutil.copy(source, dest)
        else:
            shutil.copytree(source, dest)

    def _link(self, source, dest, force=False):
        log.debug(f"link {source} -> {dest}")
        source = os.path.expanduser(source)
        dest = os.path.join(dest, os.path.basename(source))
        
        if force==True and os.path.exists(dest):
            self._rm(dest)
        
        os.symlink(os.path.abspath(source), dest)

    def _link_file(self, source, dest, force=False):
        log.debug(f"link {source} -> {dest}")
        source = os.path.expanduser(source)
        
        if force==True and os.path.exists(dest):
            self._rm(dest)

        os.symlink(os.path.abspath(source), dest)

    def _rm(self, path):
        log.debug(f"rm {path}")
        if os.path.islink(path):
            os.unlink(path)
        elif os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path, onerror=self._rmtree_error)



class IndexedRepository(Repository):
    def __init__(self, name, uri):
        super(IndexedRepository, self).__init__(name, uri)
        self._loaded = False
        self._index = {
                'updated': None,
                'packages': {}
            } 
        
    def load(self):
        # load repository index from cache
        try:
            file = os.path.join("~/.army/.cache", f"{self.name}.yaml")
            if os.path.exists(os.path.expanduser(file))==False:
                log.error(f"{self.name}: index not built")
            else:
                log.info(f"load index file {file}")
                with open(os.path.expanduser(file), "r") as f:
                    self._index = yaml.load(f, Loader=yaml.Loader)
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise RepositoryException(f"{self.name}: load repository index failed")
        
        self._loaded = True
    
    def save(self):
        pass

    def update(self):
        self._index['updated'] = datetime.datetime.now()
        
        self._index_clear_packages()
        
        self.update_index()
        
        try:
            os.makedirs(os.path.expanduser(os.path.join("~/.army/.cache")), exist_ok=True)
            
            file = os.path.join("~/.army/.cache", f"{self.name}.yaml")
            log.info(f"write index file {file}")
            with open(os.path.expanduser(file), "w") as f:
                yaml.dump(self._index, f)
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise RepositoryException(f"{self.name}: update repository index failed")

    # if repository has an internal cache this is where it should be reconstructed
    def update_index(self):
        pass
    
    @property
    def packages(self):
        raise "not yet implemented"
    
    def _create_package(self, data):
        return IndexedRepositoryPackage(data, self)
    
    def _index_clear_packages(self):
        self._index['packages'] = {}

    def _index_remove_package(self, name):
        if name in self._index['packages']:
            del self._index['packages'][name]
            
    def _index_package(self, name, version, data):
        # add package to index
        if name not in self._index['packages']:
            self._index['packages'][name] = {}
        self._index['packages'][name][version] = data
            
    def search(self, name, version=None, fullname=False):
        # check if index is loaded
        if self._loaded==False:
            raise RepositoryException(f"{self.name}: index not loaded")
        
        if version is not None:
            fullname = True
        
        res = {}
        name = name.lower()
        # select packages matching name criteria in package list
        for package in self._index['packages']:

            versions = []
            for v in self._index['packages'][package]:
                versions.append(v)

            if version is None:
                # no version specified, give latest by default
                version_range = 'latest'
            else:
                version_range = version

            for v in VersionRange(versions).filter(version_range):
                data = self._index['packages'][package][str(v)]
                
                description = data['description']
                match_name = False
            
                if fullname==False and name in description.lower():
                    match_name = True
                
                if fullname==True and name==package:
                    match_name = True
                elif fullname==False and name in package:
                    match_name = True
            
                if match_name==True:
                    pkg = self._create_package(data)
                    res[package] = [pkg]

        return res

class IndexedRepositoryPackage(RepositoryPackage):
    def __init__(self, data, repository):
        super(IndexedRepositoryPackage, self).__init__(data, repository)
        self._source_path = None

    # override this function to load full package content
    def load(self):
        pass

    def install(self, path, force=False, edit=False):
        self.load()
        super(IndexedRepositoryPackage, self).install(path, force, edit)



class AuthException(Exception):
    def __init__(self, message):
        self.message = message

class Auth(object):
    def __init__(self, id):
        self._id = id

    @property
    def id(self):
        return self._id
    
    def load(self):
        pass
    
    def save(self):
        pass
    
    def delete(self):
        pass
    
class AuthToken(Auth):
    Method = 'token'
    
    def __init__(self, id, token=None):
        super(AuthToken, self).__init__(id)
        self._token = token

    @property
    def token(self):
        return self._token

    def load(self):
        service_id = f"army.repo.{self._id}"
        
        method = None
        try:
            method = keyring.get_password(service_id, 'method')
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            return False
        
        if method is None:
            raise AuthException(f"no credential found")

        if method!='token':
            raise AuthException(f"incompatible credential method found")
        
        token = None
        try:
            token = keyring.get_password(service_id, 'token')
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")

        if token is None:
            raise AuthException(f"no credential found")
    
        self._token = token

    def save(self):
        service_id = f"army.repo.{self._id}"
        
        if self._token is None:
            raise AuthException(f"token not found")
        
        self.delete()
        
        keyring.set_password(service_id, 'method', 'token')
        keyring.set_password(service_id, 'token', self._token)

    def delete(self):
        service_id = f"army.repo.{self._id}"
        try:
            keyring.delete_password(service_id, 'method')
        except:
            pass

        try:
            keyring.delete_password(service_id, 'token')
        except:
            pass
        
class UserPasswordToken(Auth):
    Method = 'user-password'

    def __init__(self, key, user=None, password=None):
        super(UserPasswordToken, self).__init__(key)
        self._user = user
        self._password = password
        
    def load(self):
        service_id = f"army.repo.{self._id}"
        
        method = None
        try:
            method = keyring.get_password(service_id, 'method')
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            return False
        
        if method is None:
            raise AuthException(f"no credential found")

        if method!='user-password':
            raise AuthException(f"incompatible credential method found")
        
        user = None
        password = None
        try:
            user = keyring.get_password(service_id, 'user')
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")
            
        try:
            password = keyring.get_password(service_id, 'password')
        except Exception as e:
            print_stack()
            log.debug(f"{type(e)} {e}")

        if user is None or password is None:
            raise AuthException(f"no credential found")
    
        self._user = user
        self._password = password
    
    def save(self):
        service_id = f"army.repo.{self._id}"
        
        if self._user is None or self._password is None:
            raise AuthException(f"user/password not found")
        
        self.delete()
        
        keyring.set_password(service_id, 'method', 'user-password')
        keyring.set_password(service_id, 'user', self._user)
        keyring.set_password(service_id, 'password', self._password)

    def delete(self):
        service_id = f"army.repo.{self._id}"
        try:
            keyring.delete_password(service_id, 'method')
        except:
            pass

        try:
            keyring.delete_password(service_id, 'user')
        except:
            pass
        
        try:
            keyring.delete_password(service_id, 'password')
        except:
            pass
