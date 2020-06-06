import click

@click.command()
@click.option('--count', default=1, help='Number of greetings.')
def hello(count):
    print("hello")

if __name__ == '__main__':
    hello()

