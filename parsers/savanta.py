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
        "con": 100 * float(r["Conservative"]),
        "grn": 100 * float(r["Green"]),
        "lab": 100 * float(r["Labour"]),
        "lib": 100 * float(r["LibDem"]),
        "oth": 100 * (float(r["Other"]) + float(r["Minor"])),
        "pc": 100 * float(r["Plaid"]),
        "ref": 100 * float(r["Reform"]),
        "snp": 100 * float(r["SNP"]),
    }
