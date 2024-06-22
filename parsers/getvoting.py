import csv

from lxml import html


def parse(path):
    with open("data/constituencies.csv") as f:
        code_to_name = {r[0]: r[1] for r in csv.reader(f)}

    for filepath in path.glob("*.html"):
        code = get_code(filepath.parts[-1].split(".")[0])
        recommendation = parse_one(filepath)
        yield {
            "code": code,
            "name": code_to_name[code],
            "recommendation": recommendation,
        }


def parse_one(path):
    content = path.read_text()
    tree = html.fromstring(content)
    div = tree.xpath('//div[contains(@class, "recommendation_text")]')[0]
    recommendation = div.text_content().strip().splitlines()[-1].strip()
    assert recommendation.startswith("Vote ")
    return {
        "Green": "grn",
        "Labour": "lab",
        "Lib Dem": "lib",
        "Plaid Cymru": "pc",
        "SNP": "snp",
        "with your heart": "",
    }[recommendation[5:]]


def get_code(code):
    # See also parsers/survation.py

    return {
        "S14000107": "S14000006",  # Ayr, Carrick and Cumnock
        "S14000108": "S14000008",  # Berwickshire, Roxburgh and Selkirk
        "S14000109": "S14000010",  # Central Ayshire
        "S14000110": "S14000040",  # Kilmarnock and Loudoun
        "S14000111": "S14000058",  # West Aberdeenshire and Kincardine
    }.get(code, code)
