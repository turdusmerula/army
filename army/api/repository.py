from army.api.debugtools import print_stack
from army.api.dict_file import load_dict_file, find_dict_files, save_dict_file
from army.api.log import log
from army.api.package import Package, PackageException
from army.api.path import prefix_path
from army.api.version import Version, VersionRange
import os
import subprocess
import shutil
import toml
import datetime

repository_types = {}

repository_cache = {}

# register a repository type
def register_repository(repository_class):
    global repository_types
    
    if repository_class.TYPE:
        repository_types[repository_class.TYPE] = repository_class
        log.info(f"registered '{repository_class.TYPE}' repository type")


# build repository list from configuration
def load_repositories(config):
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

def load_repository_file(path, parent=None):
    content = load_dict_file(path=path, name="army")
    
    try:
        res = ArmyConfigRepository(value=content, parent=parent)
        res.check()
    except Exception as e:
        print_stack()
        log.debug(e)
        raise ConfigException(f"{format(e)}")
        
    return res

class RepositoryException(Exception):
    def __init__(self, message):
        self.message = message

# TODO: implement source
class Repository(object):
    TYPE=None
    DEV=False
    
    def __init__(self, name, uri):
        self._name = name
        self._uri = uri
    
    @property
    def uri(self):
        return self._uri
    
    @property
    def name(self):
        return self._name
    
    # override to return package list
    @property
    def packages(self):
        return [] 
    
    @property
    def type(self):
        return self.TYPE

    @property
    def editable(self):
        return self.DEV==True
    
    def load_credentials(self):
        return True
    
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
    
    def login(self, user=None, password=None, token=None):
        pass

    def logout(self):
        pass

class RepositoryPackage(Package):
    def __init__(self, data, repository):
        super(RepositoryPackage, self).__init__(data=data, schema={})
        self._repository = repository
        self._source_path = repository._uri
        
    @property
    def repository(self):
        return self._repository
    
    
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
            profile_path = os.path.join(profile_path, f"{profile_name}.yaml")
            if os.path.exists(profile_path):
                raise RepositoryException(f"{profile_path}: profile already installed")
            self._link_file(os.path.join(self._source_path, 'profile', f"{profile}.yaml"), profile_path)
            
    
    def _install(self, path, force, edit):
        self._install_packages_files(path, force=force, edit=edit)
        self._install_profiles(path, force=force, edit=edit)
        self._install_plugins_files(path, force=force, edit=edit)
        
        package_path = os.path.join(path, 'dist', self.name, str(self.version))
        try:
            # try to load installed package definition
            # if package is already installed then it will be modified
            content = load_dict_file(package_path, "army")
        except Exception as e:
            # load source defintion
            content = load_dict_file(self._source_path, "army")

        # add package install source
        content['repository'] = {
            'uri': str(self._repository._uri),
            'name': self._repository._name
        }

        save_dict_file(package_path, "army", content)
        
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
            
class IndexedRepositoryPackage(RepositoryPackage):
    def __init__(self, data, repository):
        super(IndexedRepositoryPackage, self).__init__(data, repository)
        self._loaded = False

    def load(self):
        pass

    def install(self, path, link):
        if self._loaded==False:
            self.load()
        
        super(IndexedRepositoryPackage, self).install(path, link)

class IndexedRepository(Repository):
    def __init__(self, name, uri):
        super(IndexedRepository, self).__init__(name, uri)
        self._loaded = False
        self._index = {}
        
        self._index = {
                'updated': None,
                'packages': {}
            } 
        
    def load(self):
        # load repository index from cache
        try:
            file = os.path.join("~/.army/.cache", f"{self.name}.toml")
            if os.path.exists(os.path.expanduser(file))==False:
                log.error(f"{self.name}: index not built")
            else:
                log.info(f"load index file {file}")
                self._index = toml.load(os.path.expanduser(file))
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise RepositoryException(f"{self.name}: load repository index failed")
        
        self._loaded = True
    
    def save(self):
        pass

    # if repository has an internal cache this is where it should be reconstructed
    def update(self):
        self._index['updated'] = datetime.datetime.now()
        
        try:
            os.makedirs(os.path.expanduser(os.path.join("~/.army/.cache")), exist_ok=True)
            
            file = os.path.join("~/.army/.cache", f"{self.name}.toml")
            log.info(f"write index file {file}")
            with open(os.path.expanduser(file), "w") as f:
                toml.dump(self._index, f)
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            raise RepositoryException(f"{self.name}: load repository index failed")

    @property
    def packages(self):
        raise "not yet implemented"
    
    def _create_package(self, data):
        return IndexedRepositoryPackage(data, self)
    
    def _index_remove_package(self, name):
        if name in self._index['packages']:
            del self._index['packages'][name]
            
    def _index_package(self, name, version, description):
        # add package to index
        if name not in self._index['packages']:
            self._index['packages'][name] = {
                    'description': description,
                    'versions': []
                }
        if version not in self._index['packages'][name]['versions']:
            self._index['packages'][name]['versions'].append(version)
        
        # update common fields in case version is the latest
        if Version(version)>=Version(max(self._index['packages'][name]['versions'], key=lambda x: Version(x))):
            self._index['packages'][name]['description'] = description
            
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
            description = self._index['packages'][package]['description']
            versions = self._index['packages'][package]['versions']
            match_name = False
            
            if fullname==False and name in description.lower():
                match_name = True
                
            if fullname==True and name==package:
                match_name = True
            elif fullname==False and name in package:
                match_name = True
            
            if match_name==True:
                if version is None:
                    # no version specified, give latest by default
                    version_range = VersionRange('latest', versions=versions)
                else:
                    version_range = VersionRange(version, versions=versions)
                
                for version in versions:
                    if version_range.match(version):
                        if (package in res and Version(version)>res[package].version) or package not in res:
                            package_data = {
                                    'name': package,
                                    'description': description,
                                    'version': version
                                }
                            pkg = self._create_package(package_data)
                            res[package] = pkg

        return res
    