import requests
import os
import time
from zipfile import ZipFile
from io import BytesIO

# Define the headers and session to ensure cookies work properly
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

def fetch_cookies(session, url="https://www.nseindia.com"):
    """
    Fetch the cookies by sending a request to the specified URL.
    """
    session.get(url, headers=HEADERS)
    return session.cookies

def download_csv(session, date, cookie_jar):
    """
    Download the CSV file for the specified date from the NSE API.
    Handles cookie-based sessions and saves the file.
    """
    # Correct URL format with required query parameters
    api_url = f"https://www.nseindia.com/api/reports?archives=%5B%7B%22name%22%3A%22CM%20-%20Margin%20Trading%20Disclosure%22%2C%22type%22%3A%22archives%22%2C%22category%22%3A%22capital-market%22%2C%22section%22%3A%22equities%22%7D%5D&date={date}&type=equities&mode=single"
    
    cookies = cookie_jar.get_dict()  # Convert cookies to dictionary
    response = session.get(api_url, cookies=cookies, headers=HEADERS, timeout=60)

    if response.status_code == 200:
        # If the response is a zip file, we will handle it here
        with ZipFile(BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(f"data/{date}")
            print(f"CSV file for {date} extracted successfully.")
    else:
        print(f"Error: {response.status_code}, Failed to download for {date}")

def main():
    session = requests.Session()
    cookies = fetch_cookies(session)

    # For demo, we fetch the report for April 30, 2025
    date_to_fetch = "30-Apr-2025"
    
    try:
        print(f"Starting download for {date_to_fetch}...")
        download_csv(session, date_to_fetch, cookies)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
