from stega_portfolio.domain.commands import CreatePortfolio
from stega_portfolio.services.messagebus import MessageBus


class TestCreatePortfolio:
    def test_create_portfolio(self, unit_test_bus: MessageBus):
        # Arrange
        cmd = CreatePortfolio(
            id="id1",
            name="test portfolio",
            assets={},
        )

        # Act
        unit_test_bus.handle(cmd)

        # Assert
        uow = unit_test_bus.uow
        portfolios = uow.portfolios._portfolios
        assert len(portfolios) == 1
        portfolio = portfolios[0]
        assert portfolio.id == cmd.id
        assert portfolio.name == cmd.name
        for symbol, weight in cmd.assets.items():
            assert any(asset.symbol == symbol and asset.weight == weight for asset in portfolio.assets)
        assert uow.committed is True
