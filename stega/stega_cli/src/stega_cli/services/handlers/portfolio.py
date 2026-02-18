from dataclasses import asdict

from stega_cli.config import create_config
from stega_cli.domain.command import Response, GetPortfolio
from stega_cli.ports import db
from stega_cli.ports import portfolio as portfolio_db
from stega_lib import http


# TODO: We don't have a true event based system here. We are still dependent on synchronous network calls (e.g. each network call dispatches work in a synchronous manner and doesn't return immediately with a response/correlation id to allow for future querying).
#
# Instead we need to make the following modifications. NOTE: This is for all WRITES only. Reads can query the cache and then the make a synchronous request as needed.
#
# 1.) Generate a correlation id immediately by the client. In this case the CLI daemon should be generating this id.
# 2.) Every WRITE enabled command should have a correlation id argument associated with it.
# 3.) Start an async event loop in the daemon process. This will accept tasks that it iteratively completes and allows for easy cancelling.
# 4.) Write the correlation id to a local operations table that maps correlation ids to entity ids. All entities will be queryable by correlation id or entity id.
# 5.) Submit a cancellable task to the daemon event loop that subscribes to the commands associated topic. Use the correlation id to find the event indicating the work was accomplished by some service. Update the local entities table with the result of that event. Upodate the correlation to entity id table.
# 6.) Submit the http request to perform the work. If this succeeds, return a response to the client indicating the command request was submitted (not necessarily finished). If this does not succeed, cancel the async task submitted subscribing to the SSE topic and indicate that the request submission failed.
# 7.) Add a timeout to the SSE topic subscription, so it's never left in an unknown state in case there is an internal error in the service chain somewhere.


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

    data = {}
    # hit api to get latest result
    with http.acquire_session(config.core_service_url) as session:
        resp = session.get(f"porftolio/{cmd.portfolio_id}")
        data = resp.json()
    
    status = data["ok"]
    result = data["result"] if status else {}
    # TODO: cache result locally if found

    return Response(
        status="ok" if status else "error",
        result=asdict(result),
    )


def create_portfolio(cmd: CreatePortfolio) -> Response:
    config = create_config()

    data = {}
    with http.acquire_session(config.core_service_url) as session:
        payload = {
            "name": cmd.name,
            "assets": cmd.assets,
        }
        resp = session.post("portfolios", json=payload)
        data = resp.json()

    status = data["ok"]
    result = data["result"] if status else {}

    return Response(
        status="ok" if status else "error",
        result=str(result),
    )

