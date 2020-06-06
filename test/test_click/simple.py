import click

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
def hello(count):
    print("hello")

@click.group(chain=True)
def cli():
    pass

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
def initdb(count):
    print(count)

@click.command()
def dropdb():
    click.echo('Dropped the database')

cli.add_command(initdb)
cli.add_command(dropdb)

if __name__ == '__main__':
    cli()

