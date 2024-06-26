import json


def parse(path):
    with (path / "flourish.json").open() as f:
        data = json.load(f)
    for r in data["regions"]:
        yield parse_one(r["metadata"])


def parse_one(m):
    return {
        "code": m[1],
        "name": m[2],
        "con": m[14].rstrip("%"),
        "lab": m[15].rstrip("%"),
        "lib": m[16].rstrip("%"),
        "ref": m[17].rstrip("%"),
        "grn": m[18].rstrip("%"),
        "snp": m[19].rstrip("%"),
        "pc": m[20].rstrip("%"),
        "oth": m[21].rstrip("%"),
    }
