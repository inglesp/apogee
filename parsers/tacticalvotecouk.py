import csv


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        for r in csv.DictReader(f):
            if r["id"][0] == "N":
                # Northern Ireland
                continue
            recommendation = {
                "Any": "",
                "Green": "grn",
                "LD": "lib",
                "Labour or SNP": "?",
                "Labour": "lab",
                "Lib Dem": "lib",
                "Plaid Cymru": "pc",
                "SNP": "snp",
                "Labour or Plaid Cymru": "?",
                "TBC": "?",
                "Not sure": "?",
                "Not Sure": "?",
            }[r["Vote For"]]

            yield {
                "code": r["id"],
                "name": r["Constituency"],
                "recommendation": recommendation,
            }
