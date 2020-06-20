# click extentions and helpers
from army.api.log import set_log_level

import click

# utility tool to add member methods to a class
from functools import wraps
def add_method(cls):
    def decorator(func):
        @wraps(func) 
        def wrapper(self, *args, **kwargs): 
            return func(self, *args, **kwargs)
        setattr(cls, func.__name__, wrapper)
        # Note we are not binding func, but wrapper which accepts self but does exactly the same as func
        return func # returning func means func can still be used normally
    return decorator


def _check_section_params(cmd):
    if not isinstance(cmd, Section) or len(cmd.params)==0:
        return
    
    raise RuntimeError(
        f"Section '{cmd.name}' can not have any parameter as they would be ignored."
    )

@add_method(click.MultiCommand)
def format_commands(self, ctx, formatter):
    """Extra format methods for multi methods that adds all the commands
    after the options.
    """
    default_section = "Commands"
    
    sections = {}
    # add default section
    sections["Commands"] = []
    for subcommand in self.list_commands(ctx):
        cmd = self.get_command(ctx, subcommand)
        # What is this, the tool lied about a command.  Ignore it
        if cmd is None:
            continue
        if cmd.hidden:
            continue
        
        if isinstance(cmd, Section):
            # add section subcommands
            sections[cmd.name] = []
            for sxnsubcommand in cmd.list_commands(ctx):
                sxncmd = cmd.get_command(ctx, sxnsubcommand)
                # What is this, the tool lied about a command.  Ignore it
                if sxncmd is None:
                    continue
                if sxncmd.hidden:
                    continue
                
                sections[cmd.name].append((sxnsubcommand, sxncmd))
        else:
            sections[default_section].append((subcommand, cmd))
    
    # allow for 3 times the default spacing
    for section in sections:
        commands = sections[section]
        
        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                rows.append((subcommand, help))

            if rows:
                with formatter.section(section):
                    formatter.write_dl(rows)


@add_method(click.MultiCommand)
def resolve_command(self, ctx, args):
    cmd_name = click.utils.make_str(args[0])
    original_cmd_name = cmd_name

    # Get the command
    cmd = self.get_command(ctx, cmd_name)
    
    if isinstance(cmd, Section):
        # in case we find a section we do not consume argument, it will be
        # consumed later by the section
        return cmd_name, cmd, args
    
    # If we can't find the command but there is a normalization
    # function available, we try with that one.
    if cmd is None and ctx.token_normalize_func is not None:
        cmd_name = ctx.token_normalize_func(cmd_name)
        cmd = self.get_command(ctx, cmd_name)

    # If we don't find the command we want to show an error message
    # to the user that it was not provided.  However, there is
    # something else we should do: if the first argument looks like
    # an option we want to kick off parsing again for arguments to
    # resolve things like --help which now should go to the main
    # place.
    if cmd is None and not ctx.resilient_parsing:
        if click.parser.split_opt(cmd_name)[0]:
            self.parse_args(ctx, ctx.args)
        ctx.fail(f"No such command '{original_cmd_name}'.")

    return cmd_name, cmd, args[1:]


@add_method(click.Group)
def section(self, *args, **kwargs):
    """A shortcut decorator for declaring and attaching a section to
    the group.  This takes the same arguments as :func:`group` but
    immediately registers the created command with this instance by
    calling into :meth:`add_command`.
    """
    from .decorators import section

    def decorator(f):
        cmd = section(*args, **kwargs)(f)
        self.add_command(cmd)
        return cmd

    return decorator

@add_method(click.Group)
def get_command(self, ctx, cmd_name):
    cmd = self.commands.get(cmd_name)
    if cmd is None:
        # look if there is any section containing the command
        for section in self.commands:
            if isinstance(self.commands[section], Section) and self.commands[section].get_command(ctx, cmd_name):
                return self.commands[section]
    return cmd

@add_method(click.Group)
def list_commands(self, ctx):
    return sorted(self.commands)

class Section(click.Group):
    """A section allows a command to split subcommands into categories attached. This can be seen
    as creating an anonymous group of subcommands

    :param commands: a dictionary of commands.
    """

    def __init__(
        self,
        name=None,
        **attrs,
    ):
        super(Section, self).__init__(name, **attrs)

    def get_params(self, ctx):
        # TODO this check is too late, should appear when argument is added
        _check_section_params(self)
        return super(Section, self).get_params(ctx)

    def get_command(self, ctx, cmd_name):
        return self.commands.get(cmd_name)

    def list_commands(self, ctx):
        return sorted(self.commands)
