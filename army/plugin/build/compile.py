from army.api.log import log
from army.api.command import Command
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories

from army.army import prefix

class CompileCommand(Command):
    
    def __init__(self, group):
        super(CompileCommand, self).__init__(id="compile", help="Compile firmware", group=group)

        # add command arguments
        self.parser().add_default_args()
        self.parser().set_defaults(func=self.execute)

    def init_parser(self):
        pass
    
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
    
