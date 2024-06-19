import csv


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        return [parse_one(r) for r in csv.DictReader(f)]


def parse_one(r):
    return {
        "code": r["onscode"],
        "name": r["seatname"],
        "con": float(r["Conservative"]),
        "grn": float(r["Green"]),
        "lab": float(r["Labour"]),
        "lib": float(r["LibDem"]),
        "oth": float(r["Other"]) + float(r["Minor"]),
        "pc": float(r["Plaid"]),
        "ref": float(r["Reform"]),
        "snp": float(r["SNP"]),
    }
