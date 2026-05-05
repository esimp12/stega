# TODOS

- (`stega_core`) Add RabbitMqTransport to service_lifespan and DependencyContainer in bootstrap.py
- (`stega_lib`) Create AbstractUnitOfWork
- (`stega_lib`) Create a generic sqlalchemy UnitOfWork
- (`stega_lib`) Create a generic AbstractRepository

# ASKS

- How can we have an AbstractUnitOfWork shared as a base class across all services, BUT then each service can register its own repositories for this unit of work. Aka, we don't want to have to define ALL OF the service base class Repos on the global abstract unit of work.
    - 2 early ideas
        - 1) Do I go with class inheritance here. For example have 1 global AbstractUnitOfWork, and then each Service has their own base UnitOfWork with the appropriate Repos added. Then the MessageBus would need a way to "type" itself (e.g. [TUoW: AbstractUoW] and MessageBus[ServiceAbstractUoW] is the service implementation).
        - 2) Can I have some sort of RepoRegistry on a UnitOfWork and the service bootstraps the available repositories at start. I kind of like this more as it feels more like composition and also decouples the UoW from specific repos. For example, uow.repos.get(PortfolioRepository). Maybe there's a way to make this cleaner though (like uow.repos.portfolio calls .get(PortfolioRepository) under the hood. Would be nice as I expect these to be in every handler. Also there's some sort of dispatching required here. I'm unsure if the typing would work out nicely though and can live with .get(Repo) for the time being.
- How should external REST APIs be treated? Should I write repos for these? I assume no, currently I have created a generic "ServicePort" class. For example, I'd want to be able to pull data from the EOD API, and write the results to a database.
