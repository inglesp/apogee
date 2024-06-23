from datetime import date
from pathlib import Path

import httpx


def scrape():
    dirpath = Path(f"data/raw/tacticalvote/{date.today()}")
    dirpath.mkdir(parents=True, exist_ok=True)
    rsp = httpx.get("https://tactical.vote/open-data/tactical-vote.csv")
    (dirpath / "tactical-vote.csv").write_text(rsp.text)


if __name__ == "__main__":
    scrape()
