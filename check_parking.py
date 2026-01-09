from playwright.sync_api import sync_playwright

URL = "https://reservenski.parkbrightonresort.com/select-parking"

def weekend_available(page_text: str) -> bool:
    text = page_text.lower()

    # If Saturday or Sunday appears and the page is not fully sold out,
    # assume weekend availability exists
    if ("saturday" in text or "sunday" in text) and "sold out" not in text:
        return True

    return False


def check_parking():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # wait for JS content to load
        page.wait_for_timeout(6000)

        page_text = page.inner_text("body")
        browser.close()

        return weekend_available(page_text)


if check_parking():
    print("🚨 Brighton WEEKEND parking availability detected!")
    exit(1)   # fail job → GitHub sends email
else:
    print("No weekend availability yet.")
    exit(0)
