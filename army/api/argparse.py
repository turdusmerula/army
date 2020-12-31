from army.api.log import log, get_log_level
import army.api.click as click
import os
import sys

groups = {}
sections = {}
commands = {}

class CommandException(Exception):
    def __init__(self, message):
        self.message = message

def create_parser(*args, **kwargs):
    parser = Parser(*args, **kwargs)
    return parser

# # add a new command group
# # @param name group name
# # @param help group message that will be shown in console
# # @param callback function to be called when group match
# # @param parent parent group, by default group is added to the root group
# # @param chain if Trus then commands inside the group can be chained
# def add_group(name, help="", callback=None, parent="army", chain=False):
#     global groups
#     
#     if name in groups:
#         raise CommandException(f"{name}: command group already exists")
#     
#     if parent not in groups:
#         raise CommandException(f"{parent}: command group does not exist")
#         
#     parent_group = groups[parent]
# 
# def add_section():
#     pass
# 
# def add_command():
#     pass


def _print_command_list(commands, indent=0, file=sys.stderr):
    command_list = {}
    
    for command in commands:
        if command.name is not None:
            command_list[command.name] = command
    
    column_name = []
    column_help = []
    
    # order commands by name
    for command in sorted(command_list):
        column_name.append(command)
        column_help.append(command_list[command].help or "")

    if len(column_name)>0:
        max_name = len(max(column_name, key=len))
        max_help = len(max(column_help, key=len))
    
        for i in range(len(column_name)):
            if indent>0:
                print(" ".ljust(indent*4), end='', file=file)
            print(f"{column_name[i].ljust(max_name)}    ", end='', file=file)
            print(f"{column_help[i].ljust(max_help)}", end='', file=file)
            print(file=file)

def _print_option_list(options, indent=0, file=sys.stderr):
    option_list = {}
    
    # add long options
    for option in options:
        if option.name is not None:
            option_list[option.name] = option
        elif option.shortcut is not None:
            option_list[option.shortcut] = option
    
    column_name = []
    column_value = []
    column_help = []
    
    # order commands by name
    for option in option_list:
        option_name = ""
        if option_list[option].name is not None:
            option_name += f"--{option_list[option].name}"
        if option_list[option].shortcut is not None:
            if option_name!="":
                option_name += ", "
            option_name += f"-{option_list[option].shortcut}"
        column_name.append(option_name)
        
        if option_list[option].flag:
            column_value.append("")
        else:
            column_value.append(option_list[option].value)
        
        help = option_list[option].help or ""
        if option_list[option].has_default:
            help += f" ({option_list[option].default})"
        column_help.append(help) 
            
    if len(column_name)>0:
        max_name = len(max(column_name, key=len))
        max_value = len(max(column_value, key=len))
        max_help = len(max(column_help, key=len))
    
        for i in range(len(column_name)):
            if indent>0:
                print(" ".ljust(indent*4), end='', file=file)
            print(f"{column_name[i].ljust(max_name)}", end='', file=file)
            if max_value>0:
                print(f" {column_value[i].ljust(max_value)}    ", end='', file=file)
            print(f"{column_help[i].ljust(max_help)}", end='', file=file)
            print(file=file)


class Parser(object):
    def __init__(self, command=None, callback=None):
        self._command = command
        self._callbacks = []
        self.childs = []

        if callback is not None:
            self._callbacks.append(callback)

    @property
    def command(self):
        if self._command is None and len(sys.argv)>0:
            return os.path.basename(sys.argv[0])
        return self._command

    @property
    def callbacks(self):
        return self._callbacks

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def call_callbacks(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(self, *args, **kwargs)

    def _find_option(self, name=None, shortcut=None):
        if name is not None:
            for child in self.childs:
                if isinstance(child, Option) and child.name is not None and child.name==name:
                    return child
            raise CommandException(f"{self.command}: invalid option --{name}")
       
        if shortcut is not None:
            for child in self.childs:
                if isinstance(child, Option) and child.shortcut is not None and child.shortcut==shortcut:
                    return child
            raise CommandException(f"{self.command}: invalid option -{shortcut}")
    
    def _find_command(self, command_list, name):
        for command in command_list:
            if command.name==name:
                return command
        raise CommandException(f"{self.command}: invalid command {name}")

    def _check_option_shortcut(self, option, values):
        if option.count is not None and option.count!='*':
            if len(values)>option.count:
                raise CommandException(f"{self.command}: -{option.shortcut} has too much values")
    
    def _check_option_name(self, option, values):
        if option.count is not None and option.count!='*':
            if len(values)>option.count:
                raise CommandException(f"{self.command}: --{option.name} has too much values")

    def _parse_shortcut_option(self, option, rarg, argv):
        # if rarg is not None it contains the what is after the shortcut option that could be consumed as option value
        if option.flag==True:
            if rarg is not None:
                return True, [f"-{rarg}", *argv]
            return True, argv
        else:
            if rarg is not None:
                return rarg, argv
            if len(argv)==0:
                raise CommandException(f"{self.command}: -{option.shortcut} requires a value")
            return argv[0], argv[1:]

    def _parse_name_option(self, option, argv):
        # if rarg is not None it contains the what is after the shortcut option that could be consumed as option value
        if option.flag==True:
            return True, argv
        else:
            if len(argv)==0:
                raise CommandException(f"{self.command}: --{option.name} requires a value")
            return argv[0], argv[1:]

    def _recursive_build_command_list(self, parent):
        args = []
        for child in parent.childs:
            if isinstance(child, Command):
                args.append(child)
            elif isinstance(child, Group):
                args += self._recursive_build_command_list(child)
        return args
    
    def _build_command_list(self):
        return self._recursive_build_command_list(self)
    
    def _build_argument_list(self):
        args = []
        for child in self.childs:
            if isinstance(child, Argument):
                args.append(child)
        return args
    
    def _check_arguments(self, arguments):
        for child in self.childs:
            if isinstance(child, Argument) and child not in arguments:
                if child.help is not None:
                    raise CommandException(f"{self.command}: argument {child.help} missing")
                else:
                    raise CommandException(f"{self.command}: argument {child.name} missing")
                    
        for argument in arguments:
            if argument.count is not None and argument.count!='*' and len(arguments[argument])<argument.count:
                if child.help is not None:
                    raise CommandException(f"{self.command}: not enough values for argument {child.help}")
                else:
                    raise CommandException(f"{self.command}: not enough values for argument {child.name}")
    
    def _set_options_defaults(self, options):
        for child in self.childs:
            if isinstance(child, Option) and child.has_default:
                if child not in options:
                    options[child] = []
                    options[child].append(child.default)

    def parse(self, argv):
        command = argv.pop(0)
        
        # list of found options
        options = {}
        # list of found arguments
        arguments = {}
        # found command
        command = None
        
        # indicates we should stop to consider args beginning by - as options
        stop_options = False

        # flatten list of possible arguments / commands
        argument_list = self._build_argument_list()
        command_list = self._build_command_list()
        current_arg = None
        
        while len(argv)>0:
            
            arg = argv.pop(0)
            
            if stop_options==False and arg=="--":
                stop_options = True
            
            elif stop_options==False and arg.startswith("--"):
                # treat long options
                name = arg[2:]
                value = None
                arg = arg[2:]
                if '=' in name:
                    name, value = name.split('=', 1)
                option = self._find_option(name=name)
                if value is None:
                    value, argv = self._parse_name_option(option, argv)
                # callbacks
                option.call_callbacks(value)
                
                # store value
                if option not in options:
                    options[option] = []
                options[option].append(value)
                self._check_option_name(option, options[option])

            elif stop_options==False and arg.startswith("-"):
                # treat short options
                shortcut = arg[1]
                arg = arg[2:]   # consume -x
                option = self._find_option(shortcut=shortcut)
                # option found
                if arg=='':
                    value, argv = self._parse_shortcut_option(option, None, argv)
                else:
                    value, argv = self._parse_shortcut_option(option, arg, argv)
                # callbacks
                option.call_callbacks(value)
                
                # store value
                if option not in options:
                    options[option] = []
                options[option].append(value)
                self._check_option_shortcut(option, options[option])
            
            else:
                # treat arguments then command
                if len(argument_list)>0:
                    if current_arg is None:
                        current_arg = argument_list.pop(0)
                else:
                    if len(command_list)==0:
                        if current_arg is None and len(command_list)==0:
                            raise CommandException(f"{self.command}: unknown parameter '{arg}'")
                    else:
                        command = self._find_command(command_list, arg)
                        
                if current_arg is not None:
                    if current_arg not in arguments:
                        # first time this argument is treated
                        arguments[current_arg] = []
                        arguments[current_arg].append(arg)
                        if current_arg.count is None:
                            # argument is not an array, go to next
                            current_arg = None
                        elif current_arg.count!='*':
                            # argument is a fixed size array
                            if len(arguments[current_arg])>=current_arg.count:
                                current_arg = None

                    else:
                        # check if we should go to next argument
                        if current_arg.count is None:
                            current_arg = None
                        elif current_arg.count=='*':
                            arguments[current_arg].append(arg)
                        else:
                            arguments[current_arg].append(arg)
                            # we are in an array
                            if len(arguments[current_arg])>=current_arg.count:
                                current_arg = None
                
                if command is not None:
                    parser = Parser(command=f"{self.command} {command.name}")
                    parser._callbacks = command._callbacks
                    parser.childs = command.childs
                    argv = parser.parse([command.name, *argv])
                    
        self._check_arguments(arguments)
        self._set_options_defaults(options)
        
        # call parser callback
        callback_dict_args = {}
        callback_kwargs_args = {}
        for option in options:
            name = None
            if option.name is not None:
                name = option.name
            elif option.shortcut is not None:
                name = option.shortcut
            
            if option.count is None:
                callback_dict_args[name] = options[option][-1]
            else:
                callback_dict_args[name] = options[option]
        for argument in arguments:
            if argument.count is None:
                callback_dict_args[argument.name] = arguments[argument][-1]
            else:
                callback_dict_args[argument.name] = arguments[argument]

        self.call_callbacks(**callback_dict_args)
        
        return argv
    
    def _show_usage(self, file=sys.stderr):
        print(f"Usage: {self.command}", end='', file=file)
        
        has_option = False
        has_command = False
        for child in self.childs:
            if isinstance(child, Option):
                has_option = True
            elif isinstance(child, Command):
                has_command = True
        if has_option:
            print(f" [OPTIONS]", end='', file=file)
            

        for child in self.childs:
            if isinstance(child, Argument):
                if child.help is not None:
                    print(f" {child.help}", end='', file=file)
                else:
                    print(f" {child.name}", end='', file=file)
        
        if has_command:
            print(f" COMMAND [ARGS]", end='', file=file)

        print(file=file)
        
    def show_help(self, file=sys.stderr):
        self._show_usage(file)
        
        groups = []
        commands = []
        options = []
        
        for child in self.childs:
            if isinstance(child, Group):
                groups.append(child)
            elif isinstance(child, Command):
                commands.append(child)
            elif isinstance(child, Option):
                options.append(child)
        
        if len(options)>0:
            print("", file=file)
            print("Options:", file=file)
            _print_option_list(options, indent=1, file=file)
            
        for group in groups:
            if group.help is None:
                # add command from hidden groups inside commands
                for child in group.childs:
                    if isinstance(child, Command):
                        commands.append(child)
            else:
                print("", file=file)
                print(f"{group.help}:", file=file)
                group._show_help(indent=1, file=file)

        if len(commands)>0:
            print("", file=file)
            print("Commands:", file=file)
            _print_command_list(commands, indent=1, file=file)

    def add_group(self, *args, **kwargs):
        group = Group(parent=self, *args, **kwargs)
        self.childs.append(group)
        return group

    def add_command(self, *args, **kwargs):
        command = Command(parent=self, *args, **kwargs)
        self.childs.append(command)
        return command
    
    def add_option(self, *args, **kwargs):
        option = Option(parent=self, *args, **kwargs)
        self.childs.append(option)
        return option

    def add_argument(self, *args, **kwargs):
        argument = Argument(parent=self, *args, **kwargs)
        self.childs.append(argument)
        return argument

class Group(object):
    # @param name optional, used to identify group
    # @param help shown help string, if None create a hidden group 
    # @param chain allow group commands to be chained
    def __init__(self, parent, name=None, help=None, chain=False):
        self._parent = parent
        self._name = name
        self._help = help
        self.childs = []

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    @property
    def help(self):
        return self._help

    def _show_help(self, indent=0, file=sys.stderr):
        groups = []
        commands = []
        
        for child in self.childs:
            if isinstance(child, Group):
                groups.append(child)
            elif isinstance(child, Command):
                commands.append(child)
        
        for group in groups:
            if group.help is None:
                # add command from hidden groups inside commands
                for child in group.childs:
                    if isinstance(child, Command):
                        commands.append(child)
            else:
                print("", file=file)
                if indent>0:
                    print(" ".ljust(indent*4), end='', file=file)
                print(f"{group.help}:", file=file)
                group._show_help(indent=1, file=file)

        if len(commands)>0:
            _print_command_list(commands, indent=1, file=file)

    def add_group(self, *args, **kwargs):
        group = Group(parent=self, *args, **kwargs)
        self.childs.append(group)
        return group

    def add_command(self, *args, **kwargs):
        command = Command(parent=self, *args, **kwargs)
        self.childs.append(command)
        return command


class Command(object):
    def __init__(self, parent, name=None, help=None, callback=None):
        self._parent = parent
        self._name = name
        self._help = help
        self._callbacks = []
        self.childs = []
        
        if callback is not None:
            self._callbacks.append(callback)

#         last_varg = parent.childs[-1:][0]
        
        # TODO check that last varg is not a wildcard size array
        # TODO check that last varg is not optional
        # TODO check that last varg is not a command

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    @property
    def help(self):
        return self._help

    @property
    def callbacks(self):
        return self._callbacks

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def call_callbacks(self, *args, **kwargs):
        for callback in self.callbacks:
            callback(self, *args, **kwargs)

    
    def add_group(self, *args, **kwargs):
        group = Group(parent=self, *args, **kwargs)
        self.childs.append(group)
        return group

    def add_command(self, *args, **kwargs):
        command = Command(parent=self, *args, **kwargs)
        self.childs.append(command)
        return command
    
    def add_option(self, *args, **kwargs):
        option = Option(parent=self, *args, **kwargs)
        self.childs.append(option)
        return option

    def add_argument(self, *args, **kwargs):
        argument = Argument(parent=self, *args, **kwargs)
        self.childs.append(argument)
        return argument

class Option(object):

    # @param name optional, long option name
    # @param shortcut optional, shortcut name for option
    # @param help shown help string
    # @param value value description, should be None if option is a flag
    # @param flag if True indicates that option does not take any value
    # @param count if None indicates that option should appear only once, '*' or >=1 indicates that option is a list
    # @param callback callback to call when option is found 
    def __init__(self, parent, name=None, shortcut=None, help=None, value=None, flag=False, count=None, callback=None, **kwargs):
        self._parent = parent
        self._name = name
        self._shortcut = shortcut
        self._help = help
        self._value = value
        self._flag = flag
        self._count = count
        self._callbacks = []
        
        self._default = None
        self._has_default = False
        if "default" in kwargs:
            self._default = kwargs["default"]
            self._has_default = True
        
        if callback is not None:
            self._callbacks.append(callback)

        if shortcut is not None and len(shortcut)!=1:
            raise CommandException(f"{shortcut}: shortcut can only be one letter length")

#         last_varg = parent.childs[-1:][0]
        
        # TODO check that last varg is not a command

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    @property
    def shortcut(self):
        return self._shortcut
    
    @property
    def help(self):
        return self._help

    @property
    def value(self):
        return self._value

    @property
    def flag(self):
        return self._flag

    @property
    def count(self):
        return self._count

    @property
    def default(self):
        return self._default

    @property
    def has_default(self):
        return self._has_default

    @property
    def callbacks(self):
        return self._callbacks

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def call_callbacks(self, value):
        for callback in self.callbacks:
            callback(self, value)

class Argument(object):
    def __init__(self, parent, name=None, help=None, count=None, callback=None):
        self._parent = parent
        self._name = name
        self._help = help
        self._count = count

#         last_varg = parent.childs[-1:][0]
        
        # TODO check that last argument is not a wildcard size array
        # TODO check that last argument is not optional
        # TODO check that last argument is not a command

    @property
    def parent(self):
        return self._parent

    @property
    def name(self):
        return self._name

    @property
    def help(self):
        return self._help

    @property
    def count(self):
        return self._count

    @property
    def callbacks(self):
        return self._callbacks

    def add_callback(self, callback):
        self.callbacks.append(callback)
