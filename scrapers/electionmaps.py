import json
from datetime import date
from pathlib import Path

import httpx


def scrape():
    client = httpx.Client(timeout=60)

    rsp = client.get("https://flo.uri.sh/visualisation/17427609/embed?auto=1")
    for line in rsp.text.splitlines():
        if "_Flourish_data = " in line:
            data = line.split("_Flourish_data = ")[1][:-1]
            break
    else:
        assert False

    dirpath = Path(f"data/raw/electionmaps/{date.today()}")
    dirpath.mkdir(parents=True, exist_ok=True)
    (dirpath / "flourish.json").write_text(json.dumps(json.loads(data), indent=2))


if __name__ == "__main__":
    scrape()
