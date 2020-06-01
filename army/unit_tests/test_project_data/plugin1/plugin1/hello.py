from army.api.log import log
from army.api.command import Command
from army.api.debugtools import print_stack
from army.api.project import load_project
from army.api.repository import load_repositories
from army.army import prefix

import os
import fnmatch
import shutil

class HelloCommand(Command):
    
    def __init__(self, group):
        super(HelloCommand, self).__init__(id="hello", help="hello command", group=group)

        # add command arguments
        self.parser().add_default_args()
        self.parser().set_defaults(func=self.execute)

    def execute(self, config, args):
        print("Hello !!")
        