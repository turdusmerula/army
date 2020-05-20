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


# A command consists of two parts:
# - a command line parser  
# - the command line behavior
# Commands are created by plugins and given to the army core upon initialization
class Command(object):
    
    def __init__(self, id, help, group):
        self._id = id
        self._group = group
        self._parser = group.parser().add_parser(id, help=help)

    def id(self):
        return self._id
    
    def parser(self):
        return self._parser 

    def execute(self, config, args):
        pass
    
#     # map storing all command instances
#     # key: command name
#     # value: an array containing commands by creation order
#     instances = {}
#     
#     def __init__(self, name, plugin, parser, default_args={}):
#         self.name = name
#         self.plugin = plugin
#         self.parser = parser
#         self.default_args = default_args
#         
#         self.childs = []
#         
#     def register(self):
#         if self.name not in Command.instances:
#             Command.instances[self.name] = [self]
#         else:
#             Command.instances[self.name].append(self)
#     
#     @staticmethod
#     def execute(name, args, config, **kwargs):
#         Command.commands[name].entry_point()
# 
#     def add_parent(self, name, config):
#         if name in Command.instances:
#             instances = Command.instances[name]
#         else:
#             return False
#         
#         for instance in instances:
#             found = None
#             for child in instance.childs:
#                 if child.name==self.name:
#                     found = child
#             
#             if found is None:
#                 instance.childs.append(self)
#                 self.plugin.init_parser(instance.parser, config)
#         
#         return True