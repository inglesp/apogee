# I'm not very proud of the code in build.py.  Given the importance of
# transparency aroudn evaluating the different forecasts, I've tried to make
# the code that generates the leaderboards as easy to follow as possible.

from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader


models = {
    "britainpredicts": "Britain Predicts (New Statesman)",
    "economist": "The Economist",
    "electionmaps": "electionmaps",
    "electoralcalculus": "Electoral Calculus STM",
    "electoralcalculusmrp": "Electoral Calculus MRP",
    "focaldata": "Focaldata",
    "ft": "The FT",
    "ipsos": "Ipsos",
    "jlp": "JLP",
    "moreincommon": "More in Common",
    "savanta": "Savanta",
    "survation": "Survation",
    "wethink": "WeThink",
    "yougov": "YouGov",
    "samfr": "Sam Freedman",
    "exitpoll": "Exit Poll",
    "manifold": "Manifold",
}

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


def analyse():
    df = pd.concat(load_model_data(model) for model in ["2024"] + list(models))
    env = Environment(loader=FileSystemLoader("."))
    tpl = env.get_template("templates/leaderboard.html")
    ctx = {
        "by_seat_totals": make_table(
            score_by_seat_totals,
            df,
            low_good=True,
        ),
        "by_correct_seat_calls": make_table(
            score_by_correct_seat_calls,
            df,
            low_good=False,
        ),
        "by_vote_share_error": make_table(
            score_by_vote_share_error,
            df,
            low_good=True,
        ),
    }
    with open("outputs/leaderboard/index.html", "w") as f:
        f.write(tpl.render(ctx))


def load_model_data(model):
    path = sorted(Path(f"data/processed/{model}").glob("*/data.csv"))[-1]

    if model == "samfr":
        # Sam's only predicted a winner for each seat
        df = pd.read_csv(path)
        df["winner"] = df["party"]
        df["model"] = model
        return df[["code", "model", "winner"]]

    # All other forecasts have a numerical value attached to each party for
    # each seat; in most cases this is the predicted (or actual) vote share,
    # but for exitpoll and manifold, this is a probability.  In either case,
    # we're interested in the party with the highest value in each seat.
    df = pd.read_csv(path)[["code", *parties]]
    df["model"] = model
    winner = df[parties].idxmax(axis=1)
    winner[df[parties].eq(df[parties].max(axis=1), axis=0).sum(axis=1) > 1] = "tie"
    winner[df[parties].sum(axis=1) == 0] = "?"
    df["winner"] = winner
    return df


def make_table(fn, df, low_good):
    scores = fn(df)
    sorted_scores = sorted(scores.items(), key=lambda kv: kv[1], reverse=not low_good)
    return [
        {
            "model": m,
            "title": models[m],
            "score": s,
        }
        for m, s in sorted_scores
    ]


def score_by_seat_totals(df):
    seat_totals = (
        df.groupby("model")
        .value_counts(["winner"])
        .unstack()[parties]
        .fillna(0)
        .astype(int)
    )

    return {
        model: calculate_rmse(seat_totals.loc["2024"], seat_totals.loc[model])
        for model in models
    }


def score_by_correct_seat_calls(df):
    df = df[["code", "model", "winner"]].pivot(index="code", columns="model")
    df.columns = df.columns.droplevel(0)

    return {
        model: (df["2024"] == df[model]).value_counts()[True]
        for model in models
    }


def score_by_vote_share_error(df):
    scores = {}
    for model in models:
        if model in ["exitpoll", "manifold", "samfr"]:
            # We don't have vote share predictions for these forecasts
            continue
        s1 = df[df["model"] == model][parties].stack()
        # Limitations in my data model mean that, in seats where an "oth"
        # candidate came first or second, we don't capture the results of "oth"
        # candidates apart from the top one.  See comment in scrape_bbc.py.
        df2 = df[df["model"] == "2024"][parties]
        df2["oth"] = 100 - df2.sum() + df2["oth"]
        s2 = df2.stack()
        scores[model] = calculate_rmse(s1, s2)

    return scores


def calculate_rmse(s1, s2):
    return (((s1 - s2) ** 2).mean()) ** 0.5


if __name__ == "__main__":
    analyse()
