import typing as T

import requests

from config import CONFIG


def symbols() -> T.List[str]:
    url = (
        f"{CONFIG.STEGA_EOD_API}/exchange-symbol-list/"
        + f"{CONFIG.STEGA_EOD_EXCHANGE}?"
        + f"fmt=json&api_token={CONFIG.STEGA_EOD_API_TOKEN}"
    )
    res = requests.get(url)
    res.raise_for_status()
    return [elem["Code"] for elem in res.json()]
