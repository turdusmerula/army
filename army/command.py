
def register_command():
    pass


class CommandException(Exception):
    def __init__(self, message):
        self.message = message

class Command(object):
    instances = {}
    
    def __init__(self, name, plugin, parser, default_args={}):
        self.name = name
        self.plugin = plugin
        self.parser = parser
        self.default_args = default_args
        
        self.childs = []
        
    def register(self):
        if self.name not in Command.instances:
            Command.instances[self.name] = [self]
        else:
            Command.instances[self.name].append(self)
    
    @staticmethod
    def execute(name, args, config, **kwargs):
        Command.commands[name].entry_point()

    def add_parent(self, name, config):
        if name in Command.instances:
            instances = Command.instances[name]
        else:
            return False
        
        for instance in instances:
            found = None
            for child in instance.childs:
                if child.name==self.name:
                    found = child
            
            if found is None:
                instance.childs.append(self)
                self.plugin.init_parser(instance.parser, config)
        
        return True