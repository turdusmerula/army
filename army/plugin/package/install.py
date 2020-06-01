from army.api.log import log
from army.api.command import Command
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.army import prefix

import os
import fnmatch
import shutil

class PackageDependency(object):
    def __init__(self, package, from_package=None):
        self._package = package
        self._from_package = from_package
    
    def package(self):
        return self._package
    
    def from_package(self):
        return self._from_package

class InstallCommand(Command):
    
    def __init__(self, group):
        super(InstallCommand, self).__init__(id="install", help="Install package", group=group)

        # add command arguments
        self.parser().add_default_args()
        self.parser().add_argument('-l', '--link', action='store_true', help='Link files for dev module', default=False)
        self.parser().add_argument('-g', '--global', action='store_true', help='Install module in user space', default=False)
        self.parser().add_argument('-r', '--reinstall', action='store_true', help='Force reinstall module if alredy exists', default=False)
        self.parser().add_argument('--save', action='store_true', help='Update project package list', default=False)
        self.parser().add_argument('--save-dev', action='store_true', help='Update project dev package list', default=False)

        self.parser().add_argument('NAME', nargs='*', help='Packages', default=[])
        self.parser().set_defaults(func=self.execute)

    def init_parser(self):
        pass
    
    def execute(self, config, args):
        project_config = None
        if os.path.exists("army.toml"):
            try:
                # load project configuration
                project_config = load_project(config)
                config = project_config
            except Exception as e:
                print_stack()
                log.error(e)
                exit(1  )
         
        if project_config is None:
            log.debug(f"no project loaded")
#             project_config = config
         
        # build repositories list
        repositories = load_repositories(config, prefix)
 
        packages = []
    
        if len(args.NAME)==0:
            if project_config is None:
                log.error(f"{os.getcwd()}: army.toml not found")
                exit(1)

            for package in project_config.project.dependencies:
                pkg = self.find_package(package.value(), repositories)
                packages.append(PackageDependency(pkg))

            for package in project_config.project.get("dev-dependencies"):
                pkg = self.find_package(package.value(), repositories)
                packages.append(PackageDependency(pkg))
                
            for plugin in project_config.plugin:
                pkg = self.find_package(plugin, repositories)
                packages.append(PackageDependency(pkg))
        else:
            for package in args.NAME:
                pkg = self.find_package(package, repositories)
                packages.append(PackageDependency(pkg))

        # locate install folder
        if getattr(args, 'global'):
            path = os.path.join(prefix, "~/.army/dist/")
        else:
            path = "dist"
        
        link = False
        if args.link:
            link = True
            
        force = False
        if args.reinstall:
            force = True
    
        dependencies = []
        while(len(packages)>0):
            # get dependencies fro top level package to end level
            package_dep = packages.pop(0)
            package = package_dep.package()

            try:
                # load package
                package.load()
            except Exception as e:
                print_stack()
                log.error(e)
                exit(1)
            
            # dependency treated ok, append to list
            dependencies.append(package_dep)
            
            # append dependencies to list
            for dependency in package.dependencies():
                pkg = self.find_package(dependency, repositories)
                dep_pkg = PackageDependency(package=pkg, from_package=package)
                self.check_dependency_version_conflict(dependencies, dep_pkg)
                packages.append(dep_pkg)

            # append dependencies to list
            for dependency in package.dev_dependencies():
                pkg = self.find_package(dependency, repositories)
                dep_pkg = PackageDependency(package=pkg, from_package=package)
                self.check_dependency_version_conflict(dependencies, dep_pkg)
                packages.append(dep_pkg)
        
            # append plugins to list
            for dependency in package.plugins():
                pkg = self.find_package(dependency, repositories)
                dep_pkg = PackageDependency(package=pkg, from_package=package)
                self.check_dependency_version_conflict(dependencies, dep_pkg)
                packages.append(dep_pkg)
        
        dependencies.reverse()
        for dependency in dependencies:
            install = False
            installed_package = self.find_installed_package(dependency.package(), path)
            if installed_package:
                if force==True:
                    log.info(f"reinstall package {dependency.package()}")
                    install = True

                    def rmtree_error(func, path, exc_info):
                        print(exc_info)
                        exit(1)
                    shutil.rmtree(os.path.join(path, installed_package), onerror=rmtree_error)
                else:
                    print(f"package {dependency.package()} already installed, skip")
                    install = False
            else:
                install = True
                
            if install==True:
                if dependency.package().repository().DEV==True:
                    dependency.package().install(path=os.path.join(path, str(dependency.package())), link=link)
                else:
                    # link mode is only possible with repository DEV
                    dependency.package().install(path=os.path.join(path, str(dependency.package())), link=False)
        
        # TODO save and save-dev
        
    def check_dependency_version_conflict(self, dependencies, dependency):
        for dep in dependencies:
            if dep.package().name()==dependency.package().name() and dep.package().version()!=dependency.package().version():
                msg = f"'{dependency.package().name()}': version conflicts: "
                if dependency.from_package() is None:
                    msg += f"'{dependency.package().version()}' from project"
                else:
                    msg += f"'{dependency.package().version()}' from '{dependency.from_package().name()}'"
                msg += " conflicts with "
                if dep.from_package() is None:
                    msg += f"'{dep.package().version()}' from project"
                else:
                    msg += f"'{dep.package().version()}' from '{dep.from_package().name()}'"
                log.error(msg)
                exit(1)

    def find_package(self, package, repositories):
        # search for module in repositories
        for repo in repositories:
            res = repo.search(package, fullname=True)
            if len(res)>0:
                # result can contain only one element as fullname is True
                for package in res:
                    return res[package]
        log.error(f"{package}: package not found")
        exit(1)
    
    def find_installed_package(self, package, path):
        if os.path.exists(path):
            for entry in os.listdir(path):
                if fnmatch.fnmatch(entry, f"{package.name()}:*"):
                    return entry
        return None
    