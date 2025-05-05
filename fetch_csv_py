import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

def get_lag_date():
    return (datetime.utcnow() - timedelta(days=7)).strftime('%d-%b-%Y')  # example: "30-Apr-2025"

def get_session_with_cookie():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://www.nseindia.com/"
    })
    session.get("https://www.nseindia.com", timeout=10)
    return session

def get_report_file_url(session, lag_date):
    url = "https://www.nseindia.com/api/reports"
    params = {
        "archives": '[{"name":"CM - Margin Trading Disclosure","type":"archives","category":"capital-market","section":"equities"}]',
        "date": lag_date,
        "type": "equities",
        "mode": "single"
    }

    response = session.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    if "data" in data and len(data["data"]) > 0 and "reportUrl" in data["data"][0]:
        report_url = data["data"][0]["reportUrl"]
        print(f"✅ Found report URL: {report_url}")
        return report_url
    else:
        raise Exception(f"❌ No report URL found in response for date {lag_date}")

def download_csv(report_url, save_path, session):
    base = "https://www.nseindia.com"
    full_url = base + report_url
    response = session.get(full_url, timeout=15)
    response.raise_for_status()

    with open(save_path, 'wb') as f:
        f.write(response.content)
    print(f"✅ Downloaded and saved CSV to {save_path}")

def main():
    lag_date = get_lag_date()
    Path("data").mkdir(exist_ok=True)
    file_name = f"mrg_trading_{lag_date}.csv"
    save_path = Path("data") / file_name

    session = get_session_with_cookie()
    report_url = get_report_file_url(session, lag_date)
    download_csv(report_url, save_path, session)

if __name__ == "__main__":
    main()

