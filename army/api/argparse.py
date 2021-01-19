from army.api.log import log, get_log_level
import os
import sys
import copy

class ArgparseException(Exception):
    def __init__(self, message):
        self.message = message

def create_parser(*args, **kwargs):
    parser = Parser(*args, **kwargs)
    return parser


def _print_command_list(commands, indent=0):
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
                print(" ".ljust(indent*4), end='', file=sys.stderr)
            print(f"{column_name[i].ljust(max_name)}    ", end='', file=sys.stderr)
            print(f"{column_help[i].ljust(max_help)}", end='', file=sys.stderr)
            print(file=sys.stderr)

def _print_option_list(options, indent=0):
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
        if option_list[option].has_default and option_list[option].default is not None:
            help += f" ({option_list[option].default})"
        column_help.append(help) 
            
    if len(column_name)>0:
        max_name = len(max(column_name, key=len))
        max_value = len(max(column_value, key=len))
        max_help = len(max(column_help, key=len))
    
        for i in range(len(column_name)):
            if indent>0:
                print(" ".ljust(indent*4), end='', file=sys.stderr)
            print(f"{column_name[i].ljust(max_name)}", end='', file=sys.stderr)
            if max_value>0:
                print(f" {column_value[i].ljust(max_value)}    ", end='', file=sys.stderr)
            else:
                print(f"    ", end='', file=sys.stderr)
            print(f"{column_help[i].ljust(max_help)}", end='', file=sys.stderr)
            print(file=sys.stderr)


class Context(object):
    reserved = ["_values"]
    
    def __init__(self):
        self._values = {}
        
    def __getattr__(self, name):
        if name in Context.reserved:
            return super(Context, self).__getattribute__(name)
        
        if name in super(Context, self).__getattribute__("_values"):
            return super(Context, self).__getattribute__("_values")[name]
        return None

    def __setattr__(self, name, value):
        if name in Context.reserved:
            super(Context, self).__setattr__(name, value)
        super(Context, self).__getattribute__("_values")[name] = value

    def __iter__(self):
        return iter(super(Context, self).__getattribute__("_values"))

    def __deepcopy__(self, memo=None):
        # we do not want to copy context
        return self

class Parser(object):
    
    # Parser is the root of command and options handling
    # @command command name, if not specified equals to argv[0]
    # @need_command if true the parser will throw an error if no command is specified
    # @callback callback to call when command line parsed ok
    def __init__(self, name=None, command=None, need_command=None, callback=None, command_parser=create_parser, context=Context()):
        self._name = name
        if command is None and len(sys.argv)>0:
            self._command = os.path.basename(sys.argv[0])
        else:
            self._command = command
        self._need_command = need_command
        
        self._callbacks = []
        self.childs = []
        self._context = context
        
        self.command_parser = command_parser
        
        if callback is not None:
            self._callbacks.append(callback)

    @property
    def name(self):
        return self._name

    @property
    def command(self):
        return self._command

    @property
    def need_command(self):
        if self._need_command is None:
            # the default behavior is to ask for a command if there is at least one
            return self.has_command()
        return self._need_command

    @property
    def callbacks(self):
        return self._callbacks

    @property
    def context(self):
        return self._context

    def add_callback(self, callback):
        self.callbacks.append(callback)

    def call_callbacks(self, ctx, *args, **kwargs):
        for callback in self.callbacks:
            callback(ctx, *args, **kwargs)

    def _recursive_find_group(self, parent, name):
        for child in parent.childs:
            if isinstance(child, Group) and child.name is not None and child.name==name:
                return child
            elif isinstance(child, Group):
                found = self._recursive_find_group(child, name)
                if found is not None:
                    return found
        return None
    
    # find a non anonymous group inside parser
    def find_group(self, name):
        return self._recursive_find_group(self, name)
            
    # find a non anonymous command inside parser
    def find_command(self, name):
        def recursive_find_command(parent, name):
            for child in parent.childs:
                if isinstance(child, Command) and child.name is not None and child.name==name:
                    return child
                elif isinstance(child, Group):
                    found = recursive_find_command(child, name)
                    if found is not None:
                        return found                
            return None
        return recursive_find_command(self, name)

    def has_command(self):
        commands = self._recursive_build_command_list(self)
        return len(commands)>0
        
    def _find_option(self, name=None, shortcut=None):
        if name is not None:
            for child in self.childs:
                if isinstance(child, Option) and child.name is not None and child.name==name:
                    return child
            raise ArgparseException(f"{self.command}: invalid option --{name}")
       
        if shortcut is not None:
            for child in self.childs:
                if isinstance(child, Option) and child.shortcut is not None and child.shortcut==shortcut:
                    return child
            raise ArgparseException(f"{self.command}: invalid option -{shortcut}")
    
    def _find_command(self, command_list, name):
        for command in command_list:
            if command.name==name:
                return command
        raise ArgparseException(f"{self.command}: invalid command {name}")

    def _check_option_shortcut(self, option, values):
        if option.count is not None and option.count!='*':
            if len(values)>option.count:
                raise ArgparseException(f"{self.command}: -{option.shortcut} has too much values")
    
    def _check_option_name(self, option, values):
        if option.count is not None and option.count!='*':
            if len(values)>option.count:
                raise ArgparseException(f"{self.command}: --{option.name} has too much values")

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
                raise ArgparseException(f"{self.command}: -{option.shortcut} requires a value")
            return argv[0], argv[1:]

    def _parse_name_option(self, option, argv):
        # if rarg is not None it contains the what is after the shortcut option that could be consumed as option value
        if option.flag==True:
            return True, argv
        else:
            if len(argv)==0:
                raise ArgparseException(f"{self.command}: --{option.name} requires a value")
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
                    raise ArgparseException(f"{self.command}: argument '{child.help}' missing")
                else:
                    raise ArgparseException(f"{self.command}: argument '{child.name}' missing")
                    
        for argument in arguments:
            if argument.count is not None and argument.count!='*' and len(arguments[argument])<argument.count:
                if child.help is not None:
                    raise ArgparseException(f"{self.command}: not enough values for argument '{child.help}'")
                else:
                    raise ArgparseException(f"{self.command}: not enough values for argument '{child.name}'")
    
    def _set_options_defaults(self, options):
        for child in self.childs:
            if isinstance(child, Option) and child.has_default:
                if child not in options:
                    options[child] = []
                    options[child].append(child.default)

    def _set_arguments_defaults(self, arguments):
        for child in self.childs:
            if isinstance(child, Argument) and child.count is not None and child.count=='*':
                if child not in arguments:
                    arguments[child] = []

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
                self.context.item = option
                option.call_callbacks(self.context, value)
                
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
                self.context.item = option
                option.call_callbacks(self.context, value)
                
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
                            raise ArgparseException(f"{self.command}: unknown parameter '{arg}'")
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
                    # open a sub parser to treat the command
                    # if the command has sub commands then set the parser to check for command
                    parser = self.command_parser(command=f"{self.command} {command.name}", need_command=command.has_sub_command())
                    parser._callbacks = command._callbacks
                    parser.childs += copy.deepcopy(command.childs)
                    parser._context = self._context
                    if command.parent is not None and isinstance(command.parent, Group) and command.parent.chain==True:
                        # when command is inside a chain then add the command from the chain to the parser
                        # these commands are then optional if the parent command does not contain any command
                        parser.childs.append(command.parent)
                    argv = parser.parse([command.name, *argv])
                    

        self._set_arguments_defaults(arguments)
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

        self.context.item = command
        self.call_callbacks(self.context, **callback_dict_args)
        
        if self.need_command==True and command is None:
            raise ArgparseException(f"{self.command}: command missing")
        
        return argv
    
    def _show_usage(self):
        print(f"Usage: {self.command}", end='', file=sys.stderr)
        
        # flatten list of possible arguments / commands
        argument_list = self._build_argument_list()
        command_list = self._build_command_list()
        
        has_option = False
        for child in self.childs:
            if isinstance(child, Option):
                has_option = True
        if has_option:
            print(f" [OPTIONS]", end='', file=sys.stderr)
            

        for argument in argument_list:
            if argument.help is not None:
                print(f" {argument.help}", end='', file=sys.stderr)
            else:
                print(f" {argument.name}", end='', file=sys.stderr)
        
        if len(command_list)>0:
            if self.need_command==True:
                print(f" COMMAND [ARGS]", end='', file=sys.stderr)
            else:
                print(f" [COMMAND] [ARGS]", end='', file=sys.stderr)
                

        print(file=sys.stderr)
        
    def show_help(self):
        self._show_usage()
        
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
            print("", file=sys.stderr)
            print("Options:", file=sys.stderr)
            _print_option_list(options, indent=1)
            
        for group in groups:
            if group.help is None:
                # add command from hidden groups inside commands
                for child in group.childs:
                    if isinstance(child, Command):
                        commands.append(child)
            else:
                print("", file=sys.stderr)
                print(f"{group.help}:", file=sys.stderr)
                group._show_help(indent=1)

        if len(commands)>0:
            print("", file=sys.stderr)
            print("Commands:", file=sys.stderr)
            _print_command_list(commands, indent=1)

        print("", file=sys.stderr)

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


    def debug_show_childs(self):
        def _recursive_show_childs(tab, parent):
            if hasattr(parent, "childs"):
                for child in parent.childs:
                    print(f"{tab}{child.name} ({child})")
                    _recursive_show_childs(f"{tab}  ", child)
        print(f"{self.name} ({self})")
        _recursive_show_childs("  ", self)
        
class Group(object):
    # @param name optional, used to identify group
    # @param help shown help string, if None create a hidden group 
    # @param chain allow group commands to be chained
    def __init__(self, parent, name=None, help=None, chain=False):
        self._parent = parent
        self._name = name
        self._help = help
        self._chain = chain
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

    @property
    def chain(self):
        return self._chain


    def _show_help(self, indent=0):
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
                print("", file=sys.stderr)
                if indent>0:
                    print(" ".ljust(indent*4), end='', file=sys.stderr)
                print(f"{group.help}:", file=sys.stderr)
                group._show_help(indent=1)

        if len(commands)>0:
            _print_command_list(commands, indent=1)

    # find a non anonymous command inside parser
    def find_command(self, name):
        def recursive_find_command(parent, name):
            for child in parent.childs:
                if isinstance(child, Command) and child.name is not None and child.name==name:
                    return child
                elif isinstance(child, Group):
                    found = recursive_find_command(child, name)
                    if found is not None:
                        return found                
            return None
        return recursive_find_command(self, name)

    def add_group(self, *args, **kwargs):
        group = Group(parent=self, *args, **kwargs)
        self.childs.append(group)
        return group

    def add_command(self, *args, **kwargs):
        command = Command(parent=self, *args, **kwargs)
        self.childs.append(command)
        return command


class Command(object):
    # @param used to identify command
    # @param help shown command help string
    # @param callback callback to call when command is encountered
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

    def call_callbacks(self, ctx, *args, **kwargs):
        for callback in self.callbacks:
            callback(ctx, *args, **kwargs)

    def has_sub_command(self):
        commands = self._recursive_build_command_list(self)
        return len(commands)>0
    
    def _recursive_build_command_list(self, parent):
        args = []
        for child in parent.childs:
            if isinstance(child, Command):
                args.append(child)
            elif isinstance(child, Group):
                args += self._recursive_build_command_list(child)
        return args

    # find a non anonymous command inside parser
    def find_command(self, name):
        def recursive_find_command(parent, name):
            for child in parent.childs:
                if isinstance(child, Command) and child.name is not None and child.name==name:
                    return child
                elif isinstance(child, Group):
                    found = recursive_find_command(child, name)
                    if found is not None:
                        return found                
            return None
        return recursive_find_command(self, name)

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

    def _parser_from_command(self):
        parser = Parser(command=f"{self.name}")
        parser._callbacks = self._callbacks
        parser.childs = self.childs
        if self.parent is not None and isinstance(self.parent, Group) and self.parent.chain==True:
            parser.childs.append(self.parent)
        return parser
    
    def show_help(self):
        parser = self._parser_from_command()
        parser.show_help()

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
            raise ArgparseException(f"{shortcut}: shortcut can only be one letter length")

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

    def call_callbacks(self, ctx, value):
        for callback in self.callbacks:
            callback(ctx, value)

class Argument(object):
    # @param name optional, used to identify argument
    # @param help shown command help string
    # @param count if None indicates single argument, '*' indicates one or more arguments, any number will wait for exact argument count
    # @param callback callback to call when command is encountered
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

