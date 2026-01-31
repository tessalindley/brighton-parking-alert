from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta
import re


# ---------- Date formatting ----------

def format_date(dt: datetime) -> str:
    """Return 'Saturday, January 31, 2026' (platform-safe)."""
    try:
        return dt.strftime("%A, %B %-d, %Y")
    except ValueError:
        return dt.strftime("%A, %B %d, %Y").replace(" 0", " ")

def build_date_regex(dates: list[datetime]) -> re.Pattern:
    """Build a regex that matches any formatted date in the list."""
    date_strings = [format_date(dt) for dt in dates]
    escaped_dates = [re.escape(ds) for ds in date_strings]
    return re.compile(rf"\b({'|'.join(escaped_dates)})\b")


# ---------- Target date selection ----------

def get_next_weekday(start: datetime, weekday: int) -> datetime:
    """
    weekday: Monday=0 ... Sunday=6
    Returns the next occurrence INCLUDING today if it matches.
    """
    days_ahead = (weekday - start.weekday()) % 7
    return start + timedelta(days=days_ahead)


def get_next_target_dates(
    holidays: list[datetime] | None = None,
    today: datetime | None = None,
    ) -> list[datetime]:
    """
    Returns datetimes for:
    - next Friday
    - next Saturday
    - next Sunday
    - upcoming holidays
    """
    today = today or datetime.today()
    today = today.replace(hour=0, minute=0, second=0, microsecond=0)
    
    targets = set()
    
    # Friday (4), Saturday (5), Sunday (6)
    for weekday in (4, 5, 6):
        targets.add(get_next_weekday(today, weekday))
    
    # Add holidays that are today or in the future
    if holidays:
        for h in holidays:
            h = h.replace(hour=0, minute=0, second=0, microsecond=0)
            if h >= today:
                targets.add(h)
    
    return sorted(targets)


# ---------- Color detection ----------

def is_green(rgb: str) -> bool:
    """
    Determine whether an rgb/rgba color is green-ish.
    Example: 'rgb(34, 197, 94)'
    """
    nums = [int(n) for n in re.findall(r"\d+", rgb)[:3]]
    r, g, b = nums
    return g > 150 and g > r and g > b


# ---------- Playwright logic ----------

def get_green_date_elements(page, date_regex: re.Pattern):
    """
    Find elements whose aria-label matches the date regex
    AND whose background color is green.
    """
    green_elements = []
    
    elements = page.locator("[aria-label]").all()
    
    for el in elements:
        aria_label = el.get_attribute("aria-label")
        if not aria_label or not date_regex.search(aria_label):
            continue
    
    background_color = el.evaluate(
    "el => window.getComputedStyle(el).backgroundColor"
    )
    
    if is_green(background_color):
        green_elements.append(el)
        print(f"Green date found: {aria_label} ({background_color})")

    return green_elements

def create_env_var(message):
    #Get the path to the GITHUB_OUTPUT file
    output_file = os.getenv('GITHUB_OUTPUT')

    if output_file:
        with open(output_file, "a") as f:
            f.write(f"my_output={message}\n")
    return


# ---------- Main ----------

def main():
    # Example holiday list (inject whatever source you want)
    holidays = [
        datetime(2026, 1, 1), # New Year's Day
        datetime(2026, 7, 4), # Independence Day
        datetime(2026, 12, 25), # Christmas
    ]
    
    target_dates = get_next_target_dates(holidays=holidays)
    
    print("Target dates:")
    for d in target_dates:
        print(" -", format_date(d))
    
    date_regex = build_date_regex(target_dates)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://example.com")
        
        green_dates = get_green_date_elements(page, date_regex)
        print(f"\nTotal green dates matched: {len(green_dates)}")
        browser.close()
        if (len(green_dates) > 0):
            output_text = "Brighton parking available"
            print(output_text)
            create_env_variable(output_text)
            exit(1)
        else:
            output_text = "No availability"
            print(output_text)
            create_env_var("none")
            exit(0)

if __name__ == "__main__":
    main()
