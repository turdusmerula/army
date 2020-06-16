# click extentions and helpers
from army.api.log import set_log_level

import click
from army.api.click.core import Section

def verbose_option(*param_decls, **attrs):
    """Adds a ``-v`` option to a command
    option is handled directyl and sets the logger to the right level
    """

    def decorator(f):
        def callback(ctx, param, value):
            verbose = None
            
            # init verbose level from parent config if exists
            if ctx.parent and ctx.parent.config:
                verbose = ctx.parent.config.verbose
            
            set_log_level(verbose)
            
            if value:
                if len(value)==1:
                    set_log_level('error')
                elif len(value)==2:
                    set_log_level('warning')
                elif len(value)==3:
                    set_log_level('info')
                else:
                    set_log_level('debug')

        attrs.setdefault("is_flag", True)
        attrs.setdefault("multiple", True)
        attrs.setdefault("help", "Activate verbose/debug mode")
        attrs["callback"] = callback
        return click.option(*(param_decls or ("-v",)), **attrs)(f)

    return decorator

def section(name=None, **attrs):
    """Creates a new :class:`Section` with a function as callback.  This
    works otherwise the same as :func:`command` just that the `cls`
    parameter is set to :class:`Group`.
    """
    attrs.setdefault("cls", Section)
    return click.command(name, **attrs)


def _check_section_params(cmd):
    if not isinstance(cmd, Section) or len(cmd.params)==0:
        return
    
    raise RuntimeError(
        f"Section '{cmd.name}' can not have any parameter as they would be ignored."
    )
