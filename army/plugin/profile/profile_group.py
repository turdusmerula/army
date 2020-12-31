from army.api.click import verbose_option 
from army import profile
from army import cli
import click

# name='profile', help='Manage profiles
@profile.group(help="Manage profiles")
@verbose_option()
@click.pass_context
def profile(ctx, **kwargs):
    # recopy parent config in context
    ctx.config = ctx.parent.config
    ctx.project = ctx.parent.project
    ctx.target = ctx.parent.target
    ctx.target_name = ctx.parent.target_name
