from enum import auto

from stega_config import source
from stega_core import (
    HttpServiceSpec,
    ServiceContract,
    RuntimeFlag,
)
from stega_contracts.portfolio.routes import ROUTES


class PortfolioServiceRuntime(RuntimeFlag):
    MEMORY = auto()
    HTTP = auto()


class PortfolioServiceConfig:
    PORTFOLIO_SERVICE_RUNTIME: PortfolioServiceRuntime = source(
        "env",
        default=PortfolioServiceRuntime.HTTP,
    )

    PORTFOLIO_SERVICE_URL: str = source(
        "env",
        default="http://portfolio:5000",
        depends_on="PORTFOLIO_SERVICE_RUNTIME",
        depends_value=PortfolioServiceRuntime.HTTP,
    )


CONTRACT = ServiceContract(
    port_base=PortfolioServicePort,
    runtime_field="PORTFOLIO_SERVICE_RUNTIME",
    specs=[
        HttpServiceSpec(
            runtime=PortfolioServiceRuntime.HTTP,
            base_url_field="PORTFOLIO_SERVICE_URL",
            routes=ROUTES,
        ),
    ],
)
