import click


def startServer():
    """
    Safely starts the main server
    """
    ...


def verifyServer():
    """
    Verify if server is up and running
    """
    ...


def safelyKillServer():
    """
    Safely stop and killing the server
    """
    ...


@click.group()
def cli():
    """
    Bundle all the commands together
    """
    pass


@click.command()
def bee():
    serverStatus = verifyServer()
    if serverStatus:
        click.echo("Opening mine!")
    else:
        click.echo("Starting server")
        startServer()
        click.echo("Opening mine!")


@click.command()
def kbee():
    click.echo("Killing Server")
    safelyKillServer()
    click.echo("Server killed")


cli.add_command(bee)
cli.add_command(kbee)


if __name__ == "__main__":
    """this is a temp format for development purpose. After the CLI is finished and goes to production this will be replaced by entry points"""
    cli()
