from lxml import html


party_map = {
    "Conservative": "con",
    "Green": "grn",
    "Labour": "lab",
    "Liberal Democrats": "lib",
    "Others": "oth",
    "Plaid Cymru": "pc",
    "SNP": "snp",
    "Speaker": "speaker",
    "Reform": "ref",
}


def parse(path):
    return [parse_one(filepath) for filepath in path.glob("*.html")]


def parse_one(path):
    code = path.parts[-1].split(".")[0]
    content = path.read_text()
    tree = html.fromstring(content)
    name = tree.find(".//h4").text_content()
    row = {"code": code, "name": name}
    table = tree.xpath('//table[contains(@class, "TableEl-sc-upst2p-0")]')[0]
    for tr in table.xpath(".//tr")[1:]:
        values = [td.text_content() for td in tr.xpath("td")]
        row[party_map[values[0]]] = values[1]
    return row
