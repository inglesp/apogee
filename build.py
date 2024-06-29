import csv
import shutil
from datetime import datetime
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

with open("data/constituencies.csv") as f:
    constituencies = list(csv.DictReader(f))

code_to_name = {c["code"]: c["name"] for c in constituencies}
code_to_2019 = {c["code"]: c["2019"] for c in constituencies}
code_to_demo_club_code = {c["code"]: c["demo_club_code"] for c in constituencies}

model_map = {
    "britainpredicts": {
        "title": "Britain Predicts",
        "full_title": "Britain Predicts (New Statesman)",
        "url": "https://sotn.newstatesman.com/2024/05/britainpredicts",
    },
    "economist": {
        "title": "Economist",
        "full_title": "The Economist",
        "url": "https://www.economist.com/interactive/uk-general-election/forecast",
    },
    "electionmaps": {
        "title": "electionmaps",
        "url": "https://electionmaps.uk/nowcast",
    },
    "electoralcalculus": {
        "title": "Electoral Calculus",
        "url": "https://www.electoralcalculus.co.uk/dynamicmap.html",
    },
    "focaldata": {
        "title": "Focaldata",
        "url": "https://www.focaldata.com/blog/focaldata-prolific-uk-general-election-mrp",
    },
    "ft": {
        "title": "FT",
        "full_title": "The FT",
        "url": "https://ig.ft.com/uk-general-election/2024/projection/",
    },
    "ipsos": {
        "title": "Ipsos",
        "url": "https://www.ipsos.com/en-uk/uk-opinion-polls/ipsos-election-mrp",
    },
    "moreincommon": {
        "title": "More in Common",
        "url": "https://www.moreincommon.org.uk/general-election-2024/mrp/",
    },
    "savanta": {
        "title": "Savanta",
        "url": "https://savanta.com/knowledge-centre/press-and-polls/mrp-model-daily-telegraph-19-june-2024/",
    },
    "survation": {
        "title": "Survation",
        "url": "https://www.survation.com/survation-mrp-update-labour-set-to-become-the-largest-party-in-scotland/",
    },
    "wethink": {
        "title": "WeThink",
        "url": "https://wethink.report/news-hub/news/we-think-mrp-historical-low-for-the-conservatives/",
    },
    "yougov": {
        "title": "YouGov",
        "url": "https://yougov.co.uk/politics/articles/49809",
    },
}
models = sorted(model_map)


def main():
    build_predictions()
    build_predictions_all()
    build_recommendations()


def build_predictions():
    def df_to_list_of_lists(df):
        df = df.rename(
            {"code": "", "name": "Constituency", "2019": "2019 (nominal)"}
            | {k: v["title"] for k, v in model_map.items()},
            axis=1,
        )
        rv = [[""] + list(df.columns)]
        for ix, row in df.iterrows():
            rv.append([ix] + list(row))
        return rv

    data = None

    for model in models:
        path = sorted(Path(f"data/processed/{model}").glob("*/data.csv"))[-1]
        model_map[model]["date"] = datetime.strptime(path.parts[-2], "%Y-%m-%d")
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
    predictions = predictions.sort_values("name")
    predictions = predictions[["name", "2019", *models]]

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

    env = Environment(loader=FileSystemLoader("."))

    tpl = env.get_template("templates/index.html")
    ctx = {
        "models": model_map.values(),
        "parties": parties,
        "summary": df_to_list_of_lists(summary),
        "predictions": df_to_list_of_lists(predictions),
    }
    with open("outputs/index.html", "w") as f:
        f.write(tpl.render(ctx))

    shutil.copyfile("templates/index.js", "outputs/index.js")

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
            "demo_club_code": code_to_demo_club_code[code],
            "constituency_details": df_to_list_of_lists(constituency_details),
        }
        dirpath = Path(f"outputs/constituencies/{code}")
        dirpath.mkdir(parents=True, exist_ok=True)
        (dirpath / "index.html").write_text(tpl.render(ctx))


def build_predictions_all():
    data = None

    for path in sorted(Path("data/processed").glob("*/*/data.csv")):
        if path.parts[2] not in models:
            continue
        model_data = pd.read_csv(path)
        model_data["model"] = path.parts[2]
        model_data["scrape_date"] = path.parts[3]
        if data is None:
            data = model_data
        else:
            data = pd.concat([data, model_data])

    data = data.drop("name", axis=1)
    data = pd.melt(
        data,
        id_vars=["model", "scrape_date", "code"],
        value_vars=parties,
        var_name="party",
        value_name="prediction",
    )

    data.to_csv("outputs/data/predictions-all.csv", index=False)


def build_recommendations():
    recommender_map = {
        "getvoting": {
            "title": "GetVoting",
            "full_title": "GetVoting (Best for Britain)",
            "url": "https://www.getvoting.org/",
        },
        "stopthetories": {
            "title": "StopTheTories",
            "url": "https://stopthetories.vote/",
        },
        "tacticalvote": {
            "title": "tactical.vote",
            "url": "https://tactical.vote/",
        },
        "tacticalvotecouk": {
            "title": "Tactical Vote",
            "url": "https://tacticalvote.co.uk/",
        },
    }
    recommenders = sorted(recommender_map)

    data = None

    for recommender in recommenders:
        path = sorted(Path(f"data/processed/{recommender}").glob("*/data.csv"))[-1]
        if recommender == "stopthetories":
            recommender_map[recommender]["date"] = datetime.strptime(
                path.parts[-2][:8], "%Y%m%d"
            )
        else:
            recommender_map[recommender]["date"] = datetime.strptime(
                path.parts[-2], "%Y-%m-%d"
            )
        recommender_data = pd.read_csv(path)
        recommender_data["recommender"] = recommender
        if data is None:
            data = recommender_data
        else:
            data = pd.concat([data, recommender_data])

    data = data.drop("name", axis=1)
    recommendations = data.pivot(index="code", columns="recommender").fillna("")
    recommendations.columns = recommendations.columns.droplevel(0)
    recommendations.columns.name = None
    recommendations["name"] = recommendations.index.map(code_to_name)
    recommendations["2019"] = recommendations.index.map(code_to_2019)

    def is_interesting(row):
        recommendations = set(row[recommenders]) - {""}
        if len(recommendations) > 1:
            return True
        if len(recommendations) == 1:
            if (list(recommendations)[0] != row["2019"]) and (row["2019"] != "con"):
                return True
        return False

    recommendations["interesting"] = recommendations.apply(
        is_interesting, axis=1
    ).astype(int)
    recommendations = recommendations.sort_values("name")
    recommendations = recommendations[["name", "2019", *recommenders, "interesting"]]

    headers = ["", "Constituency", "2019"] + [
        recommender_map[r]["title"] for r in recommenders
    ]
    body = []
    for code, row in recommendations.iterrows():
        body.append(
            {
                "code": code,
                "name": row["name"],
                "2019": row["2019"],
                "recommendations": [
                    {
                        "party": row[r] or "&nbsp;",
                        "css_class": f"party-{row[r]}"
                        if row[r] in parties
                        else "party-none",
                        "url": build_tv_url(r, code),
                    }
                    for r in recommenders
                ],
                "interesting": row["interesting"],
            }
        )

    env = Environment(loader=FileSystemLoader("."))

    tpl = env.get_template("templates/tactical-voting.html")
    ctx = {
        "recommenders": recommender_map.values(),
        "headers": headers,
        "body": body,
    }
    with open("outputs/tactical-voting/index.html", "w") as f:
        f.write(tpl.render(ctx))


def build_tv_url(recommender, code):
    if recommender == "getvoting":
        return f"https://www.getvoting.org/constituency/{code}"
    if recommender == "stopthetories":
        slug = code_to_demo_club_code[code].split(".")[1]
        return f"https://stopthetories.vote/parl/{slug}"
    if recommender == "tacticalvote":
        slug = code_to_demo_club_code[code].split(".")[1]
        return f"https://tactical.vote/{slug}/"
    if recommender == "tacticalvotecouk":
        name = code_to_name[code]
        name = name.replace(" and ", "")
        slug = "".join([c for c in name if c.isalpha() and c.isascii()])
        return f"https://tacticalvote.co.uk/#{slug}"
    assert False, recommender


if __name__ == "__main__":
    main()
