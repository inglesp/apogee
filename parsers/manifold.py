import csv
import json


def normalise(name):
    return "".join(c for c in sorted(name.lower().split("(")[0]) if c.isalpha())


with open("data/constituencies.csv") as f:
    normalised_name_to_code = {
        normalise(r["name"]): r["code"] for r in csv.DictReader(f)
    }

special_cases = {
    "Central Ayreshire": "S14000010",
    "Hull East": "E14001313",
    "Ynys Mon (Anglesey)": "W07000112",
}

party_map = {
    "Conservatives": "con",
    "Green": "grn",
    "Labour": "lab",
    "LiberalDemocrats": "lib",
    "Other": "oth",
    "PlaidCymru": "pc",
    "Reform": "ref",
    "SNP": "snp",
}

parties = sorted(party_map.values())


def parse():
    rows = []

    with open("data/raw/manifold/2024-07-04/election-2024.json") as f:
        for c in json.load(f)["constituencies"]:
            stats = c["stats"]
            if {
                stats["labour_probability"],
                stats["conservative_probability"],
                stats["lib_dem_probability"],
                stats["green_probability"],
                stats["reform_probability"],
            } == {None}:
                # Northern Ireland
                continue

            name = c["constituency"]
            code = normalised_name_to_code.get(normalise(name), special_cases.get(name))
            assert code is not None
            row = {"code": code, "name": name, "oth": 0}
            for p in c["parties"]:
                if (
                    isinstance(p["name"], dict)
                    or p["name"] == "Other"
                    or p["name"] not in party_map
                ):
                    row["oth"] += float(p["probability"])
                else:
                    row[party_map[p["name"]]] = p["probability"]
            for p in parties:
                if p not in row:
                    row[p] = 0
            rows.append(row)

    rows.sort(key=lambda r: r["code"])

    with open("data/processed/manifold/2024-07-04/data.csv", "w") as f:
        writer = csv.DictWriter(f, ["code", "name", *parties])
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parse()
