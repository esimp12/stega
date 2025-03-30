import typing as T
from datetime import datetime

from flask import Blueprint, jsonify

from config import CONFIG
from src import db

bp = Blueprint("prices", __name__)


@bp.route("/prices/<string:symbol>", methods=["GET"])
def get(symbol: str):
    return jsonify(prices(symbol)), 200


def prices(symbol: str) -> T.Dict[str, T.Any]:
    conn = db.connection(
        CONFIG.STEGA_DBNAME,
        CONFIG.STEGA_DBUSER,
        CONFIG.STEGA_DBPASSWORD,
        CONFIG.STEGA_DBHOST,
        CONFIG.STEGA_DBPORT,
    )
    results = db.get_prices(conn, symbol)
    conn.close()
    return {
        "symbol": symbol,
        "prices": [
            {
                "date": datetime.strftime(res["date"], "%Y-%m-%d"),
                "close": res["closing_price"],
            }
            for res in results
        ],
    }
