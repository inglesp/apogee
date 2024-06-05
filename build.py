import csv
import json
from collections import defaultdict
from pathlib import Path


def main():
    predictions = defaultdict(dict)
    details = defaultdict(dict)
    parties = set()
    sources = []

    for dirpath in sorted(Path("data/processed").glob("*")):
        source = dirpath.parts[-1]
        sources.append(source)
        datapath = sorted(dirpath.glob("*/data.json"))[-1]
        with datapath.open() as f:
            data = json.load(f)
        for code, item in data.items():
            # if code == "E14001232":
            #     if "lib" not in item["2024"]:
            #         breakpoint()
            #     print(source)
            #     print(item)
            predictions[code][source] = item["party"]
            details[code][source] = item["2024"]
            parties |= set(item["2024"])

    with open("data/constituencies.csv") as f:
        constituencies = {r["code"]: r for r in csv.DictReader(f)}

    predictions = [
        {
            "code": code,
            "name": constituencies[code]["name"],
            "_2019": constituencies[code]["_2019"],
            "disagreement": int(len(set(v.values())) > 1),
        }
        | v
        for code, v in predictions.items()
        if code != "E14001170"  # Chorley, the speaker's constituency
    ]
    predictions.sort(key=lambda row: row["name"])

    with open("outputs/predictions.csv", "w") as f:
        writer = csv.DictWriter(f, ["code", "name", "_2019", *sources, "disagreement"])
        writer.writeheader()
        writer.writerows(predictions)

    details = [
        {
            "code": code,
            "name": constituencies[code]["name"],
            "party": party,
        }
        | {source: v[source].get(party, 0) for source in sources}
        for code, v in details.items()
        for party in parties
        if code != "E14001170"  # Chorley, the speaker's constituency
    ]
    details = [r for r in details if any(r[source] > 0 for source in sources)]
    details.sort(key=lambda row: (row["name"], row["party"]))

    with open("outputs/details.csv", "w") as f:
        writer = csv.DictWriter(f, ["code", "name", "party", *sources])
        writer.writeheader()
        writer.writerows(details)


if __name__ == "__main__":
    main()
