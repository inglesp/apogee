import csv


def parse(path):
    with open("data/constituencies.csv") as f:
        three_code_to_ons_code = {r["three_code"]: r["code"] for r in csv.DictReader(f)}

    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        for r in csv.DictReader(f):
            if r["Country"] == "Northern Ireland":
                continue
            code = three_code_to_ons_code[r["Short Code"].split(".")[-1]]
            recommendation = {
                "Green": "grn",
                "Lab": "lab",
                "LD": "lib",
                "PC": "pc",
                "SNP": "snp",
                "Heart": "",
                "None": "?",
                "ToughToCall": "?",
                "": "?",
            }[r["TV Advice"]]

            yield {
                "code": code,
                "name": r["Name"],
                "recommendation": recommendation,
            }
