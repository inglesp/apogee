import csv
from collections import defaultdict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


def main():
    env = Environment(loader=FileSystemLoader("."))

    with open("outputs/predictions.csv") as f:
        predictions = list(csv.DictReader(f))
    tpl = env.get_template("templates/index.html")
    ctx = {"rows": predictions}
    with open("outputs/index.html", "w") as f:
        f.write(tpl.render(ctx))

    with open("outputs/details.csv") as f:
        details = list(csv.DictReader(f))
    details_by_constituency = defaultdict(list)
    for row in details:
        details_by_constituency[row["code"]].append(row)

    tpl = env.get_template("templates/constituency.html")
    for code, details in details_by_constituency.items():
        details.sort(
            key=lambda row: sum(
                int(v) for k, v in row.items() if k not in ["code", "name", "party"]
            ),
            reverse=True,
        )
        ctx = {"name": details[0]["name"], "rows": details}
        dirpath = Path(f"outputs/constituencies/{code}")
        dirpath.mkdir(parents=True, exist_ok=True)
        (dirpath / "index.html").write_text(tpl.render(ctx))


if __name__ == "__main__":
    main()
