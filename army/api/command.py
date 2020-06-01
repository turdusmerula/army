import army.api.extargparse

class CommandGroupException(Exception):
    def __init__(self, message):
        self.message = message

class CommandException(Exception):
    def __init__(self, message):
        self.message = message


class CommandGroup(object):
    _root = None
    
    def __init__(self, id, title, parser=None):
        self._id = id
        self._title = title
        
        # commands inside group
        self._commands = {}
        # subgroups 
        self._subgroups = {}
    
        # parser for group
        self._parser = parser

    @staticmethod
    def init_root(id, title, parser):
        CommandGroup._root = CommandGroup(id, title, parser)
        
    @staticmethod
    def root():
        return CommandGroup._root
    
    def id(self):
        return self._id
    
    def title(self):
        return self._title
    
    def parser(self):
        return self._parser

    def get_subgroup(self, id):
        if id in self._subgroups:
            return self._subgroups[id]
        return None
            
    def add_subgroup(self, group):
        if group.id() in self._subgroups:
            raise CommandGroupException(f"Group {group.id()} already in group {self._id}")
        
        group._parser = self._parser.add_parser_group(title=group._title, id=group._id)
        self._subgroups[group.id()] = group
        return group
    
    def add_command(self, command):
        if command.id() not in self._commands:
            self._commands[command.id()] = [command]
        else:
            self._commands[command.id()].append(command)

        if command.subparser():
            command.subparser.
    def find_command(self, id):
        if id in self._commands:
            return self._commands[id]
        return None

    def command_executable_after(self, leftid, rightid):
        if leftid in self._executable_after:
            if rightid not in self._executable_after[leftid]:
                self._executable_after[leftid] = [rightid]
        else:
            self._executable_after[leftid].append(rightid)

# A command consists of two parts:
# - a command line parser  
# - the command line behavior
# Commands are created by plugins and given to the army core upon initialization
class Command(object):
    
    def __init__(self, id, help, group):
        self._id = id
        self._group = group
        self._parser = group.parser().add_parser(id, help=help)
        self._subparser = None
        
        self.parser().set_defaults(func=self._execute)
        self._group.add_command(self)
        
    def id(self):
        return self._id
    
    def parser(self):
        return self._parser 

    def subparser(self):
        return self._subparser
    
    def _build_subparser(self):
        pass
    
    # execute the command defined by id
    # a command can be overriden, last to be defined is executed
    def _execute(self, config, args):
        command = self._group.find_command(self._id)
        if command:
            command[len(command)-1].execute(config, args)

    # override for command code
    def execute(self, config, args):
        pass
    
    def add_subparser(self):
        self._subparser = self._parser.add_subparsers(metavar='COMMAND', title=None, description=None, help=None, parser_class=army.api.extargparse.ArgumentParser, required=False)
        return self._subparser

    def _action(self, **kwargs):
        print("****", kwargs)
    