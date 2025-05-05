import httpx
import time
from datetime import datetime, timedelta
from pathlib import Path

def get_lag_date():
    return (datetime.utcnow() - timedelta(days=7)).strftime('%d-%b-%Y')

def get_report_file_url(session: httpx.Client, lag_date: str):
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
            response = session.get(url, headers=headers, params=params)
            response.raise_for_status()

            if 'Content-Disposition' in response.headers:
                print("✅ CSV file located.")
                return response
            else:
                print("⚠️ Response received but no CSV headers found.")
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(2)

    raise Exception("❌ Failed to get report URL after multiple attempts.")

def save_csv(response: httpx.Response, save_path: Path):
    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"✅ CSV saved at: {save_path}")

def get_cookies(session: httpx.Client):
    # Send a request to the homepage to capture necessary cookies
    url = "https://www.nseindia.com"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    }

    # Perform a GET request to capture cookies
    session.get(url, headers=headers)
    
    # At this point, session.cookies contains the cookies set by the website
    # You can inspect them if needed (optional)
    print("Cookies captured:", session.cookies)

def main():
    lag_date = get_lag_date()
    Path("data").mkdir(exist_ok=True)
    file_name = f"mrg_trading_{lag_date}.csv"
    save_path = Path("data") / file_name

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com"
    }

    with httpx.Client(http2=True, follow_redirects=True, timeout=10) as session:
        print("🌐 Priming session with NSE...")
        # Capture cookies by sending an initial request to the homepage
        get_cookies(session)
        
        session.headers.update(headers)
        
        # Now that we have the session with cookies, fetch the report
        print(f"📅 Fetching report for lag date: {lag_date}")
        response = get_report_file_url(session, lag_date)
        save_csv(response, save_path)

if __name__ == "__main__":
    main()
