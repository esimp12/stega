from enum import auto

from stega_config import source
from stega_core import HttpServiceSpec, RuntimeFlag, ServiceContract

from stega_contracts.edge.port import EdgeServicePort
from stega_contracts.routes import ROUTES


class EdgeServiceRuntime(RuntimeFlag):
    MEMORY = auto()
    HTTP = auto()


class EdgeServiceConfig:
    EDGE_SERVICE_RUNTIME: EdgeServiceRuntime = source(
        "env",
        default=EdgeServiceRuntime.HTTP,
    )
    EDGE_SERVICE_URL: str = source(
        "env",
        default="http:localhost:20000",
        depends_on="EDGE_SERVICE_RUNTIME",
        depends_value=EdgeServiceRuntime.HTTP,
    )


CONTRACT = ServiceContract(
    port_base=EdgeServicePort,
    runtime_field="EDGE_SERVICE_RUNTIME",
    specs=[
        HttpServiceSpec(
            runtime=EdgeServiceRuntime.HTTP,
            base_url_field="EDGE_SERVICE_URL",
            routes=ROUTES,
        ),
    ],
)
