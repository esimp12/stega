"""Unit tests for portfolio service commands in the stega_portfolio application."""

from stega_portfolio.domain.commands import CreatePortfolio
from stega_portfolio.services.messagebus import MessageBus


class TestCreatePortfolio:
    """Tests for the CreatePortfolio command."""

    def test_create_portfolio_with_no_assets(self, unit_test_bus: MessageBus) -> None:
        """Test creating a portfolio with no assets."""
        cmd = CreatePortfolio(
            id="id1",
            name="test portfolio",
            assets={},
        )
        unit_test_bus.handle(cmd)
        uow = unit_test_bus.uow
        portfolio = uow.portfolios.get_portfolio(cmd.id)
        assert portfolio is not None
        assert portfolio.id == cmd.id
        assert portfolio.name == cmd.name
        assert portfolio.assets == []
        assert uow.committed is True

    def test_create_portfolio_with_assets(self, unit_test_bus: MessageBus) -> None:
        """Test creating a portfolio with assets."""
        cmd = CreatePortfolio(
            id="id1",
            name="test portfolio",
            assets={
                "asset1": 0.3,
                "asset2": 0.7,
            },
        )
        unit_test_bus.handle(cmd)
        uow = unit_test_bus.uow
        portfolio = uow.portfolios.get_portfolio(cmd.id)
        assert portfolio is not None
        assert portfolio.id == cmd.id
        assert portfolio.name == cmd.name
        assert len(portfolio.assets) == len(cmd.assets.keys())
        for symbol, weight in cmd.assets.items():
            assert any(asset.symbol == symbol and asset.weight == weight for asset in portfolio.assets)
        assert uow.committed is True
