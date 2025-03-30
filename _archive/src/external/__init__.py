from flask import Flask

from src.external.prices import bp as prices
from src.external.symbols import bp as symbols


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(symbols)
    app.register_blueprint(prices)
    return app
