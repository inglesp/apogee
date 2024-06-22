import csv


def parse(path):
    with open("data/constituencies.csv") as f:
        three_code_to_ons_code = {r["three_code"]: r["code"] for r in csv.DictReader(f)}

    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        for r in csv.DictReader(f):
            if r["threecode"] not in three_code_to_ons_code:
                continue
            code = three_code_to_ons_code[r["threecode"]]
            recommendation = {
                "Green": "grn",
                "Labour": "lab",
                "Liberal Democrat": "lib",
                "None": "",
                "Not needed": "",
                "Not sure": "?",
                "Plaid Cymru": "pc",
                "Scottish National Party": "snp",
                "Withdrawn": "?",
            }[r["recommendation"]]
            yield {
                "code": code,
                "name": r["constituency"],
                "recommendation": recommendation,
            }
