from dataclasses import asdict

from stega_cli.config import create_config
from stega_cli.domain.command import Response, GetPortfolio
from stega_cli.ports import db
from stega_cli.ports import portfolio as portfolio_db
from stega_lib import http

def get_portfolio(cmd: GetPortfolio) -> Response:
    config = create_config()
    
    # check if portfolio is locally cached first
    with db.acquire_connection(config.db_uri) as conn:
        portfolio = portfolio_db.get_portfolio(conn, cmd.portfolio_id) 
        if portfolio is not None:
            return Response(
                status="ok",
                result=asdict(portfolio),
            )
        
    configure
    with http.acquire_session(config.core_service_url) as session:

