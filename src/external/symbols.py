import typing_extensions as T
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
