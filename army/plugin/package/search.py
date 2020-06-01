from army.api.log import log
from army.api.command import Command
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories

from army.army import prefix

class SearchCommand(Command):
    
    def __init__(self, group):
        super(SearchCommand, self).__init__(id="search", help="Search package in repositories", group=group)

        # add command arguments
        self.parser().add_default_args()
        self.parser().add_argument('NAME', help='Package name')
        self.parser().set_defaults(func=self.execute)

    def execute(self, config, args):
        log.info(f"search {args}")
        
        main_config = config
        
        project_config = None
        try:
            # load project configuration
            project_config = load_project(config)
        except Exception as e:
            pass
        
        if project_config is None:
            log.debug(f"no project loaded")
            project_config = config

        name = args.NAME
        log.debug(f"search {name}")
        
        # build repositories list
        repositories = load_repositories(config, prefix)
        packages = []
         
        for r in repositories:
            res = r.search(name)
            if len(res)>0:
                for pkg in res:
                    packages.append(res[pkg])

        if len(packages)==0:
            print(f'No matches found for "{name}"')
            return
     
        column_repo = ['repository']
        column_package = ['package']
        column_version = ['version']
        column_description = ['description']
#
        for package in packages:
            column_repo.append(package.repository().name())
            column_package.append(package.name())
            column_version.append(str(package.version()))
            column_description.append(package.description())
      
        max_repo = len(max(column_repo, key=len))
        max_package = len(max(column_package, key=len))
        max_version = len(max(column_version, key=len))
      
        for i in range(len(column_repo)):
            print(f"{column_repo[i].ljust(max_repo, ' ')} | {column_package[i].ljust(max_package)} | {column_version[i].ljust(max_version)} | {column_description[i]}")
