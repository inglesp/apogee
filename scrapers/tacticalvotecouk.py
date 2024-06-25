from datetime import date
from pathlib import Path

import httpx


def scrape():
    dirpath = Path(f"data/raw/tacticalvotecouk/{date.today()}")
    dirpath.mkdir(parents=True, exist_ok=True)
    rsp = httpx.get("https://tacticalvote.co.uk/data/recommendations.csv")
    (dirpath / "tactical-vote.csv").write_text(rsp.text)


if __name__ == "__main__":
    scrape()
