"""Render meme.html to meme.png with headless Chromium (Playwright).

Local file only, no network. Run with the airdrop-agent venv python:
    ~/workspace/airdrop-agent/.venv/bin/python render.py
"""
import pathlib

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent


def main() -> None:
    url = (HERE / "meme.html").as_uri()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": 1280, "height": 1024},
            device_scale_factor=2,
        )
        page.goto(url)
        page.wait_for_timeout(300)
        page.screenshot(path=str(HERE / "meme.png"))
        browser.close()
    print("wrote", HERE / "meme.png")


if __name__ == "__main__":
    main()
