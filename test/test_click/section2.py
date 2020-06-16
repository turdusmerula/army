import click

@click.group()
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
def cli(**kwargs):
    print(kwargs)

@cli.section(name="Management Commands")
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
def cli1(**kwargs):
    print(kwargs)

@cli.section(name="Commands", chain=True)
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
def cli2(**kwargs):
    print(kwargs)

@cli1.command(help='Install package')
@click.option('-l', '--link', help='Link files instead of copy (local repository only)', is_flag=True)
@click.option('-g', '--global', help='Install module in user space', is_flag=True)
@click.option('-r', '--reinstall', help='Force reinstall module if already exists', is_flag=True)
@click.pass_context
def cli1test1(ctx, name, link, reinstall, **kwargs):
    pass

@cli1.command(help='Install package')
@click.option('-l', '--link', help='Link files instead of copy (local repository only)', is_flag=True)
@click.option('-g', '--global', help='Install module in user space', is_flag=True)
@click.option('-r', '--reinstall', help='Force reinstall module if already exists', is_flag=True)
@click.pass_context
def cli1test2(ctx, name, link, reinstall, **kwargs):
    pass

@cli1.command(help='Install package')
@click.option('-l', '--link', help='Link files instead of copy (local repository only)', is_flag=True)
@click.option('-g', '--global', help='Install module in user space', is_flag=True)
@click.option('-r', '--reinstall', help='Force reinstall module if already exists', is_flag=True)
@click.pass_context
def cli1test3(ctx, name, link, reinstall, **kwargs):
    pass

@cli2.command(help='Install package')
@click.option('-l', '--link', help='Link files instead of copy (local repository only)', is_flag=True)
@click.option('-g', '--global', help='Install module in user space', is_flag=True)
@click.option('-r', '--reinstall', help='Force reinstall module if already exists', is_flag=True)
# @click.option('--save', help='Update project package list', is_flag=True)    # TODO
@click.argument('name', nargs=-1)
@click.pass_context
def cli2test1(ctx, name, link, reinstall, **kwargs):
    pass

@cli2.command(help='Install package')
@click.option('-l', '--link', help='Link files instead of copy (local repository only)', is_flag=True)
@click.option('-g', '--global', help='Install module in user space', is_flag=True)
@click.option('-r', '--reinstall', help='Force reinstall module if already exists', is_flag=True)
# @click.option('--save', help='Update project package list', is_flag=True)    # TODO
@click.argument('name', nargs=-1)
@click.pass_context
def cli2test2(ctx, name, link, reinstall, **kwargs):
    pass

@cli2.command(help='Install package')
@click.option('-l', '--link', help='Link files instead of copy (local repository only)', is_flag=True)
@click.option('-g', '--global', help='Install module in user space', is_flag=True)
@click.option('-r', '--reinstall', help='Force reinstall module if already exists', is_flag=True)
# @click.option('--save', help='Update project package list', is_flag=True)    # TODO
@click.argument('name', nargs=-1)
@click.pass_context
def cli2test3(ctx, name, link, reinstall, **kwargs):
    pass

if __name__ == '__main__':
    cli()

