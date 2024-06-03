import csv
import json
import sys
from pathlib import Path


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open(encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    data = {
        r["const"]: {
            "name": r["area"],
            "2024": {
                "con": r["ConShare"],
                "grn": r["GreenShare"],
                "lab": r["LabShare"],
                "lib": r["LibDemShare"],
                "oth": r["OthersShare"],
                "pc": r["PlaidShare"],
                "ref": r["ReformShare"],
                "snp": r["SNPShare"],
            },
        }
        for r in rows
    }

    for item in data.values():
        item["2024"] = {k: int(v.rstrip("%")) for k, v in item["2024"].items() if v}
        item["party"] = max(item["2024"].items(), key=lambda pair: pair[1])[0]

    date = path.parts[-1]
    dirpath = Path(f"data/processed/yougov/{date}")
    dirpath.mkdir(parents=True, exist_ok=True)

    with (dirpath / "data.json").open("w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    path = Path(sys.argv[1])
    parse(path)
