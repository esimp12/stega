## Overview

## Workspace Management & Build System

This project uses `uv` for its build system and workspace management solution. The project follows a "monorepo" structure where the top level `pyproject.toml` file defines the `uv` workspace as a "virtual" package and includes each application service as a workspace member (under `/stega`). Each service also has its own `pyproject.toml` file that defines unique dependencies and the `uv` build backend for that service. 

A `Dockerfile` is provided for each service to build a Docker image that includes the service and its dependencies. The service `pyproject.toml` files define an entry point to run the service in the Docker container. At the top level, a `docker-compose.yml` file is provided to run all services together in a Docker environment. If a service requires coordination with multiple containers, a `docker-compose.yml` file is provided in that service directory and then included in the top-level `docker-compose.yml` file.

### Adding a Dependency to a Service

```
uv add --directory stega/<service_name> <dependency>
```

### Insalling Dependencies

```
uv sync --all-packages
```

### Building a Service

```
uv build --all-packages
```

## Database Migrations

Database migrations are managed using `alembic`. Each service that requires a database should have its own `alembic` configuration and migration scripts. The `alembic` configuration is defined in the service's `pyproject.toml` file, and the migration scripts are stored in the `alembic` directory of the service.

### Running Migrations

#### Updating Database to Latest Migration

```
uv run --env-file .env.dev --directory stega/<service_name> --package <service_name> alembic upgrade head
```

#### Generating a New Migration Script

```
uv run --env-file .env.dev --directory stega/<service_name> --package <service_name> alembic revision --autogenerate -m "<migration_message>"
```

## Deploying Services

The entire application is deployed using Docker Compose. The top-level `docker-compose.yml` file includes references to each individual service's `docker-compose.yml` file. The following commands show how to deploy the entire application or individual services.

### Deploying the Entire Application

Note the `.env.prod` file is at the project root and should contain the necessary environment variables for a production deployment across all services. Services prefix their environment variables with the service name to avoid conflicts (e.g. `STEGA_PORTFOLIO_LOG_LEVEL`).

```
docker compose --env-file .env.prod up -d
```

### Deploying a Single Service (for Development)

```
uv run invoke serve <service_name>
```
