import uuid_utils as uuid
from stega_contracts.portfolio.command import (
    CreatePortfolio,
    DeletePortfolio,
    UpdatePortfolio,
)
from stega_contracts.portfolio.query import GetPortfolio, ListPortfolios
from stega_core import CliCommand, CliParam, ParamKind

from stega_cli.cli.parse import parse_asset_csv

GROUPS = {
    "portfolio": "Manage portfolios.",
}

CLI_COMMANDS = [
    CliCommand(
        group="portfolio",
        name="get",
        msg_type=GetPortfolio,
        help="Fetch a portfolio.",
        params=[
            CliParam(key="portfolio_id", help="Portfolio identifier."),
        ],
    ),
    CliCommand(
        group="portfolio",
        name="list",
        msg_type=ListPortfolios,
        help="List all portfolios.",
    ),
    CliCommand(
        group="portfolio",
        name="create",
        msg_type=CreatePortfolio,
        help="Create a new portfolio.",
        params=[
            CliParam(key="portfolio_id", factory=lambda: str(uuid.uuid7())),
            CliParam(key="name", help="Portfolio name."),
            CliParam(
                key="assets",
                kind=ParamKind.OPTION,
                flags=("-f", "--portfolio-file"),
                help="CSV file of symbol,weight rows.",
                parser=parse_asset_csv,
            ),
        ],
    ),
    CliCommand(
        group="portfolio",
        name="update",
        msg_type=UpdatePortfolio,
        help="Update an existing portfolio.",
        params=[
            CliParam(key="portfolio_id", help="Portfolio identifier."),
            CliParam(
                key="name",
                kind=ParamKind.OPTION,
                required=False,
                help="Portfolio name.",
            ),
            CliParam(
                key="assets",
                kind=ParamKind.OPTION,
                flags=("-f", "--portfolio-file"),
                required=False,
                help="CSV file of symbol,weight rows.",
                parser=parse_asset_csv,
            ),
        ],
    ),
    CliCommand(
        group="portfolio",
        name="delete",
        msg_type=DeletePortfolio,
        help="Delete a portfolio.",
        params=[
            CliParam(key="portfolio_id", help="Portfolio identifier."),
        ],
    ),
]

MESSAGE_TYPES = {spec.msg_type.__name__: spec.msg_type for spec in CLI_COMMANDS}
