import click
import os


class Config(object):
    def __init__(self):
        print("---")



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
def build(ctx, **kwargs):
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

@cliinit.command()
@click.pass_context
def dummy(ctx, **kwargs):
    print("dummy", ctx.parent.__dict__, ctx.__dict__, kwargs)
    
if __name__ == '__main__':
    try:
        cliinit()
    except:
        pass
    
    print("init ok")

    cli()
