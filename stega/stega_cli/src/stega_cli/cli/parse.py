from pathlib import Path


def parse_asset_csv(value: str) -> dict[str, float]:
    assets: dict[str, float] = {}
    with Path(value).open(encoding="utf-8") as fd:
        for line in fd:
            if not line.strip():
                continue
            symbol, weight = line.split(",")
            assets[symbol.strip()] = float(weight.strip())
    return assets
