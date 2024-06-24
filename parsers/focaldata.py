import csv


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        return [parse_one(r) for r in csv.DictReader(f)]


def parse_one(r):
    return {
        "code": r["ONS Code"],
        "name": r["Westminster Constituency"],
        "con": r["CON"].rstrip("%"),
        "grn": r["GRN"].rstrip("%"),
        "lab": r["LAB"].rstrip("%"),
        "lib": r["LDM"].rstrip("%"),
        "oth":  r["OTH"].rstrip("%"),
        "pc": r["PCY"].rstrip("%"),
        "ref": r["RFM"].rstrip("%"),
        "snp": r["SNP"].rstrip("%"),
    }

