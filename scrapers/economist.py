from datetime import date
from pathlib import Path

import httpx


def scrape():
    dirpath = Path(f"data/raw/economist/{date.today()}")
    dirpath.mkdir(parents=True, exist_ok=True)
    rsp = httpx.get(
        "https://cdn.economistdatateam.com/uk-elections/2024/forecast/data/constit.vote.share.csv"
    )
    (dirpath / "constit.vote.share.csv").write_text(rsp.text)


if __name__ == "__main__":
    scrape()
