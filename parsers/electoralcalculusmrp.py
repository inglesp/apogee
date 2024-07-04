import csv
import functools


def parse(path):
    csv_paths = list(path.glob("*.csv"))
    assert len(csv_paths) == 1
    with csv_paths[0].open() as f:
        return [parse_one(r) for r in csv.DictReader(f)]


def parse_one(r):
    name = r["Seat Name"]
    code = get_constituency_code(name)

    if code[0] == "S":
        snp = 100 * float(r["SNP/Plaid"])
        pc = 0
    elif code[0] == "W":
        snp = 0
        pc = 100 * float(r["SNP/Plaid"])
    else:
        snp = pc = 0

    return {
        "code": code,
        "name": name,
        "con": 100 * float(r["CON"]),
        "grn": 100 * float(r["Green"]),
        "lab": 100 * float(r["LAB"]),
        "lib": 100 * float(r["LIB"]),
        "oth": 100 * float(r["Other"]) + 100 * float(r["Indept."]),
        "ref": 100 * float(r["Reform"]),
        "pc": pc,
        "snp": snp,
    }


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
