import httpx
import typing_extensions as T
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify

from config import CONFIG
from src import db

bp = Blueprint("symbols", __name__)


@bp.route("/symbols", methods=["GET"])
def get():
    return jsonify(symbols()), 200


def symbols() -> T.List[T.Dict[str, T.Any]]:
    conn = db.connection(
        CONFIG.STEGA_DBNAME,
        CONFIG.STEGA_DBUSER,
        CONFIG.STEGA_DBPASSWORD,
        CONFIG.STEGA_DBHOST,
        CONFIG.STEGA_DBPORT,
    )
    results = db.get_symbols(conn)
    conn.close()
    return results


def get_sp500_symbols(url: str = CONFIG.STEGA_SP500_URL) -> T.List[str]:
    resp = httpx.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", {"class": "wikitable"})
    symbols = []
    for row in table.tbody.find_all("tr"):
        columns = row.find_all("td")
        if columns:
            symbol = columns[0].text.strip()
            symbols.append(symbol)
    return symbols
