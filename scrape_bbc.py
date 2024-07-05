import csv
from datetime import datetime

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

party_name_to_code = {
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
            code = href.split("/")[-1]
            if code[0] == "N":
                continue  # Northern Ireland
            if code == "E14001170":
                continue  # Chorley
            codes_with_results.add(code)

    return codes_with_results - codes_we_have


def update(code):
    results = get_results_for_code(code)
    if results is None:
        return

    with open(path) as f:
        rows = list(csv.DictReader(f))

    name = None

    for row in rows:
        if row["code"] == code:
            name = row["name"]
            for party in parties:
                row[party] = f"{results[party]:.3f}"

    assert name is not None, code
    print(f"{datetime.now()} Updating {code} ({name})")

    with open(path, "w") as f:
        writer = csv.DictWriter(f, ["code", "name", *parties])
        writer.writeheader()
        writer.writerows(rows)


def get_results_for_code(code):
    rsp = httpx.get(
        f"https://www.bbc.co.uk/news/election/2024/uk/constituencies/{code}"
    )
    tree = html.fromstring(rsp.text)

    results = []

    for li in tree.xpath("//ol//li"):
        spans = li.xpath(".//span")
        if any("Supertitle" in span.get("class", "") for span in spans):
            party_name = (
                [span for span in spans if "Supertitle" in span.get("class", "")][0]
                .text_content()
                .strip()
                .strip(",")
            )
            num_votes = int(
                [span for span in spans if "ResultValue" in span.get("class", "")][0]
                .text_content()
                .replace(",", "")
            )
            results.append(
                {
                    "party": party_name_to_code.get(party_name, "oth"),
                    "num_votes": num_votes,
                }
            )

    total_num_votes = sum(r["num_votes"] for r in results)

    if total_num_votes == 0:
        # Full details not yet published
        return

    all_num_votes = [r["num_votes"] for r in results]
    assert all_num_votes == sorted(all_num_votes, reverse=True), code

    oth_votes = sum(r["num_votes"] for r in results if r["party"] == "oth")
    if oth_votes > results[1]["num_votes"]:
        # If the total votes for "oth" candidates is greater than the number of
        # votes for the winner, we'll incorrectly claim that "oth" has taken
        # the seat.  If the total votes for "oth" candidates is greater than
        # the number of votes for the runner up, we'll get the majority
        # calculation wrong.  So in either case, we have to ignore all "oth"
        # votes apart from the first.  Next time: do better.

        # Not sure how we'd handle "oth" candidates coming first and second...
        assert not (results[0]["party"] == "oth" and results[1]["party"] == "oth"), code
        oth_votes = [r for r in results if r["party"] == "oth"][0]["num_votes"]

    results = {r["party"]: r["num_votes"] for r in results}
    results["oth"] = oth_votes
    for p in parties:
        if p not in results:
            results[p] = 0

    return {p: 100 * results[p] / total_num_votes for p in parties}


if __name__ == "__main__":
    for code in get_new_codes():
        update(code)
