import csv
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader


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

model_map = {
    "britainpredicts": "Britain Predicts",
    "economist": "Economist",
    "electoralcalculus": "Electoral Calculus",
    "ft": "FT",
    "ipsos": "Ipsos",
    "moreincommon": "More in Common",
    "survation": "Survation",
    "yougov": "YouGov",
}

models = sorted(model_map)


def main():
    with open("data/constituencies.csv") as f:
        constituencies = list(csv.DictReader(f))

    code_to_name = {c["code"]: c["name"] for c in constituencies}
    code_to_2019 = {c["code"]: c["2019"] for c in constituencies}

    data = None

    for model in models:
        path = sorted(Path(f"data/processed/{model}").glob("*/data.csv"))[-1]
        model_data = pd.read_csv(path)
        model_data["model"] = model
        if data is None:
            data = model_data
        else:
            data = pd.concat([data, model_data])

    data = data.drop("name", axis=1)
    data["prediction"] = data[parties].idxmax(axis=1)

    predictions = data[["code", "model", "prediction"]].pivot(
        index="code", columns="model"
    )
    predictions.columns = predictions.columns.droplevel(0)
    predictions.columns.name = None
    predictions["name"] = predictions.index.map(code_to_name)
    predictions["2019"] = predictions.index.map(code_to_2019)
    predictions["disagreement"] = (predictions[models].nunique(axis=1) > 1).astype(int)
    predictions = predictions.sort_values("name")
    predictions = predictions[["name", "2019", *models, "disagreement"]]

    predictions.to_csv("outputs/data/predictions.csv")

    summary = (
        pd.DataFrame(
            {model: predictions[model].value_counts() for model in ["2019", *models]}
        )
        .fillna(0)
        .astype(int)
    )
    summary["total"] = summary[models].sum(axis=1)
    summary = summary.sort_values("total", ascending=False)
    summary = summary[["2019", *models]]

    summary.to_csv("outputs/data/summary.csv")

    details = (
        data.drop("prediction", axis=1)
        .melt(id_vars=["code", "model"], value_vars=parties, var_name="party")
        .pivot_table(index=["code", "party"], columns="model")
        .reset_index()
    )
    details.columns = ["code", "party"] + models
    details["name"] = details["code"].map(code_to_name)
    details["2019"] = details["code"].map(code_to_2019)
    details = details[["code", "name", "2019", "party", *models]]

    details.to_csv("outputs/data/details.csv", index=False)

    env = Environment(loader=FileSystemLoader("."))

    tpl = env.get_template("templates/index.html")
    ctx = {
        "parties": parties,
        "summary": df_to_list_of_lists(summary),
        "predictions": df_to_list_of_lists(predictions),
    }
    with open("outputs/index.html", "w") as f:
        f.write(tpl.render(ctx))

    tpl = env.get_template("templates/constituency.html")
    for code in details["code"].unique():
        constituency_details = details[details["code"] == code].set_index("party")
        constituency_details["total"] = constituency_details[models].sum(axis=1)
        constituency_details = constituency_details.sort_values(
            "total", ascending=False
        )
        constituency_details = constituency_details[models]
        constituency_details = constituency_details[
            constituency_details.sum(axis=1) > 0
        ]

        ctx = {
            "name": code_to_name[code],
            "constituency_details": df_to_list_of_lists(constituency_details),
        }
        dirpath = Path(f"outputs/constituencies/{code}")
        dirpath.mkdir(parents=True, exist_ok=True)
        (dirpath / "index.html").write_text(tpl.render(ctx))


def df_to_list_of_lists(df):
    df = df.rename(
        {"code": "", "name": "Constituency", "2019": "2019 (nominal)"} | model_map,
        axis=1,
    )
    rv = [[""] + list(df.columns)]
    for ix, row in df.iterrows():
        rv.append([ix] + list(row))
    return rv


if __name__ == "__main__":
    main()
