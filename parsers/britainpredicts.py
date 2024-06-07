import csv


def parse(path):
    with open("data/constituencies.csv") as f:
        name_to_code = {r[1].lower(): r[0] for r in csv.reader(f)}
    name_to_code["ynys mon"] = name_to_code["ynys môn"]  # ffs

    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        return [parse_one(r, name_to_code) for r in csv.DictReader(f)]


def parse_one(r, name_to_code):
    return {
        "code": name_to_code[r["Constituency"].lower()],
        "name": r["Constituency"],
        "con": r["Con"].rstrip("%"),
        "grn": r["Grn"].rstrip("%"),
        "lab": r["Lab"].rstrip("%"),
        "lib": r["LDem"].rstrip("%"),
        "oth": r["Ind_Oth"].rstrip("%"),
        "pc": r["PC"].rstrip("%"),
        "ref": r["Ref"].rstrip("%"),
        "snp": r["SNP"].rstrip("%"),
    }
