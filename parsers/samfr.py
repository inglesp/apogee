import csv
import sys


def normalise(name):
    return "".join(c for c in sorted(name.lower().split("(")[0]) if c.isalpha())


with open("data/constituencies.csv") as f:
    normalised_name_to_code = {
        normalise(r["name"]): r["code"] for r in csv.DictReader(f)
    }


special_cases = {
    "Birimingham Northfield": "E14001097",
    "Brighton Pavillion": "E14001130",
    "Google and Pocklington": "E14001250",
    "Gordan and Buchan": "S14000091",
    "Keighly and Ilkley": "E14001308",
    "Penistone and Stockbridge": "E14001423",
    "Streford and Urmston": "E14001528",
    "Welwyn Hatfeld": "E14001573",
    "Westmoreland and Lonsdale": "E14001580",
    "Ynys Mon": "W07000112",
}

party_map = {
    "Conservative": "con",
    "Green": "grn",
    "Independent": "oth",
    "LD": "lib",
    "Labour": "lab",
    "Plaid Cymru": "pc",
    "Reform": "ref",
    "SNP": "snp",
}

probability_map = {
    "Lean": 60,
    "Likely": 80,
    "Safe": 100,
}


def parse(path):
    with open(path) as f:
        rows = [
            parse_one(r)
            for r in csv.DictReader(f)
            if r["Constituency"] not in ("", "Chorley")
            and r["Region"] != "Northern Ireland"
        ]

    rows.sort(key=lambda r: r["code"])

    with open("data/processed/samfr/2024-07-04/data.csv", "w") as f:
        writer = csv.DictWriter(f, ["code", "name", "party", "probability"])
        writer.writeheader()
        writer.writerows(rows)


def parse_one(r):
    name = r["Constituency"]
    probability, party = r["Prediction"].split(" ", 1)
    return {
        "name": name,
        "code": normalised_name_to_code.get(normalise(name), special_cases.get(name)),
        "party": party_map[party],
        "probability": probability_map[probability],
    }


if __name__ == "__main__":
    parse(sys.argv[1])
