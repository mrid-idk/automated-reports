import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

def get_lag_date():
    return (datetime.utcnow() - timedelta(days=7)).strftime('%d-%b-%Y')

def get_session_with_cookie():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.nseindia.com/"
    })
    session.get("https://www.nseindia.com")
    return session

def download_csv(session, lag_date, save_path):
    url = "https://www.nseindia.com/api/reports"
    params = {
        "archives": '[{\"name\":\"CM - Margin Trading Disclosure\",\"type\":\"archives\",\"category\":\"capital-market\",\"section\":\"equities\"}]',
        "date": lag_date,
        "type": "equities",
        "mode": "single"
    }
    response = session.get(url, params=params)
    if response.ok and 'text/csv' in response.headers.get('Content-Type', ''):
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"✅ Downloaded CSV for {lag_date}")
    else:
        raise Exception(f"❌ Failed to download file. Status: {response.status_code}, Headers: {response.headers}")

def main():
    lag_date = get_lag_date()
    Path("data").mkdir(exist_ok=True)
    file_name = f"mrg_trading_{lag_date}.csv"
    save_path = Path("data") / file_name

    session = get_session_with_cookie()
    download_csv(session, lag_date, save_path)

if __name__ == "__main__":
    main()
