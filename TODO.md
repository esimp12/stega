# TODO — Portfolio CRUD end-to-end

Target: a CLI client (`stega_cli`) can issue create/read/update/delete against
`stega_edge`, which forwards to `stega_portfolio`, which persists and emits events.

## Day 1 — Rename pass & lib syntax fixes (foundation)
- [x] Rename `stega_lib` → `stega_core` (workspace member, pyproject names, all imports)
- [x] Rename current `stega_core` → `stega_edge` (workspace member, pyproject, imports)
- [x] Extract `Event` *subclasses* (`PortfolioCreated/Deleted/Updated`) from
      `stega_core/event.py` into a new `stega_contracts` workspace package; leave
      the abstract `Event` base in `stega_core`
- [x] Fix all syntax errors in `stega_core/messaging/bus.py` and `stega_core/di.py`
      (the `int = 0 shutdown_timeout: float = 30.0` lines, the
      `self._x = dict[T, U] = {}` lines)
- [ ] Add an `invoke smoke` task that runs `python -c "import <pkg>"` for each
      workspace member; iterate ruff + smoke until both are green

## Day 2 — Lock the bus contract with the 5 unit tests
- [ ] Delete (or move to `_archive`) the stale `stega_portfolio/tests/unit/*`
- [ ] Create `stega_core/tests/unit/{test_registry,test_di,test_bus}.py` with the
      5 tests from §1: action_types, bind_handler, dispatch_scope caching,
      command dispatch, sync event drain
- [ ] Fix `stega_core/messaging/__init__.py` to alias `ActionRegistry` /
      `ActionFanOutRegistry` (not the bare `Registry`) so `action_types` exists
- [ ] Fix `Event.deserialize` (`payload` undefined), `Event.event_types`
      (`_registery` typo), `AbstractRepository.list` (`results` undefined)
- [ ] All 5 tests pass; commit

## Day 3 — `stega_portfolio` boots and serves one CREATE
- [ ] Replace `adapters/rest/app.py` Flask app with a Quart app; new
      `bootstrap.py` matches the actual current container/registry shape
      (no more `bootstrap(uow=...)` — use `service_lifespan(config)` from
      the new bus)
- [ ] Fix `bootstrap.py` import errors and config-attribute mismatches
      (`STEGA_BROKER_PASS` vs `STEGA_BROKER_PASSWORD`, etc.); align names with
      whatever the actual `PortfolioConfig` exposes
- [ ] Fix `services/handlers/portfolio.py` to (a) have imports, (b) return
      `CommandResponse`, (c) use `cmd.id` not `cmd.portfolio_id`
- [ ] Write a single concrete `SqlAlchemyPortfolioRepository` and register it
      in `build_repo_registry`
- [ ] `invoke serve --package stega_portfolio` boots; POST /portfolios with
      curl returns 201

## Day 4 — Round out portfolio CRUD + emit events
- [ ] GET /portfolios/<id> — wire up `GetPortfolio` query + handler + view
- [ ] GET /portfolios — list query
- [ ] PATCH/PUT /portfolios/<id> — `UpdatePortfolio` handler returning
      `CommandResponse`
- [ ] DELETE /portfolios/<id>
- [ ] Verify `PortfolioCreated/Updated/Deleted` events get published to
      RabbitMQ (use `docker logs` on the broker or rabbitmq management UI)

## Day 5 — `stega_edge` proxies through, `stega_cli` calls it
- [ ] Fix `stega_edge/ports/http.py` to use a config-injected URL (currently
      `self.config` is referenced but never set on the port)
- [ ] Verify `stega_edge` REST adapter forwards all 5 CRUD endpoints to
      `stega_portfolio` (it currently has GET/POST; add list, update, delete)
- [ ] Wire `stega_cli/cli/portfolio.py` commands to hit `stega_edge` for all
      five operations; smoke-test the full chain CLI → edge → portfolio → db
- [ ] Document the env-var setup in `CONTRIBUTING.md` so the dev loop is
      reproducible
