import click
import os

class Config(object):
    def __init__(self):
        print("---")

class Command(object):
    def __init__(self, *args, **kwargs):
        print("__init__", args, kwargs)

    def __call__(self, *args, **kwargs):
        print("__call__", args, kwargs)


def dec1(func):
    print("dec1")
    
    def wrapper(*args, **kwargs):
        print("Before calling " + func.__name__)
        res = func(*args, **kwargs)
        print("After calling " + func.__name__)
        return res
    return wrapper

def dec2(func):
    print("dec2", func.__name__)
    
    return func

# def dec2(func):
#     print("dec2")
#     def wrapper(*args, **kwargs):
#         print("Before calling " + func.__name__)
#         res = func(*args, **kwargs)
#         print("After calling " + func.__name__)
#         return res
#     return wrapper
# 
# def _make_command(**kwargs):
#     return Command(**kwargs)
# 
# def command(**kwargs):
#     def decorator(f):
#         print("create command", kwargs)
#         return _make_command
#     
#     return decorator
# 
# def group(**kwargs):
#     return command(**kwargs)



@click.group(chain=True)
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
@click.pass_context
def cli(ctx, **kwargs):
    ctx.config = Config()
    print("cli", ctx.__dict__, cli)
 
@cli.command()
@click.pass_context
# @click.argument('src')
# @click.argument('dest', required=False)
def clean(ctx, **kwargs):
    print("clean", ctx.parent.__dict__, ctx.__dict__, kwargs)
      
@cli.command()
@click.pass_context
@dec2
def build(ctx, *args, **kwargs):
    print("build", ctx.parent.__dict__, ctx.__dict__, kwargs)


@click.command()
@click.pass_context
def flash(ctx, **kwargs):
    print("build", ctx.parent.__dict__, ctx.__dict__, kwargs)

@click.group(invoke_without_command=True, 
             no_args_is_help=False, 
             add_help_option=False, 
             context_settings=dict(
                 resilient_parsing=True, 
                 allow_extra_args=True, 
                 allow_interspersed_args=True))
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
@click.pass_context
def cliinit(ctx, **kwargs):
    ctx.config = Config()
    print("cliinit", ctx.__dict__, kwargs)
    cli.add_command(flash, "flash")
    
if __name__ == '__main__':
    try:
        cliinit()
    except:
        pass
    
    print("init ok")

    cli()
