import csv


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open(encoding="utf-8-sig") as f:
        return [parse_one(r) for r in csv.DictReader(f)]


def parse_one(r):
    return {
        "code": r["pcon"],
        "name": r["pcon_name"],
        "con": r["con_est"].rstrip("%").replace("NA", ""),
        "grn": r["grn_est"].rstrip("%").replace("NA", ""),
        "lab": r["lab_est"].rstrip("%").replace("NA", ""),
        "lib": r["ld_est"].rstrip("%").replace("NA", ""),
        "oth": r["oth_est"].rstrip("%").replace("NA", ""),
        "pc": r["pc_est"].rstrip("%").replace("NA", ""),
        "ref": r["ref_est"].rstrip("%").replace("NA", ""),
        "snp": r["snp_est"].rstrip("%").replace("NA", ""),
    }
