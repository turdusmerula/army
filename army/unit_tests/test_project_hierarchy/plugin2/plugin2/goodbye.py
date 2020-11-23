from army.army import cli
from army.api.click import verbose_option 
import click

@cli.command(name='goodbye', help='Goodbye world')
@verbose_option()
@click.pass_context
def goodbye(ctx, **kwargs):
    print("Goodbye world !")