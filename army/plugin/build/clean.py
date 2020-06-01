from army.api.log import log
from army.api.command import Command
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.army import prefix
import os
import shutil

class CleanCommand(Command):
    
    def __init__(self, group):
        super(CleanCommand, self).__init__(id="clean", help="Clean build results", group=group)

        # add command arguments
        self.parser().add_default_args()
        self.parser().set_defaults(func=self.execute)

    def init_parser(self):
        pass
    
    def execute(self, config, args):
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
            
        folder = 'output'
        log.info(f"Remove folder '{folder}'")
        
        if os.path.exists('output')==True:
            shutil.rmtree('output')
