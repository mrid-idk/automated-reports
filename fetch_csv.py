import httpx
import zipfile
import json
import time
import os
from io import BytesIO
from pathlib import Path
from datetime import datetime, timedelta

# Function to get the lag date (7 days ago)
def get_lag_date():
    return (datetime.utcnow() - timedelta(days=7)).strftime('%d-%b-%Y')

# Function to get cookies and save them to a file
def get_cookies(session: httpx.Client, cookie_file_path: str):
    cookies = session.cookies  # Get cookies from the session
    cookies_dict = {cookie.key: cookie.value for cookie in cookies}  # Convert to dictionary

    with open(cookie_file_path, 'w') as f:
        json.dump(cookies_dict, f)
    print("✅ Cookies saved successfully.")

# Function to load cookies from the file and add them to the session
def load_cookies(session: httpx.Client, cookie_file_path: str):
    try:
        with open(cookie_file_path, 'r') as f:
            cookies_dict = json.load(f)
        for key, value in cookies_dict.items():
            session.cookies.set(key, value)
        print("✅ Cookies loaded successfully.")
    except FileNotFoundError:
        print("⚠️ No cookies file found. Fresh cookies will be captured.")

# Function to get the URL for the report zip file for a given date
def get_report_zip_url(session: httpx.Client, lag_date: str):
    url = "https://www.nseindia.com/api/reports"
    params = {
        "archives": '[{"name":"CM - Margin Trading Disclosure","type":"archives","category":"capital-market","section":"equities"}]',
        "date": lag_date,
        "type": "equities",
        "mode": "single"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/all-reports",
        "X-Requested-With": "XMLHttpRequest"
    }

    for attempt in range(5):
        try:
            print(f"🔁 Attempt {attempt + 1} to fetch report for {lag_date}...")
            response = session.get(url, headers=headers, params=params, timeout=30)  # Increased timeout
            response.raise_for_status()

            # Check if the response contains a valid zip file
            if 'Content-Disposition' in response.headers and 'zip' in response.headers['Content-Type']:
                print("✅ Zip file located.")
                return response
            else:
                print("⚠️ Response received but no zip headers found.")
        except httpx.RequestError as e:
            print(f"❌ Error: Request failed ({e})")
        except httpx.TimeoutException as e:
            print(f"❌ Error: Timeout occurred ({e})")
        except Exception as e:
            print(f"❌ Error: {e}")

        # Retry with a delay if error occurs
        print("⏳ Retrying in 5 seconds...")
        time.sleep(5)

    raise Exception("❌ Failed to get report URL after multiple attempts.")

# Function to download, unzip and save the CSV file
def download_and_extract_zip(response: httpx.Response, save_dir: Path):
    with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
        zip_file.extractall(save_dir)
        print("✅ Zip file extracted.")

        # Assuming there is only one CSV file in the zip, we find it
        for file_name in zip_file.namelist():
            if file_name.endswith('.csv'):
                csv_file_path = save_dir / file_name
                print(f"✅ CSV file found: {csv_file_path}")
                return csv_file_path

    raise Exception("❌ No CSV file found in the zip archive.")

# Main function to control the flow
def main():
    lag_date = get_lag_date()
    cookie_file_path = "cookies.json"
    save_dir = Path("data")
    save_dir.mkdir(exist_ok=True)

    # Set up session and load cookies
    with httpx.Client(follow_redirects=True, timeout=30) as session:  # Increased timeout
        print("🌐 Priming session with NSE...")
        load_cookies(session, cookie_file_path)  # Try loading saved cookies
        session.get("https://www.nseindia.com")  # Ensure cookies are active
        time.sleep(1)  # Let cookies settle

        if not Path(cookie_file_path).exists():
            print("⚠️ No cookies file found. Capturing fresh cookies...")
            get_cookies(session, cookie_file_path)  # Capture fresh cookies

        print(f"📅 Fetching report for lag date: {lag_date}")
        response = get_report_zip_url(session, lag_date)
        csv_file_path = download_and_extract_zip(response, save_dir)

        print(f"✅ CSV saved at: {csv_file_path}")

if __name__ == "__main__":
    main()
