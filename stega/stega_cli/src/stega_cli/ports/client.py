from enum import auto

from stega_config import source
from stega_contracts.routes import ROUTES
from stega_core import HttpServiceSpec, RuntimeFlag, ServiceContract, StegaServicePort, UnixSocketServiceSpec


class ClientPort(StegaServicePort): ...


class ClientRuntime(RuntimeFlag):
    DAEMON = auto()
    DIRECT = auto()


class ClientConfig:
    CLIENT_RUNTIME: ClientRuntime = source("env", default=ClientRuntime.DAEMON)


CONTRACT = ServiceContract(
    port_base=ClientPort,
    runtime_field="CLIENT_RUNTIME",
    specs=[
        UnixSocketServiceSpec(
            runtime=ClientRuntime.DAEMON,
            socket_path_field="socket_path",
        ),
        HttpServiceSpec(
            runtime=ClientRuntime.DIRECT,
            base_url_field="EDGE_SERVICE_URL",
            routes=ROUTES,
        ),
    ],
)
