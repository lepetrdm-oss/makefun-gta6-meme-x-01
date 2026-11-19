"""Render ghost.svg to ghost.png with a transparent background (Playwright).

    ~/workspace/airdrop-agent/.venv/bin/python render-ghost.py
"""
import pathlib

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent


def main() -> None:
    url = (HERE / "ghost.svg").as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 690, "height": 690})
        page.goto(url)
        page.wait_for_timeout(200)
        page.screenshot(path=str(HERE / "ghost.png"), omit_background=True)
        browser.close()
    print("wrote", HERE / "ghost.png")


if __name__ == "__main__":
    main()
