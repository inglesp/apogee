import csv
import json
import sys
from collections import defaultdict
from pathlib import Path


def parse(path):
    data = defaultdict(dict)
    with (path / "constit.vote.share.csv").open() as f:
        for r in csv.DictReader(f):
            item = data[r["code"]]
            if "name" not in item:
                item["name"] = r["name"]
            if "2019" not in item:
                item["2019"] = {}
            if "2024" not in item:
                item["2024"] = {}
            item["2019"][r["party"]] = round(float(r["ge19.pct"] or 0))
            item["2024"][r["party"]] = round(float(r["pred24.pct"] or 0))

    for item in data.values():
        item["party"] = max(item["2024"].items(), key=lambda pair: pair[1])[0]

    date = path.parts[-1]
    dirpath = Path(f"data/processed/economist/{date}")
    dirpath.mkdir(parents=True, exist_ok=True)

    with (dirpath / "data.json").open("w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    path = Path(sys.argv[1])
    parse(path)
