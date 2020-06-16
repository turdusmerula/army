import click

@click.group()
def cli(**kwargs):
    print("cli", kwargs)


@cli.section("Commands", chain=True)
@click.pass_context
def commands(ctx, **kwargs):
    pass

@commands.command(name='btest1', help='Command btest1')
@click.argument('name')
@click.pass_context
def btest1(ctx, name, **kwargs):
    print("btest1", name)

@commands.command(name='btest2', help='Command btest2')
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
@click.pass_context
def btest2(ctx, v, **kwargs):
    print("btest2", v)

@commands.command(name='btest3', help='Command btest3')
@click.pass_context
def btest3(ctx, **kwargs):
    print("btest3")



@cli.command(help='Command test')
@click.pass_context
def test(ctx, **kwargs):
    print("test")

@cli.section("Management Commands")
@click.pass_context
def management(ctx, **kwargs):
    print("management")

@management.command(help='Command test1')
@click.pass_context
def atest1(ctx, **kwargs):
    print("atest1")

@management.command(help='Command test2')
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
@click.pass_context
def atest2(ctx, **kwargs):
    print("atest2")

@management.command(help='Command test3')
@click.pass_context
def atest3(ctx, **kwargs):
    print("atest3")


if __name__ == '__main__':
    cli()

