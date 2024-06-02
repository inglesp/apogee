import csv
import functools
import json
import sys
from pathlib import Path

from lxml import html


def parse(path):
    data = {}

    for filepath in path.glob("*.html"):
        content = filepath.read_text()
        if "Northern Ireland" in content:
            continue
        name = filepath.parts[-1].split(".")[0]
        code = get_constituency_code(name)
        item = {"name": name, "2019": {}, "2024": {}}
        tree = html.fromstring(content)
        table = tree.xpath('//table[contains(@class, "seatpred")]')[0]
        for row in table.xpath("tr")[1:-1]:
            values = [td.text_content() for td in row.xpath("td")]
            party = {
                "CON": "con",
                "Green": "grn",
                "LAB": "lab",
                "LIB": "lib",
                "MIN": "independent",
                "OTH": "oth",
                "Plaid": "pc",
                "SNP": "snp",
                "Reform": "ref",
            }[values[0]]
            item["2019"][party] = round(float(values[2].rstrip("%")))
            item["2024"][party] = round(float(values[3].rstrip("%")))
        for year in ["2019", "2024"]:
            if "independent" in item[year]:
                if "oth" not in item[year]:
                    item[year]["oth"] = 0
                item[year]["oth"] += item[year]["independent"]
                del item[year]["independent"]
        item["party"] = max(item["2024"].items(), key=lambda pair: pair[1])[0]
        data[code] = item

    date = path.parts[-1]
    dirpath = Path(f"data/processed/electoralcalculus/{date}")
    dirpath.mkdir(parents=True, exist_ok=True)

    with (dirpath / "data.json").open("w") as f:
        json.dump(data, f, indent=2)


def get_constituency_code(name):
    special_cases = {
        "Hull East": "E14001313",  # Kingston upon Hull East
        "Carmarthen": "W07000087",  # Caerfyrddin
        "Ynys Mon (Anglesey)": "W07000112",  # Ynys Môn
    }
    if name in special_cases:
        return special_cases[name]
    return normalised_name_to_code()[normalise(name)]


@functools.cache
def normalised_name_to_code():
    # Electoral Calculus prefers eg "Suffolk North" to "North Suffolk" or
    # "Wrekin, The" to "The Wrekin", and has a few other oddities around
    # punctuation and things in parentheses...
    with open("data/constituencies.csv") as f:
        name_to_code = {r[1]: r[0] for r in csv.reader(f)}

    rv = {normalise(name): code for name, code in name_to_code.items()}
    assert len(rv) == len(name_to_code)
    return rv


def normalise(name):
    name = name.lower()
    name = name.split("(")[0]
    return "".join(c for c in sorted(name) if c.isalpha())


if __name__ == "__main__":
    path = Path(sys.argv[1])
    parse(path)
