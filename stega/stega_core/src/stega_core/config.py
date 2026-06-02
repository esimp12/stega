from stega_config import source

from stega_core.bootstrap import (
    ClientBrokerRuntime,
    ReaderRuntime,
    RepositoryRuntime,
    ServiceBrokerRuntime,
)


class ServiceConfig:
    ENV: str = source("env", default="dev")
    LOG_LEVEL: str = source("env", default="INFO")

    HOST: str = source("env", deault="127.0.0.1")
    PORT: int = source("env", default=5000)


class ServiceBrokerConfig:
    SERVICE_BROKER_RUNTIME: ServiceBrokerRuntime = source(
        "env",
        default=ServiceBrokerRuntime.RABBITMQ,
    )

    SERVICE_BROKER_EXCHANGE: str = source(
        "env",
        default="events",
        depends_on="SERVICE_BROKER_RUNTIME",
        depends_value=ServiceBrokerRuntime.RABBITMQ,
    )
    SERVICE_BROKER_USER: str = source(
        "env",
        depends_on="SERVICE_BROKER_RUNTIME",
        depends_value=ServiceBrokerRuntime.RABBITMQ,
    )
    SERVICE_BROKER_PASS: str = source(
        "env",
        depends_on="SERVICE_BROKER_RUNTIME",
        depends_value=ServiceBrokerRuntime.RABBITMQ,
    )
    SERVICE_BROKER_HOST: str = source(
        "env",
        default="broker",
        depends_on="SERVICE_BROKER_RUNTIME",
        depends_value=ServiceBrokerRuntime.RABBITMQ,
    )
    SERVICE_BROKER_PORT: int = source(
        "env",
        default=5672,
        depends_on="SERVICE_BROKER_RUNTIME",
        depends_value=ServiceBrokerRuntime.RABBITMQ,
    )


class ClientBrokerConfig:
    CLIENT_BROKER_RUNTIME: ClientBrokerRuntime = source(
        "env",
        default=ClientBrokerRuntime.MEMORY,
    )


class RepositoryConfig:
    REPOSITORY_RUNTIME: RepositoryRuntime = source(
        "env",
        default=RepositoryRuntime.POSTGRES,
    )

    REPOSITORY_DBNAME: str = source("env")
    REPOSITORY_DBUSER: str = source(
        "env",
        depends_on="REPOSITORY_RUNTIME",
        depends_value=RepositoryRuntime.POSTGRES,
    )
    REPOSITORY_DBPASS: str = source(
        "env",
        depends_on="REPOSITORY_RUNTIME",
        depends_value=RepositoryRuntime.POSTGRES,
    )
    REPOSITORY_DBHOST: str = source(
        "env",
        depends_on="REPOSITORY_RUNTIME",
        depends_value=RepositoryRuntime.POSTGRES,
    )
    REPOSITORY_DBPORT: str = source(
        "env",
        default=5432,
        depends_on="REPOSITORY_RUNTIME",
        depends_value=RepositoryRuntime.POSTGRES,
    )


class ReaderConfig:
    READER_RUNTIME: ReaderRuntime = source(
        "env",
        default=ReaderRuntime.POSTGRES,
    )

    READER_DBNAME: str = source("env")
    READER_DBUSER: str = source(
        "env",
        depends_on="READER_RUNTIME",
        depends_value=ReaderRuntime.POSTGRES,
    )
    READER_DBPASS: str = source(
        "env",
        depends_on="READER_RUNTIME",
        depends_value=ReaderRuntime.POSTGRES,
    )
    READER_DBHOST: str = source(
        "env",
        depends_on="READER_RUNTIME",
        depends_value=ReaderRuntime.POSTGRES,
    )
    READER_DBPORT: str = source(
        "env",
        default=5432,
        depends_on="READER_RUNTIME",
        depends_value=ReaderRuntime.POSTGRES,
    )
