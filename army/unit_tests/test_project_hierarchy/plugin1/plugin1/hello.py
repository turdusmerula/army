from army.army import cli
from army.api.click import verbose_option 
import click

@cli.command(name='hello', help='Hello world')
@verbose_option()
@click.pass_context
def hello(ctx, **kwargs):
    print("Hello world !")