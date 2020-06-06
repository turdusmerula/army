import click
import os


class Repo(object):
    def __init__(self):
        print("---")

@click.group()
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
@click.pass_context
def cli(ctx, **kwargs):
    ctx.obj = Repo()
    print("cli", ctx)


### Build group
@cli.group(chain=True)
def cli_build( **kwargs):
    print("cli_build")

@cli_build.command()
# @click.argument('src')
# @click.argument('dest', required=False)
def clean(**kwargs):
    print("clean")
    
@cli_build.command()
def build():
    print("build")

# ### Image group
# @cli.group()
# @cli.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
# @cli.pass_context
# def cli_image(ctx, **kwargs):
#     ctx.obj = Repo()
#     print("++", ctx)
# 
# @cli_image.command()
# def image():
#     print("image")
#     cli2()
#     
# @cli.group(chain=True)
# def cli2(ctx, **kwargs):
#     ctx.obj = Repo()
#     print("++", ctx)
# 
# @cli2.command()
# def remove():
#     print("remove")

if __name__ == '__main__':
    cli()

