import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

import httpx


def scrape(n):
    dirpath = Path(f"data/raw/electoralcalculus/{date.today()}")
    dirpath.mkdir(parents=True, exist_ok=True)

    client = httpx.Client(timeout=60)

    rsp = client.get("https://www.electoralcalculus.co.uk/newseatlookup.html")
    text = rsp.text.split("SeatList = new Array(")[1].split(");")[0]
    names = re.findall('"(.*?)"', text)
    for ix, name in enumerate(names[n * 50 : (n + 1) * 50]):
        path = dirpath / f"{name}.html"
        if path.exists():
            continue
        print(datetime.now(), ix, name)
        rsp = client.get(
            f"https://www.electoralcalculus.co.uk/fcgi-bin/calcwork23.py?seat={name}"
        )
        assert "New Boundaries 2023 Calculation" in rsp.text, rsp.text
        path.write_text(rsp.text)
        time.sleep(60)


if __name__ == "__main__":
    n = int(sys.argv[1])
    scrape(n)
