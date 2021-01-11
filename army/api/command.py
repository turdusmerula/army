from army.api.log import log, set_log_level
from army.api.argparse import Parser, Group, Command, Option
import os
import sys

army_parser = None

def create_parser(*args, **kwargs):
    parser = ArmyParser(*args, **kwargs)
    return parser

def get_army_parser():
    global army_parser
    if army_parser is None:
        army_parser = create_parser()
    return army_parser
    
    
class CommandException(Exception):
    def __init__(self, message):
        self.message = message

class ArmyBaseParser(Parser):
    instance = create_parser

    def __init__(self, *argv, **kwargs):
        super(ArmyBaseParser, self).__init__(*argv, **kwargs)
        self._log_level = 'fatal'

        self.add_verbose_option()
        

    def add_verbose_option(self):
        self._verbose_option = self.add_option(shortcut="v", help="Activate verbose/debug", flag=True, count=4, callback=self._verbose_option_callback)

    def _verbose_option_callback(self, ctx, value):
        if value==True:
            if self._log_level=='fatal':
                self._log_level = "error"
            elif self._log_level=='error':
                self._log_level = "warning"
            elif self._log_level=='warning':
                self._log_level = "info"
            elif self._log_level=='info':
                self._log_level = "debug"
            else:
                self._log_level = "debug"
                
            set_log_level(self._log_level)


class ArmyParser(ArmyBaseParser):
    instance = create_parser

    def __init__(self, *argv, **kwargs):
        super(ArmyParser, self).__init__(*argv, **kwargs)
        
        self.add_help_option()
        
        self._dependency_group = self.add_group(name="dependency", help="Dependencies Management Commands")

    def add_help_option(self):
        self._help_option = self.add_option(name="help", shortcut="h", help="Show this message and exit", flag=True, callback=self._help_option_callback)
    
    def _help_option_callback(self, ctx, value):
        self.show_help() 
        exit(0)
    
    @property
    def dependency_group(self):
        return self._dependency_group

###################################
### decorators
###################################
debug_decorators = False
def debug(*argv, **kwargs):
    global debug_decorators
    if debug_decorators:
        print(*argv, **kwargs)

def parser(items):
    debug(f"-->> parser", items)
    
    curr_parser = get_army_parser()
    curr_group = curr_parser    # if no group add commands to parser
    curr_command = None
    
    for item in items:
        if callable(item):
            debug("func:", item)
            if curr_command is None:
                raise CommandException(f"no command found")
            else:
                curr_command.add_callback(item)
        else:
            obj, name, argv, kwargs = item
            debug("obj:", obj, name, argv, kwargs)
            if obj==Group:
                debug("group")
                curr_group = curr_parser.find_group(name)
                if curr_group is None:
                    if 'help' in kwargs:
                        curr_group = curr_parser.add_group(name=name, *argv, **kwargs)
                    else:
                        raise CommandException(f"{name}: command group does not exists")
            elif obj==Command:
                debug("command", kwargs)
                curr_command = curr_parser.find_command(name)
                if curr_command is None:
                    if 'help' in kwargs:
                        curr_command = curr_group.add_command(name=name, *argv, **kwargs)
                    else:
                        raise CommandException(f"{name}: command does not exists")
            elif obj==Option:
                debug("option")
            else:
                debug("error")
    
def group(name, *argv, **kwargs):
    debug(f"-->> group {name}")
    def wrapper(obj):
        debug("--- group", obj)
        if isinstance(obj, list):
            return [(Group, name, argv, kwargs), *obj]
        return [(Group, name, argv, kwargs), obj]
    return wrapper

def command(name, *argv, **kwargs):
    debug(f"-->> command {name}")
    def wrapper(obj):
        debug("--- command", obj)
        if isinstance(obj, list):
            return [(Command, name, argv, kwargs), *obj]
        return [(Command, name, argv, kwargs), obj]
    return wrapper

def option(name, *argv, **kwargs):
    debug(f"-->> option {name}")
    def wrapper(obj):
        debug("--- option", obj)
        if isinstance(obj, list):
            return [(Option, name, argv, kwargs), *obj]
        return [(Option, name, argv, kwargs), obj]
    return wrapper
