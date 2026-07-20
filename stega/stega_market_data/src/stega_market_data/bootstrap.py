import httpx

from stega_market_data.config import MarketDataConfig
from stega_core import HttpProviderChannel
from stega_utils.limiter import RateLimiterStack, SmoothingRateLimiter, QuotaRateLimiter


def build_eod_channel(config: MarketDataConfig) -> HttpProviderChannel:
    limiters = RateLimiterStack([
        SmoothingRateLimiter(int(config.EOD_QUOTA_PER_MIN * 0.95), 60),
        QuotaRateLimiter(config.EOD_QUOTA_PER_MIN, 60),
    ])
    return HttpProviderChannel(
        base_url=config.EOD_BASE_URL,
        http2=True,
        limiters=limiters,
    )


def price_provider_factory(config: MarketDataConfig) -> Callable[[HttpProviderChannel], PriceProvider]:
    def build(channel: HttpProviderChannel) -> PriceProvider:
        return HttpPriceProvider(
            channel=channel,
            api_key=config.EOD_API_KEY,
        )
    return build


def get_db_uri(
    config: MarketDataConfig,
    *,
    is_async: bool = True,
) -> str:
    if bool(config.REPOSITORY_RUNTIME & RepositoryRuntime.SQLITE):
        path = Path.expanduser(Path(config.DATA_DIR))
        name = config.REPOSITORY_DBNAME
        if not Path.exists(path):
            Path.mkdir(path)
        path = Path(path) / f"{name}.db"
        dialect = "+aiosqlite" if is_async else ""
        return f"sqlite{dialect}:///{path}"
    if bool(config.REPOSITORY_RUNTIME & RepositoryRuntime.POSTGRES):
        user = config.REPOSITORY_DBUSER
        password = quote_plus(config.REPOSITORY_DBPASS)
        host = config.REPOSITORY_DBHOST
        port = config.REPOSITORY_DBPORT
        name = config.REPOSITORY_DBNAME
        dialect = "+asyncpg" if is_async else ""
        return f"postgresql{dialect}://{user}:{password}@{host}:{port}/{name}"
    return ""


def build_sqlalchemy_session_factory(db_uri: str) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(db_uri)
    return async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


def build_sqlite_session_factory(config: MarketDataConfig) -> async_sessionmaker[AsyncSession]:
    db_uri = get_db_uri(config)
    return build_sqlalchemy_session_factory(db_uri)


def build_postgres_session_factory(config: MarketDataConfig) -> async_sessionmaker[AsyncSession]:
    db_uri = get_db_uri(config)
    return build_sqlalchemy_session_factory(db_uri)


def build_in_memory_session_factory(_: MarketDataConfig) -> None:
    return None


def build_in_memory_service_broker(_: MarketDataConfig) -> InMemoryBroker:
    return InMemoryBroker()


def build_service(config: MarketDataConfig) -> Service:
    sqlite_session_factory = functools.partial(build_sqlite_session_factory, config)
    postgres_session_factory = functools.partial(build_postgres_session_factory, config)

    builder = ServiceBuilder(config)
    # set runtimes
    builder = (
        builder.with_repository_runtime("REPOSITORY_RUNTIME")
        .with_service_broker_runtime("SERVICE_BROKER_RUNTIME")
    )

    # create repo constructs
    uow_session_factories = {
        RepositoryRuntime.POSTGRES: postgres_session_factory,
        RepositoryRuntime.SQLITE: sqlite_session_factory,
    }
    uow_classes = {
        RepositoryRuntime.POSTGRES: SqlAlchemyUnitOfWork,
        RepositoryRuntime.SQLITE: SqlAlchemyUnitOfWork,
    }
    price_pull_repositories = {
        RepositoryRuntime.POSTGRES: SqlAlchemyPricePullRepository,
        RepositoryRuntime.SQLITE: SqlAlchemyPricePullRepository,
    }
    builder = (
        builder.with_unit_of_work_sessions(uow_session_factories)
        .with_unit_of_work(uow_classes)
        .with_repository(PricePullRepository, price_pull_repositories)
    )

    # create service broker
    service_broker_factories = {
        ServiceBrokerRuntime.RABBITMQ: build_rabbitmq_service_broker,
        ServiceBrokerRuntime.MEMORY: build_in_memory_service_broker,
    }
    builder = builder.with_service_broker(service_broker_factories)

    # create providers
    builder = (
        builder.with_dependency(HttpProviderChannel, Scope.SINGLETON, lambda: build_eod_channel(config))
        .with_dependency(PriceProvider, Scope.SINGLETON, price_provider_factory(config))
    )

    # create handlers
    builder = (
        builder.with_command_handlers(COMMAND_HANDLERS)
        .with_query_handlers(QUERY_HANDLERS)
        .with_event_handlers(EVENT_HANDLERS)
        .with_service_events(SERVICE_EVENTS)
    )

    return builder.build(logging.getLogger(__name__))
