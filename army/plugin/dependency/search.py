from army.api.command import parser, group, command, option, argument
from army.api.debugtools import print_stack
from army.api.log import log
from army.api.repository import load_repositories
from army.api.version import VersionRange
import os
import sys

# TODO: implement multiple search criteria

@parser
@group(name="dependency")
@command(name='search', help='Search package in repositories')
@option(name="all", shortcut="a", flag=True, default=False, help="Show all matches")
@argument(name='name')
def search(ctx, name, all, **kwargs):
    log.info(f"army search")
        
    # load configuration
    config = ctx.config
    
    # build repositories list
    repositories = load_repositories(config)
    packages = {}
    
    s_name = None
    s_version = None
    s_repository = None
    
    chunks = name.split('@')
    if len(chunks)==1:
        s_name = name
    elif len(chunks)==2:
        try:
            # check chunks[1] is a valid version range
            VersionRange([])[chunks[1]]
            s_name = chunks[0]
            s_version = chunks[1]
        except Exception as e:
            s_repository = chunks[0]
            s_name = chunks[1]
    elif len(chunks)==3:
        s_repository = chunks[0]
        s_name = chunks[1]
        s_version = chunks[2]
    else:
        print(f"{name}: naming error", file=sys.stderr)
        exit(1)
        
    for r in repositories:
        if s_repository is not None and s_repository!=r.name:
            continue
        
        res = r.search(s_name, s_version)
        if len(res)>0:
            for pkg in res:
                for version in res[pkg]:
                    if pkg not in packages:
                        if all==True:
                            packages[pkg] = {}
                        else:
                            packages[pkg] = []
                    if all==True:
                        if r.name not in packages[pkg]:
                            packages[pkg][r.name] = []
                        packages[pkg][r.name].append(version)
                    else:
                        packages[pkg].append(version)

    # only keep higher version for each package
    packages = filter(packages)
    
    if len(packages)==0:
        print(f'No matches found for "{name}"', file=sys.stderr)
        return
 
    column_repo = ['repository']
    column_package = ['package']
    column_version = ['version']
    column_description = ['description']
#
    for package in packages:
        for version in packages[package]:
            column_repo.append(version.repository.name)
            column_package.append(version.name)
            column_version.append(str(version.version))
            column_description.append(version.description)
  
    max_repo = len(max(column_repo, key=len))
    max_package = len(max(column_package, key=len))
    max_version = len(max(column_version, key=len))
    max_description = len(max(column_description, key=len))
  
    for i in range(len(column_repo)):
        print(f"{column_package[i].ljust(max_package)} | ", end='')
        print(f"{column_version[i].ljust(max_version)} | ", end='')
        print(f"{column_repo[i].ljust(max_repo, ' ')} | ", end='')
        print(f"{column_description[i].ljust(max_version)}", end='')
        print()

def filter(packages):
    res = {}
    
    def get_higher_version(packages):
        versions = []
        for package in packages:
            versions.append(package.version)
        range = VersionRange(versions=versions)
        max = range.max()
        for package in packages:
            if package.version==max:
                return package
        return None
    
    for package in packages:
        res[package] = []
        if isinstance(packages[package], dict):
            for versions in packages[package]:
                res[package].append(get_higher_version( packages[package][versions]))
        else:
            res[package].append(get_higher_version(packages[package]))
    
    return res
