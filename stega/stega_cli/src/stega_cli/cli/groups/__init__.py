from stega_cli.cli.groups.daemon import daemon
from stega_cli.cli.groups.events import events

STATIC_GROUPS = [daemon, events]

__all__ = [
    "STATIC_GROUPS",
    "daemon",
    "events",
]
