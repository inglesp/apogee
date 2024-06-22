import csv
from datetime import date, datetime
from pathlib import Path

import httpx


def scrape():
    dirpath = Path(f"data/raw/getvoting/{date.today()}")
    dirpath.mkdir(parents=True, exist_ok=True)
    client = httpx.Client(timeout=60)

    with open("data/constituencies.csv") as f:
        for r in csv.DictReader(f):
            code = get_code(r["code"])
            if code == "E14001170":  # Chorley
                continue
            path = dirpath / f"{code}.html"
            if path.exists():
                continue
            print(datetime.now(), code, r["name"])
            rsp = client.get(f"https://www.getvoting.org/constituency/{code}")
            assert rsp.text
            path.write_text(rsp.text)


def get_code(code):
    # See also parsers/survation.py

    return {
        "S14000006": "S14000107",  # Ayr, Carrick and Cumnock
        "S14000008": "S14000108",  # Berwickshire, Roxburgh and Selkirk
        "S14000010": "S14000109",  # Central Ayshire
        "S14000040": "S14000110",  # Kilmarnock and Loudoun
        "S14000058": "S14000111",  # West Aberdeenshire and Kincardine
    }.get(code, code)


if __name__ == "__main__":
    scrape()
