import click

def echo_banner(title: str, char: str = "=") -> None:
    banner = char * len(title)
    click.echo(title)
    click.echo(banner)
