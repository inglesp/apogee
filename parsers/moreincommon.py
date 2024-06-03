import csv
import json
import sys
from pathlib import Path


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        rows = list(csv.DictReader(f))

    data = {
        r["Constituency Code"]: {
            "name": r["Constituency"],
            "2024": {
                "con": r["Conservative"],
                "grn": r["Green Party"],
                "lab": r["Labour"],
                "lib": r["Liberal Democrat"],
                "oth": r["Other"],
                "pc": r["Plaid Cymru"],
                "ref": r["Reform UK"],
                "snp": r["Scottish National Party (SNP)"],
            },
        }
        for r in rows
    }

    for item in data.values():
        item["2024"] = {
            k: round(float(v.rstrip("%"))) for k, v in item["2024"].items() if v
        }
        item["party"] = max(item["2024"].items(), key=lambda pair: pair[1])[0]

    date = path.parts[-1]
    dirpath = Path(f"data/processed/moreincommon/{date}")
    dirpath.mkdir(parents=True, exist_ok=True)

    with (dirpath / "data.json").open("w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    path = Path(sys.argv[1])
    parse(path)
