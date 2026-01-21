from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

URL = "https://reservenski.parkbrightonresort.com/select-parking"

def get_dates_to_check():
    today = datetime.today()
    dates = []

    # Find the next Saturday
    days_until_saturday = (5 - today.weekday()) % 7
    next_saturday = today + timedelta(days=days_until_saturday)
    dates.append(next_saturday.strftime("%Y-%m-%d"))

    # Next Sunday
    next_sunday = next_saturday + timedelta(days=1)
    dates.append(next_sunday.strftime("%Y-%m-%d"))

    # Holidays to check if still in the future
    holidays = [datetime(2026, 1, 20), datetime(2026, 2, 17)]
    for h in holidays:
        if h >= today:
            dates.append(h.strftime("%Y-%m-%d"))

    return dates

def check_parking():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # wait for calendar to render
        page.wait_for_timeout(6000)

        available_dates = []

        for date_str in get_dates_to_check():
            try:
                button = page.query_selector(f"[data-date='{date_str}']")
                if button and not button.is_disabled():
                    available_dates.append(date_str)
            except:
                continue

        browser.close()
        return available_dates

# Main
available = check_parking()
if available:
    print("Brighton parking available for these dates:", available)
    exit(1)  # triggers GitHub email
else:
    print("No availability for the next weekend or holidays yet.")
    exit(0)
