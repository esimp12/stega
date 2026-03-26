import click


def echo_banner(title: str, char: str = "=") -> None:
    """Display a line followed by a underlining banner.

    Args:
        title: A str of the line to underline.
        char: A str of the repeating character to use to underline the title.

    """
    banner = char * len(title)
    click.echo(title)
    click.echo(banner)
