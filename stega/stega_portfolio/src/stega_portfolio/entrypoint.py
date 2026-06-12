import asyncio
import logging

from stega_contracts.portfolio.routes import ROUTES
from stega_core import (
    RepositoryRuntime,
    build_quart_app,
    init_logger,
    serve_hypercorn,
)

from stega_portfolio.bootstrap import build_service, get_db_uri
from stega_portfolio.config import create_config
from stega_portfolio.ports.orm import init_metadata, start_mappers


def run_rest_app() -> None:
    # setup config and logger
    config = create_config()
    init_logger(
        service_name="stega_portfolio",
        log_level=config.LOG_LEVEL,
        third_party_logger_names=["hypercorn"],
    )
    logger = logging.getLogger(__name__)

    # build service and app
    service = build_service(config)
    app = build_quart_app(service, ROUTES)

    # start mappers if persisted runtime
    is_sqlalchemy = RepositoryRuntime.SQLITE | RepositoryRuntime.POSTGRES
    if bool(config.REPOSITORY_RUNTIME & is_sqlalchemy):
        logger.info("Initializing metadata & starting mappers...")
        db_uri = get_db_uri(config, is_async=False)
        init_metadata(db_uri)
        start_mappers()

    asyncio.run(
        serve_hypercorn(
            app=app,
            log_level=config.LOG_LEVEL,
            host=config.HOST,
            port=config.PORT,
        )
    )
