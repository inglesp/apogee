from datetime import date, datetime
from pathlib import Path

from playwright.sync_api import sync_playwright


def scrape():
    dirpath = Path(f"data/raw/ft/{date.today()}")
    dirpath.mkdir(parents=True, exist_ok=True)

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=False)
    p = browser.new_page()
    p.goto("https://ig.ft.com/uk-general-election/2024/projection/")

    # TODO: autoclick on cookie button

    tbody = p.locator(".TBody-sc-1449bsn-4")
    for tr in tbody.locator("tr").all()[:-1]:
        constituency_id = tr.get_attribute("id").split("_")[1]
        constituency_name = tr.locator("td").all()[0].text_content()
        path = dirpath / f"{constituency_id}.html"
        if path.exists():
            continue
        print(datetime.now(), constituency_id, constituency_name)
        tr.click()
        container = p.locator(".InnerContainer-sc-gc38w6-0")
        path.write_text(container.inner_html())

    # Playwright can't click on the last row, so we get that manually
    tr = tbody.locator("tr").all()[-1]
    constituency_id = tr.get_attribute("id").split("_")[1]
    constituency_name = tr.locator("td").all()[0].text_content()
    path = dirpath / f"{constituency_id}.html"
    if not path.exists():
        p.goto(
            f"https://ig.ft.com/uk-general-election/2024/projection/?constituency={constituency_id}"
        )
        print(datetime.now(), constituency_id, constituency_name)
        container = p.locator(".InnerContainer-sc-gc38w6-0")
        path.write_text(container.inner_html())


if __name__ == "__main__":
    scrape()
