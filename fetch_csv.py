import httpx
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

# Function to get the lag date (7 days ago)
def get_lag_date():
    return (datetime.utcnow() - timedelta(days=7)).strftime('%d-%b-%Y')

# Function to load cookies from a file
def load_cookies(cookie_file_path):
    if Path(cookie_file_path).exists():
        with open(cookie_file_path, 'r') as file:
            cookies = json.load(file)
        print(f"✅ Loaded cookies from {cookie_file_path}")
        return cookies
    else:
        print("⚠️ No cookies file found. Fresh cookies will be captured.")
        return {}

# Function to save cookies to a file
def save_cookies(cookies, cookie_file_path):
    with open(cookie_file_path, 'w') as file:
        json.dump(cookies, file, indent=4)
    print(f"✅ Saved cookies to {cookie_file_path}")

# Function to capture cookies by accessing the NSE homepage
def get_cookies(session: httpx.Client, cookie_file_path):
    url = "https://www.nseindia.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    # Make a request to capture cookies
    session.get(url, headers=headers)

    # Get cookies from the session and save to file for future use
    cookies = session.cookies.get_dict()
    save_cookies(cookies, cookie_file_path)

# Function to fetch the report file URL
def get_report_file_url(session: httpx.Client, lag_date: str):
    url = f"https://www.nseindia.com/api/reports?archives=%5B%7B%22name%22%3A%22CM%20-%20Margin%20Trading%20Disclosure%22%2C%22type%22%3A%22archives%22%2C%22category%22%3A%22capital-market%22%2C%22section%22%3A%22equities%22%7D%5D&date={lag_date}&type=equities&mode=single"
    
    # Retry logic
    for attempt in range(5):
        try:
            print(f"🔁 Attempt {attempt + 1} to fetch report for {lag_date}...")
            response = session.get(url)
            response.raise_for_status()

            if response.status_code == 200:
                if 'Content-Disposition' in response.headers and 'attachment' in response.headers['Content-Disposition']:
                    print("✅ CSV file located.")
                    return response
                else:
                    print("⚠️ Response received but no CSV headers found.")
            else:
                print(f"❌ Error: {response.status_code}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)

    raise Exception("❌ Failed to get report URL after multiple attempts.")

# Function to save the downloaded CSV file
def save_csv(response: httpx.Response, save_path: Path):
    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"✅ CSV saved at: {save_path}")

# Main function to fetch the report
def main():
    # Paths
    cookie_file_path = 'cookies.json'  # Path to store cookies
    lag_date = get_lag_date()  # Get lag date
    Path("data").mkdir(exist_ok=True)  # Ensure the 'data' directory exists
    file_name = f"mrg_trading_{lag_date}.csv"  # File name
    save_path = Path("data") / file_name  # Save path for the CSV

    # Headers for requests
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com"
    }

    # Start an HTTP client session
    with httpx.Client(http2=True, follow_redirects=True, timeout=10) as session:
        # Load cookies if they exist
        cookies = load_cookies(cookie_file_path)
        if cookies:
            session.cookies.update(cookies)  # Update session with saved cookies
            print("🌐 Using saved cookies...")

        # If no cookies or they have expired, get fresh cookies
        if not cookies:
            print("🌐 Capturing fresh cookies...")
            get_cookies(session, cookie_file_path)

        # Fetch the report
        print(f"📅 Fetching report for lag date: {lag_date}")
        response = get_report_file_url(session, lag_date)

        # Save the CSV file
        save_csv(response, save_path)

if __name__ == "__main__":
    main()
