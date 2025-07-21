"""Alembic environment script for autogenerating migration scripts of the stega portfolio service."""

from sqlalchemy import create_engine, pool
from stega_portfolio.config import create_config
from stega_portfolio.ports.orm import metadata

from alembic import context

target_metadata = metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    env = context.get_x_argument(as_dictionary=True).get("env", "dev")
    config = create_config(env)
    context.configure(
        url=config.db_uri,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    env = context.get_x_argument(as_dictionary=True).get("env", "dev")
    config = create_config(env)
    connectable = create_engine(config.db_uri, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
