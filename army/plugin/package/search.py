from army.api.log import log
from army.api.command import Command
from config import load_project
from debugtools import print_stack
from repository import load_repositories

class SearchCommand(Command):
    
    def __init__(self, group):
        super(SearchCommand, self).__init__(id="search", help="Search package in repositories", group=group)

        # add command arguments
        self.parser().add_default_args()
        self.parser().add_argument('NAME', help='Module name')
        self.parser().set_defaults(func=self.execute)

    def init_parser(self):
        pass
    
    def execute(self, args, config, **kwargs):
        pass
#         try:
#             # load project configuration
#             config = load_project(config)
#             if not config:
#                 print("army: not a project")
#         except Exception as e:
#             log.error(f"army: {e}")
#             print_stack()
#             return
#             
#         name = args.NAME
#             
#         # build repositories list
#         repositories = load_repositories(config)
#         
#         res = {}
#         
#         for r in repositories:
#             repo_config = r['config']
#             repo = r['repo']
#             modules = repo.search(name)
#             if len(modules)>0:
#                 res[repo] = modules
#                  
#         if len(res)==0:
#             print(f'No matches found for "{name}"')
#             return
#     
#         column_repo = ['repository']
#         column_module = ['module']
#         column_version = ['version']
#         column_description = ['description']
#         
#         for r in res:
#             repo = res[r]
#             for module in repo:
#     
#                 column_repo.append(r.name)
#                 column_module.append(module['name'])
#                 column_version.append(module['version'])
#                 column_description.append(module['info']['description'])
#     
#         max_repo = len(max(column_repo, key=len))
#         max_module = len(max(column_module, key=len))
#         max_version = len(max(column_version, key=len))
#     
#         for i in range(len(column_repo)):
#             print(f"{column_repo[i].ljust(max_repo, ' ')}|{column_module[i].ljust(max_module)}|{column_version[i].ljust(max_version)}|{column_description[i]}")
