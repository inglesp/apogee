import csv


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        return [parse_one(r) for r in csv.DictReader(f)]


def parse_one(r):
    return {
        "code": r["Constituency Code"],
        "name": r["Constituency"],
        "con": r["Conservative"].rstrip("%"),
        "grn": r["Green Party"].rstrip("%"),
        "lab": r["Labour"].rstrip("%"),
        "lib": r["Liberal Democrat"].rstrip("%"),
        "oth": r["Other"].rstrip("%"),
        "pc": r["Plaid Cymru"].rstrip("%"),
        "ref": r["Reform UK"].rstrip("%"),
        "snp": r["Scottish National Party (SNP)"].rstrip("%"),
    }
