from army.api.log import log
from army.api.package import Package, PackageException
from army.api.debugtools import print_stack
from army.api.version import Version, VersionRange
import os
import subprocess
import shutil
import toml

repository_types = {}

def register_repository(repository_class):
    global repository_types
    
    if repository_class.TYPE:
        repository_types[repository_class.TYPE] = repository_class
        log.debug(f"registered '{repository_class.TYPE}' repository type")


# build repository list from configuration
def load_repositories(config, prefix=None):
    global repository_types
    res = []
    
    if prefix is None:
        log.debug(f"load repositories")
    else:
        log.debug(f"load repositories from {prefix}")

    repos = {}
    try:
        repos = config.repo
    except Exception as e:
        print_stack()
        log.debug(f"{e}")
        log.warning("No repository found")
    
    for repo_name in repos:
        try:
            repo_type_name = repos[repo_name].type.value()
            repo_uri = os.path.join(prefix or "", repos[repo_name].uri.value())

            if repo_type_name in repository_types:
                    
                repo_type = repository_types[repo_type_name]
                
                # instanciate repository and load it
                repo = repo_type(name=repo_name, path=repo_uri)
                res.append(repo)
            else:
                log.warning(f"{repo_type_name}: unhandheld repository type")
        except Exception as e:
            print_stack()
            log.debug(f"{e}")
            log.error(f"{repo_name}: load repository failed")
            
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
    
    # load package list from repository
    def load(self):
        pass

    # if repository has an internal cache this is where it should be reconstructed
    def update(self):
        self.load()
    
    # search for a package inside the package list
    # @param fullname if True then package name must match exactly, if version is given then fullname is True
    def search(self, name, version=None, fullname=False):
        versions = {}
        
        packages = self.packages

        if version is not None:
            fullname = True
        
        # select packages matching name criteria in package list
        for package in packages:
            match_name = False
            
            if fullname==False and name in package.description.lower():
                match_name = True
                
            if fullname==True and name==package.name:
                match_name = True
            elif fullname==False and name in package.name:
                match_name = True
            
            if match_name==True:
                if package.name in versions:
                    versions[package.name].version.add_version(package.version)
                else:
                    if version is None:
                        # no version specified, give latest by default
                        versions[package.name] = VersionRange(value='latest', versions=[package.version])
                    else:
                        versions[package.name] = VersionRange(value=version, versions=[package.version])

        res = {}
        # select packages matching version in found packages
        for name in versions:
            for package in packages:
                if package.version==versions[name].value:
                    res[name] = package
                    
        return res


class RepositoryPackage(Package):
    def __init__(self, data, repository):
        super(RepositoryPackage, self).__init__(data=data, schema={})
        self._repository = repository
    
    @property
    def repository(self):
        return self._repository
        
    def install(self, path, link):
        includes = self.packaging.include
        
        dest = path

        def rmtree_error(func, path, exc_info):
            print(exc_info)
            exit(1)
        if os.path.exists(path):
            log.debug(f"rm {path}")
            shutil.rmtree(path, onerror=rmtree_error)

        # execute preinstall step
        if os.path.exists(os.path.expanduser(os.path.join(self._repository._uri, 'pkg', 'preinstall'))):
            log.info("execute preinstall script")
            subprocess.check_call([os.path.join(os.path.expanduser(self._repository._uri), 'pkg', 'preinstall')])

        # check that all files exists
        for include in includes:
            source = os.path.join(self._repository._uri, include)
            if os.path.exists(os.path.expanduser(source))==False:
                raise PackageException(f"{include}: package include file not found")

        # create detination tree
        if os.path.exists(dest)==False:
            os.makedirs(dest)
            
        for include in includes:
            source = os.path.join(self._repository._uri, include)
            
            if link==True:
                self._link(source, dest)
            else:
                self._copy(source, dest)
        
        # add repository informations to army.toml
        try:
            self._copy(os.path.join(self._repository._uri, "army.toml"), dest)
            filepath = os.path.join(dest, 'army.toml')
            content = toml.load(filepath)
            content['repository'] = {
                'uri': self._repository._uri,
                'name': self._repository._name
                }
            with open(filepath, "w") as file:
                toml.dump(content, file)
        except Exception as e:
            print_stack()
            log.debug(e)

        #execute postinstall command
        if os.path.exists(os.path.expanduser(os.path.join(self._repository._uri, 'pkg', 'postinstall'))):
            log.info("execute postinstall script")
            subprocess.check_call([os.path.join(os.path.expanduser(self._repository._uri), 'pkg', 'postinstall')])
        
    def _copy(self, source, dest):
        log.debug(f"copy {source} -> {dest}")
        source = os.path.expanduser(source)
        if os.path.isfile(source):
            shutil.copy(source, os.path.join(dest, os.path.basename(source)))
        else:
            shutil.copytree(source, os.path.join(dest, os.path.basename(source)))

    def _link(self, source, dest):
        log.debug(f"link {source} -> {dest}")
        source = os.path.expanduser(source)
        os.symlink(os.path.abspath(source), os.path.join(dest, os.path.basename(source)))
