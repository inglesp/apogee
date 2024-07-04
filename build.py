import csv
import json
import shutil
from collections import Counter
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

# This matches the predicted order and was originally computed, but hardcoding for convenience
ordered_parties = [
    "lab",
    "con",
    "lib",
    "snp",
    "pc",
    "ref",
    "grn",
    "oth",
    "tie",
    "?",
]

with open("data/constituencies.csv") as f:
    constituencies = [
        c for c in csv.DictReader(f) if c["code"] != "E14001170"
    ]  # Chorley

codes = {c["code"] for c in constituencies}
code_to_name = {c["code"]: c["name"] for c in constituencies}
code_to_2019 = {c["code"]: c["2019"] for c in constituencies}
code_to_demo_club_code = {c["code"]: c["demo_club_code"] for c in constituencies}

model_map = {
    "2019": {
        "title": "2019 (notional)",
        "url": "https://downloads.bbc.co.uk/news/nol/shared/spl/xls_spreadsheets/results_spreadsheet.ods",
    },
    "2024": {
        "title": "2024",
        "url": "TODO",
    },
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
        "title": "Electoral Calc. STM",
        "url": "https://www.electoralcalculus.co.uk/dynamicmap.html",
    },
    "electoralcalculusmrp": {
        "title": "Electoral Calc. MRP",
        "url": "https://www.electoralcalculus.co.uk/blogs/ec_vipoll_20240626.html",
    },
    "focaldata": {
        "title": "Focaldata",
        "url": "https://www.focaldata.com/blog/focaldata-prolific-uk-general-election-mrp-final-call",
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
    "jlp": {
        "title": "JLP",
        "url": "https://jlpartners.co.uk/final-jl-partners-srp-model-project-labour-winning-442-seats",
    },
    "moreincommon": {
        "title": "More in Common",
        "url": "https://www.moreincommon.org.uk/general-election-2024/mrp-3-july/",
    },
    "savanta": {
        "title": "Savanta",
        "url": "https://savanta.com/knowledge-centre/press-and-polls/mrp-model-daily-telegraph-19-june-2024/",
    },
    "survation": {
        "title": "Survation",
        "url": "https://www.survation.com/survation-mrp-labour-99-certain-to-win-more-seats-than-in-1997/",
    },
    "wethink": {
        "title": "WeThink",
        "url": "https://wethink.report/news-hub/news/we-think-mrp-historical-low-for-the-conservatives/",
    },
    "yougov": {
        "title": "YouGov",
        "url": "https://yougov.co.uk/politics/articles/49950-final-yougov-mrp-shows-labour-on-course-for-historic-election-victory",
    },
}
models = sorted(model_map)


class TruncateFloatEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, float):
            return format(obj, ".1f")
        elif isinstance(obj, list):
            return "[" + ", ".join(self.encode(el) for el in obj) + "]"
        elif isinstance(obj, dict):
            items = (self.encode(k) + ": " + self.encode(v) for k, v in obj.items())
            return "{" + ", ".join(items) + "}"
        else:
            return json.JSONEncoder.encode(self, obj)


def main():
    build_predictions()
    build_predictions_all()
    build_recommendations()


def build_predictions():
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
    data = data[["code", "model", *parties]]
    winner = data[parties].idxmax(axis=1)
    winner[data[parties].eq(data[parties].max(axis=1), axis=0).sum(axis=1) > 1] = "tie"
    winner[data[parties].sum(axis=1) == 0] = "?"
    data["winner"] = winner

    def get_two_largest(row):
        largest = row.nlargest(2)
        return pd.Series({0: largest.iloc[0], 1: largest.iloc[1]})

    two_largest = data[parties].apply(get_two_largest, axis=1)
    data["votes0"] = two_largest[0]
    data["votes1"] = two_largest[1]

    def get_majority(party, row):
        if party == row["winner"]:
            return row[party] - row["votes1"]
        else:
            return row[party] - row["votes0"]

    for party in parties:
        data[f"majority-{party}"] = data.apply(
            lambda row: get_majority(party, row), axis=1
        )

    data = data.drop(["votes0", "votes1"], axis=1)

    def get_margin(row):
        winner = row["winner"]
        if winner not in parties:
            return "unknown"
        majority = row[f"majority-{row['winner']}"]
        if majority > 10:
            return "comfortable"
        elif majority > 5:
            return "close"
        else:
            return "very-close"

    data["margin"] = data.apply(get_margin, axis=1)

    corr_coeff = {}
    for c in codes:
        df = data[(data["code"] == c) & (data["model"] != "2019")]
        corr_coeff[c] = (
            (
                df[["model", *parties]]
                .set_index("model")
                .transpose()
                .corr()
                .sum()
                .sum()
                - (len(models) - 1)
            )
            / (len(models) - 1)
            / (len(models) - 2)
        )

    data = data.pivot(index="code", columns="model")

    predictions = {
        key: {
            model: {code: data[key][model][code] for code in codes} for model in models
        }
        for key in data.columns.levels[0]
    }
    for party in parties:
        predictions[f"vote-share-{party}"] = predictions[party]
        del predictions[party]

    for model in predictions["winner"]:
        for code in predictions["winner"][model]:
            if predictions["winner"][model][code] == "?":
                for key in predictions:
                    if key == "winner":
                        continue
                    predictions[key][model][code] = "?"

    predictions["vote-share-winner"] = {model: {} for model in models}
    predictions["majority-winner"] = {model: {} for model in models}
    for model in models:
        for code in codes:
            winner = predictions["winner"][model][code]
            if winner == "tie":
                predictions["majority-winner"][model][code] = 0
                predictions["vote-share-winner"][model][code] = max(
                    predictions[f"vote-share-{p}"][model][code] for p in parties
                )
            elif winner == "?":
                predictions["majority-winner"][model][code] = "?"
                predictions["vote-share-winner"][model][code] = "?"
            else:
                predictions["majority-winner"][model][code] = predictions[
                    f"majority-{winner}"
                ][model][code]
                predictions["vote-share-winner"][model][code] = predictions[
                    f"vote-share-{winner}"
                ][model][code]

    summary_cols_1 = {
        model: Counter(f"{predictions['winner'][model][code]}" for code in codes)
        for model in models
    }

    summary_cols_2 = {
        model: Counter(
            f"{predictions['winner'][model][code]}-{predictions['margin'][model][code]}"
            for code in codes
        )
        for model in models
    }

    summary_rows_1 = [
        {
            "party": party,
            "predictions": {model: summary_cols_1[model][party] for model in models},
        }
        for party in ordered_parties
    ]

    summary_rows_2 = [
        {
            "party": party,
            "margin": margin,
            "predictions": {
                model: summary_cols_2[model][f"{party}-{margin}"] for model in models
            },
        }
        for party in ordered_parties
        for margin in ["comfortable", "close", "very-close"]
        if party in parties
    ]

    env = Environment(loader=FileSystemLoader("."))

    tpl = env.get_template("templates/index.html")
    ctx = {
        "models": models,
        "model_map": model_map,
        "parties": parties,
        "code_to_name": code_to_name,
        "codes": sorted(codes, key=lambda c: code_to_name[c]),
        "predictions": predictions,
        "corr_coeff": corr_coeff,
        "summary": summary_rows_1,
        "json_data": {
            "parties": json.dumps(parties),
            "models": json.dumps(models),
            "code_to_name": json.dumps(code_to_name),
            "predictions": json.dumps(predictions, cls=TruncateFloatEncoder),
            "corr_coeff": json.dumps(corr_coeff),
        },
    }
    with open("outputs/index.html", "w") as f:
        f.write(tpl.render(ctx))

    tpl = env.get_template("templates/breakdown.html")
    ctx = {
        "models": models,
        "model_map": model_map,
        "summary": summary_rows_2,
    }
    with open("outputs/breakdown/index.html", "w") as f:
        f.write(tpl.render(ctx))


    shutil.copyfile("templates/index.js", "outputs/index.js")

    tpl = env.get_template("templates/constituency.html")
    for code in codes:
        cols = [
            [
                {
                    "share": predictions[f"vote-share-{party}"][model][code],
                    "party": party,
                }
                for party in parties
            ]
            for model in models
        ]
        for col in cols:
            shares = [item["share"] for item in col]
            if len(set(shares)) == 1:
                assert set(shares) == {"?"}
                continue
            one, two = sorted(set(shares), reverse=True)[:2]
            for item in col:
                if item["share"] == one:
                    item["class"] = f"party-{item['party']}"
        rows = list(zip(*cols))
        rows = [r for r in rows if not set(i["share"] for i in r) <= {0, "?"}]
        rows.sort(key=lambda r: r[0]["share"], reverse=True)

        ctx = {
            "name": code_to_name[code],
            "demo_club_code": code_to_demo_club_code[code],
            "models": models,
            "model_map": model_map,
            "rows": rows,
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
