import click

@click.group(chain=True)
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
def cli(**kwargs):
    print(kwargs)


@cli.command('c1')
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
@click.option('-s', '--string-to-echo')
def c1(**kwargs):
    print('c1 called', kwargs)


@cli.command('c2')
@click.option('-v', help='Activate verbose/debug mode', is_flag=True, multiple=True)
def c2(**kwargs):
    print('c2 called')

if __name__ == '__main__':
    cli()

