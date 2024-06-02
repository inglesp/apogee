import json
import sys
from pathlib import Path

from lxml import html


def parse(path):
    data = {}

    for filepath in path.glob("*.html"):
        code = filepath.parts[-1].split(".")[0]
        content = filepath.read_text()
        tree = html.fromstring(content)
        name = tree.find(".//h4").text_content()
        print(code, name)
        item = {"name": name, "2024": {}}
        table = tree.xpath('//table[contains(@class, "TableEl-sc-upst2p-0")]')[0]
        for row in table.xpath(".//tr")[1:-1]:
            values = [td.text_content() for td in row.xpath("td")]
            party = {
                "Conservative": "con",
                "Green": "grn",
                "Labour": "lab",
                "Liberal Democrats": "lib",
                "Others": "oth",
                "Plaid Cymru": "pc",
                "SNP": "snp",
                "Speaker": "speaker",
                "Reform": "ref",
            }[values[0]]
            item["2024"][party] = round(float(values[1]))
        item["party"] = max(item["2024"].items(), key=lambda pair: pair[1])[0]
        data[code] = item

    date = path.parts[-1]
    dirpath = Path(f"data/processed/ft/{date}")
    dirpath.mkdir(parents=True, exist_ok=True)

    with (dirpath / "data.json").open("w") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    path = Path(sys.argv[1])
    parse(path)
