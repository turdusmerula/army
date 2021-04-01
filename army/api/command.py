from army.api.log import log, set_log_level
from army.api.argparse import Parser, Group, Command, Option, Argument
import os
import sys

army_parser = None

def create_parser(*args, **kwargs):
    parser = ArmyParser(*args, **kwargs)
    return parser

def get_army_parser():
    global army_parser
    if army_parser is None:
        army_parser = create_parser(name="army")
    return army_parser
    
    
class CommandException(Exception):
    def __init__(self, message):
        self.message = message

class ArmyBaseParser(Parser):
    def __init__(self, *argv, **kwargs):
        super(ArmyBaseParser, self).__init__(*argv, **kwargs)


class ArmyParser(ArmyBaseParser):
    def __init__(self, *argv, **kwargs):
        super(ArmyParser, self).__init__(*argv, **kwargs, command_parser=create_parser)

        self._log_level = 'fatal'
        
        self._dependency_group = self.add_group(name="dependency", help="Dependency Management Commands")

        self.add_verbose_option()
        self.add_help_option()

    @property
    def dependency_group(self):
        return self._dependency_group

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

    def add_help_option(self):
        self._help_option = self.add_option(name="help", shortcut="h", help="Show this message and exit", flag=True, callback=self._help_option_callback)
    
    def _help_option_callback(self, ctx, value):
        self.show_help() 
        exit(0)

    @property
    def log_level(self):
        return self._log_level
    
    @log_level.setter
    def log_level(self, value):
        self._log_level = value
        set_log_level(self._log_level)
        

###################################
### decorators
###################################
_debug_decorators = False
def _debug(*argv, **kwargs):
    global _debug_decorators
    if _debug_decorators:
        print(*argv, **kwargs)

def parser(items):
    _debug(f"-->> parser", items)
    
    obj_stack = [get_army_parser()]
    
#     curr_parser = get_army_parser()
#     curr_group = curr_parser    # if no group add commands to parser
#     curr_command = None
    
    for item in items:
        _debug("##", obj_stack, obj_stack[-1])
        if callable(item):
            _debug("func:", item)
            obj_stack[-1].add_callback(item)
        else:
            obj, name, argv, kwargs = item
            _debug("obj:", obj, name, argv, kwargs)
            if obj==Group:
                _debug("group")
                curr_obj = obj_stack[-1].find_group(name)
                if curr_obj is None:
                    if 'help' in kwargs:
                        curr_obj = obj_stack[-1].add_group(name=name, *argv, **kwargs)
                        obj_stack.append(curr_obj)
                    else:
                        raise CommandException(f"{name}: command group does not exists")
                else:
                    obj_stack.append(curr_obj)
            elif obj==Command:
                _debug("command", kwargs)
                curr_obj = obj_stack[-1].find_command(name)
                if curr_obj is None:
                    if 'help' in kwargs:
                        curr_obj = obj_stack[-1].add_command(name=name, *argv, **kwargs)
                        obj_stack.append(curr_obj)
                    else:
                        raise CommandException(f"{name}: command does not exists")
                else:
                    obj_stack.append(curr_obj)
            elif obj==Option:
                _debug("option")
                obj_stack[-1].add_option(name=name, *argv, **kwargs)
            elif obj==Argument:
                obj_stack[-1].add_argument(name=name, *argv, **kwargs)
                _debug("argument")
            else:
                _debug("error")
    
def group(name, *argv, **kwargs):
    _debug(f"-->> group {name}")
    def wrapper(obj):
        _debug("--- group", obj)
        if isinstance(obj, list):
            return [(Group, name, argv, kwargs), *obj]
        return [(Group, name, argv, kwargs), obj]
    return wrapper

def command(name, *argv, **kwargs):
    _debug(f"-->> command {name}")
    def wrapper(obj):
        _debug("--- command", obj)
        if isinstance(obj, list):
            return [(Command, name, argv, kwargs), *obj]
        return [(Command, name, argv, kwargs), obj]
    return wrapper

def option(name, *argv, **kwargs):
    _debug(f"-->> option {name}")
    def wrapper(obj):
        _debug("--- option", obj)
        if isinstance(obj, list):
            return [(Option, name, argv, kwargs), *obj]
        return [(Option, name, argv, kwargs), obj]
    return wrapper

def argument(name, *argv, **kwargs):
    _debug(f"-->> argument {name}")
    def wrapper(obj):
        _debug("--- argument", obj)
        if isinstance(obj, list):
            return [(Argument, name, argv, kwargs), *obj]
        return [(Argument, name, argv, kwargs), obj]
    return wrapper
