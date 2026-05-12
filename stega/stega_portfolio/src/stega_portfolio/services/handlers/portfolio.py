async def create_portfolio(cmd: CreatePortfolio, uow: AbstractUnitOfWork) -> None:
    async with uow:
        repo = uow.repo(PortfolioRepository)
        if repo.get(cmd.portfolio_id) is not None:
            err_msg = f"Portfolio with ID {cmd.portfolio_id} already exists."
            raise ConflictError(err_msg)
        
        portfolio = Portfolio.from_command(cmd)
        repo.add(portfolio)
        uow.commit()


async def delete_portfolio(cmd: DeletePortfolio, uow: AbstractUnitOfWork) -> None:
    async with uow:
        repo = uow.repo(PortfolioRepository)
        
        portfolio = repo.get(cmd.portfolio_id)
        if portfolio is None:
            err_msg = f"Portfolio with ID {cmd.portfolio_id} does not exist."
            raise ResourceNotFoundError(err_msg)
        
        portfolio.purge()
        repo.delete(portfolio)
        uow.commit()


async def update_portfolio(cmd: UpdatePortfolio, uow: AbstractUnitOfWork) -> None:
    async with uow:
        repo = uow.repo(PortfolioRepository)
        
        portfolio = repo.get(cmd.portfolio_id)
        if portfolio is None:
            err_msg = f"Portfolio with ID {cmd.portfolio_id} does not exist."
            raise ResourceNotFoundError(err_msg)

        portfolio.update(
            name=cmd.name,
            assets=PortfolioAsset.from_dict(portfolio.aggregate_id, cmd.assets),
        )
        repo.update(portfolio)
        uow.commit()
