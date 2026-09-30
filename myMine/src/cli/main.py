import click

# Functions to have
## Start
### A function to start the main server
## Open (or call start if down)
### A function to open the server
## Kill
### A function to kill the server

# Possible functions to have
## It's up ?
'''
python click basic body

@click.command() # Functions decorated with this becomes a callable script
@click.option('--count', default=1, help='Number of greetings.')
@click.option('--name', prompt='Your name', help='The person to greet')
def hello(count, name):
    """
    Simple program that greets NAME for a total of COUNT times

    """
    for x in range(count):
        click.echo(f"Hello {name}!")
'''


def start(): ...


@click.command()
def bee():
    # Checks if process is runing
    # If not:
    # call start then open
    # If is:
    # open
    ...


@click.command()
def killbee():
    # Checks if process is runing
    # If is:
    # kill the process
    # If not:
    # do nothing
    ...


if __name__ == "__main__":
    """this is a temp format for development purpose. After the CLI is finished and goes to production this will be replaced by entry points"""
    bee()
    killbee()
