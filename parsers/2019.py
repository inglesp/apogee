import csv


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        for r in csv.DictReader(f):
            if r["region_name"] == "NI":
                continue
            yield parse_one(r)


def parse_one(r):
    return {
        "code": r["ONS code"],
        "name": r["Boundary Comm name"],
        "con": r["CON%"],
        "grn": r["GRN%"],
        "lab": r["LAB%"],
        "lib": r["LD%"],
        "oth": r["Tot oths%"],
        "pc": r["PC%"],
        "ref": r["BRX%"],
        "snp": r["SNP%"],
    }
