import csv
import functools

from lxml import html


party_map = {
    "CON": "con",
    "Green": "grn",
    "LAB": "lab",
    "LIB": "lib",
    "MIN": "independent",
    "OTH": "oth",
    "Plaid": "pc",
    "Reform": "ref",
    "SNP": "snp",
}


def parse(path):
    rows = [parse_one(filepath) for filepath in path.glob("*.html")]
    return [r for r in rows if r is not None]


def parse_one(path):
    content = path.read_text()
    if "Northern Ireland" in content:
        return
    name = path.parts[-1].split(".")[0]
    code = get_constituency_code(name)
    row = {"code": code, "name": name}
    tree = html.fromstring(content)
    table = tree.xpath('//table[contains(@class, "seatpred")]')[0]
    for tr in table.xpath("tr")[1:-1]:
        values = [td.text_content() for td in tr.xpath("td")]
        row[party_map[values[0]]] = float(values[3].rstrip("%"))
    if "independent" in row:
        if "oth" not in row:
            row["oth"] = 0
        row["oth"] += row["independent"]
        del row["independent"]
    return row


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
