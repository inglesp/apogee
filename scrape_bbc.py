import csv

import httpx
from lxml import html


path = "data/processed/2024/2024-07-04/data.csv"

parties = [
    "con",
    "grn",
    "lab",
    "lib",
    "oth",
    "pc",
    "snp",
    "ref",
]

party_map = {
    "Conservative": "con",
    "Green": "grn",
    "Labour": "lab",
    "Liberal Democrat": "lib",
    "Plaid Cymru": "pc",
    "Reform UK": "ref",
    "Scottish National Party": "snp",
}


def get_new_codes():
    with open(path) as f:
        rows = list(csv.DictReader(f))

    codes_we_have = {r["code"] for r in rows if any(r[p] != "0" for p in parties)}
    codes_with_results = set()

    rsp = httpx.get("https://www.bbc.co.uk/news/election/2024/uk/constituencies")
    tree = html.fromstring(rsp.text)
    for li in tree.xpath("//main//li"):
        hrefs = [a.get("href") for a in li.xpath(".//a")]
        if len(hrefs) != 1:
            continue
        href = hrefs[0]
        if not href.startswith("/news/election/2024/uk/constituencies/"):
            continue
        a = li.xpath(".//a")[0]
        if a.xpath("following-sibling::*"):
            codes_with_results.add(href.split("/")[-1])

    return codes_with_results - codes_we_have


def update(code):
    with open(path) as f:
        rows = list(csv.DictReader(f))

    old_row = [r for r in rows if r["code"] == code][0]
    name = old_row["name"]

    print(f"Updating {code} ({name})")

    rows = [r for r in rows if r != old_row]
    new_row = get_row_for_code(code)
    new_row["name"] = name
    rows.append(new_row)
    rows.sort(key=lambda row: row["code"])

    with open(path, "w") as f:
        writer = csv.DictWriter(f, ["code", "name", *parties])
        writer.writeheader()
        writer.writerows(rows)


def get_row_for_code(code):
    row = {"code": code}
    rsp = httpx.get(
        f"https://www.bbc.co.uk/news/election/2024/uk/constituencies/{code}"
    )
    tree = html.fromstring(rsp.text)

    for li in tree.xpath("//ol//li"):
        spans = li.xpath(".//span")
        if any("Supertitle" in span.get("class", "") for span in spans):
            supertitle_span = [
                span for span in spans if "Supertitle" in span.get("class", "")
            ][0]
            result_span = [
                span for span in spans if "ResultValue" in span.get("class", "")
            ][1]
            party_name = supertitle_span.text_content().strip().strip(",")
            if party_name not in party_map:
                continue
            party = party_map[party_name]
            percent = result_span.text_content().strip("%")
            row[party] = percent

    total = sum(float(v) for k, v in row.items() if k != "code")
    row["oth"] = f"{100 - total:.1f}"

    for party in parties:
        if party not in row:
            row[party] = 0

    return row


if __name__ == "__main__":
    for code in get_new_codes():
        update(code)
