import csv
import functools
import json
import sys
from pathlib import Path


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        rows = list(csv.DictReader(f))

    data = {
        name_to_code()[r["Constituency"].lower()]: {
            "name": r["Constituency"],
            "2024": {
                "con": r["Con"],
                "grn": r["Grn"],
                "lab": r["Lab"],
                "lib": r["LDem"],
                "oth": r["Ind_Oth"],
                "pc": r["PC"],
                "ref": r["Ref"],
                "snp": r["SNP"],
            },
        }
        for r in rows
    }

    for item in data.values():
        item["2024"] = {k: int(v.rstrip("%")) for k, v in item["2024"].items() if v}
        item["party"] = max(item["2024"].items(), key=lambda pair: pair[1])[0]

    date = path.parts[-1]
    dirpath = Path(f"data/processed/britainpredicts/{date}")
    dirpath.mkdir(parents=True, exist_ok=True)

    with (dirpath / "data.json").open("w") as f:
        json.dump(data, f, indent=2)


@functools.cache
def name_to_code():
    with open("data/constituencies.csv") as f:
        rv = {r[1].lower(): r[0] for r in csv.reader(f)}
    rv["ynys mon"] = rv["ynys môn"]  # ffs
    return rv


if __name__ == "__main__":
    path = Path(sys.argv[1])
    parse(path)
