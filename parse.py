import csv
import importlib.util
import sys
from operator import itemgetter
from pathlib import Path


parties = [
    "con",
    "grn",
    "lab",
    "lib",
    "oth",
    "pc",
    "ref",
    "snp",
]


def run(path):
    model = path.parts[-2]
    parse = load_parse_fn(Path(f"parsers/{model}.py"))
    rows = sorted(parse(path), key=itemgetter("code"))

    # Ensure there's an entry for each party
    for row in rows:
        for p in parties:
            if p not in row or row[p] == "":
                row[p] = 0

    # Drop Chorley, the speaker's constituency
    rows = [r for r in rows if r["code"] != "E14001170"]

    date = path.parts[-1]
    dirpath = Path(f"data/processed/{model}/{date}")
    dirpath.mkdir(parents=True, exist_ok=True)

    with (dirpath / "data.csv").open("w") as f:
        writer = csv.DictWriter(f, ["code", "name"] + parties)
        writer.writeheader()
        writer.writerows(rows)


def load_parse_fn(path):
    # https://docs.python.org/3.12/library/importlib.html#importing-a-source-file-directly
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.parse


if __name__ == "__main__":
    run(Path(sys.argv[1]))
