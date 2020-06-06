# click extentions and helpers
from army.api.log import set_log_level
import click

def verbose_option(*param_decls, **attrs):
    """Adds a ``-v`` option to a command
    option is handled directyl and sets the logger to the right level
    """

    def decorator(f):
        def callback(ctx, param, value):
            verbose = None
            
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
