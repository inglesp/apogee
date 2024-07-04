import csv


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        return [parse_one(r) for r in csv.DictReader(f)]


def parse_one(r):
    for k in list(r):
        r[k.strip()] = r[k]

    return {
        "code": get_code(r["PCON24CD"]),
        "name": r["Seat"],
        "con": r["mean_Con"].strip().replace("-", ""),
        "grn": r["mean_Green"].strip().replace("-", ""),
        "lab": r["mean_Lab"].strip().replace("-", ""),
        "lib": r["mean_LDem"].strip().replace("-", ""),
        "oth": r["mean_Other"].strip().replace("-", ""),
        "pc": r["mean_Plaid"].strip().replace("-", ""),
        "ref": r["mean_Reform"].strip().replace("-", ""),
        "snp": r["mean_SNP"].strip().replace("-", ""),
    }


def get_code(code):
    # Some constituency codes are changing and Survation are ahead of everyone else here
    # (source: https://www.data.gov.uk/dataset/30d5f756-2c53-4b2e-af06-3f9f8023395f/postcode-may-2024-to-westminster-parliamentary-constituencies-july-2024-lookup-in-the-uk)

    return {
        "S14000107": "S14000006",  # Ayr, Carrick and Cumnock
        "S14000108": "S14000008",  # Berwickshire, Roxburgh and Selkirk
        "S14000109": "S14000010",  # Central Ayshire
        "S14000110": "S14000040",  # Kilmarnock and Loudoun
        "S14000111": "S14000058",  # West Aberdeenshire and Kincardine
    }.get(code, code)
