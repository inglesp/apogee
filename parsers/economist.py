import csv
from collections import defaultdict


def parse(path):
    data = defaultdict(dict)
    with (path / "constit.vote.share.csv").open() as f:
        for r in csv.DictReader(f):
            item = data[r["code"]]
            item["code"] = r["code"]
            item["name"] = r["name"]
            item[r["party"]] = r["pred24.pct"]
    return data.values()
