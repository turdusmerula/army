from army.api.log import log
from army.api.command import Command
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories

from army.army import prefix

class CompileCommand(Command):
    
    def __init__(self, group):
        super(CompileCommand, self).__init__(id="compile", help="Compile firmware", group=group)
    
        self.add_subparser()

    
    def init_parser(self, parser):
        # add command arguments
        parser.add_default_args()
        parser.add_argument('-d', '--debug', action='store_true', help='Build with debug options')
        parser.add_argument('-j', '--jobs',  type=int, default=1, help='Number of parallel builds (default 1)')

    
    def execute(self, config, args):
        print(f"compile {args}")
        #TODO
        log.info(f"clean {args}")
        
        project_config = None
        try:
            # load project configuration
            project_config = load_project(config)
            config = project_config
        except Exception as e:
            print_stack()
            log.error(e)
            exit(1)
        
        # get target config
        target_name = project_config.get("default-target")
        if project_config.project.target!="":
            target_name = project_config.project.target
        if target_name=="":
            log.error("No target defined")
            exit(1)

        target = None
        try:
            target = project_config.target[target_name]
        except Exception as e:
            print_stack()
            log.error(e)
        
        if target==None:
            print("No target defined")
            exit(1)
    
