import csv
import json


parties = [
    "con",
    "grn",
    "lab",
    "lib",
    "oth",
    "pc",
    "ref",
    "snp",
]


def parse():
    rows = []

    with open("data/raw/exitpoll/2024-07-04/exitpoll.json") as f:
        for loc in json.load(f)["locations"]:
            row = {"code": loc["id"], "name": loc["name"]}
            for p in loc["parties"]:
                party = p["party"]["code"].lower().replace("ld", "lib")
                row[party] = p["probability"]
            rows.append(row)

    rows.sort(key=lambda r: r["code"])

    with open("data/processed/exitpoll/2024-07-04/data.csv", "w") as f:
        writer = csv.DictWriter(f, ["code", "name", *parties])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parse()
