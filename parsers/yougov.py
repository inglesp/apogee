import csv


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open(encoding="utf-8-sig") as f:
        return [parse_one(r) for r in csv.DictReader(f)]


def parse_one(r):
    return {
        "code": r["const"],
        "name": r["area"],
        "con": r["ConShare"].rstrip("%"),
        "grn": r["GreenShare"].rstrip("%"),
        "lab": r["LabShare"].rstrip("%"),
        "lib": r["LibDemShare"].rstrip("%"),
        "oth": r["OthersShare"].rstrip("%"),
        "pc": r["PlaidShare"].rstrip("%"),
        "ref": r["ReformShare"].rstrip("%"),
        "snp": r["SNPShare"].rstrip("%"),
    }
