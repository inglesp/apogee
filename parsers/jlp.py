import csv


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        return [parse_one(r) for r in csv.DictReader(f)]


def parse_one(r):
    return {
        "code": r["gss_code"],
        "name": r["name"],
        "con": 100 * float(r["Conservative"] or 0),
        "grn": 100 * float(r["Green Party"] or 0),
        "lab": 100 * float(r["Labour"] or 0),
        "lib": 100 * float(r["Liberal Democrat"] or 0),
        "oth":  100 * float(r["Other"] or 0),
        "pc": 100 * float(r["Plaid Cymru"] or 0),
        "ref": 100 * float(r["Reform UK"] or 0),
        "snp": 100 * float(r["Scottish National Party"] or 0),
    }
