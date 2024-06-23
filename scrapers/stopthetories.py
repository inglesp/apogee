from pathlib import Path

import httpx
from lxml import html


def scrape():
    rsp = httpx.get("https://stopthetories.vote/data")
    tree = html.fromstring(rsp.text)
    for a in tree.xpath("//a"):
        href = a.get("href")
        if not (href and href.startswith("/data/20240704")):
            continue
        timestamp = href.split("/")[-1].split(".")[0]
        if timestamp == "latest":
            continue
        dirpath = Path(f"data/raw/stopthetories/{timestamp}")
        if dirpath.exists():
            continue
        print(dirpath)
        dirpath.mkdir(parents=True, exist_ok=True)
        rsp = httpx.get(f"https://stopthetories.vote{href}")
        (dirpath / f"{timestamp}.csv").write_text(rsp.text)


if __name__ == "__main__":
    scrape()
