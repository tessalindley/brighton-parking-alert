from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import os

URL = "https://reservenski.parkbrightonresort.com/select-parking"

def get_dates_to_check():
    today = datetime.today()
    dates = []

    # Find the next Friday
    days_until_friday = (4 - today.weekday()) % 7
    next_friday = today + timedelta(days=days_until_friday)
    #next_friday = next_friday + timedelta(days=38)
    dates.append(next_friday.strftime("%A, %B %d, %Y"))

    # Find the next Saturday
    days_until_saturday = (5 - today.weekday()) % 7
    next_saturday = today + timedelta(days=days_until_saturday)
    dates.append(next_saturday.strftime("%A, %B %d, %Y"))

    # Next Sunday
    next_sunday = next_saturday + timedelta(days=1)
    dates.append(next_sunday.strftime("%A, %B %d, %Y"))

    # Holidays to check if still in the future
    holidays = [datetime(2026, 1, 20), datetime(2026, 2, 17)]
    for h in holidays:
        if h >= today:
            dates.append(h.strftime("%A, %B %d, %Y"))

    print(dates)
    return dates

def check_parking():
    with sync_playwright() as p:
        print("here")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # wait for calendar to render
        page.wait_for_timeout(6000)

        available_dates = []

        for date_str in get_dates_to_check():
            try:
                button = page.locator(f"'{date_str}'")
                background_color = locator.evaluate("(element) => window.getComputedStyle(element).getPropertyValue('font-size')")
                print(background_color)
                if button and not button:
                    available_dates.append(date_str)
            except:
                continue

        browser.close()
        print(available_dates)
        return available_dates


def create_env_var(message):
    # Get the path to the GITHUB_OUTPUT file
    output_file = os.getenv('GITHUB_OUTPUT')
    
    # Write the output variable to the file in the format "variable_name=value"
    if output_file:
        with open(output_file, "a") as f:
            f.write(f"my_output={message}\n")
    return
    
# Main
available = check_parking()
if available:
    output_text = "Brighton parking available for these dates: " + available
    print(output_text)
    create_env_var(output_text)
    exit(1)  # triggers GitHub email
else:
    output_text = "No availability for the next weekend or holidays yet."
    print(output_text)
    create_env_var("none")
    exit(0)
