import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, timedelta
import pandas as pd

def get_lag_date():
    return (datetime.utcnow() - timedelta(days=7)).strftime('%d-%b-%Y')

def main():
    # Load credentials from environment variable
    creds_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not creds_json:
        raise Exception("Google credentials JSON not found in environment.")

    creds_dict = json.loads(creds_json)
    creds_file = "google_creds.json"
    with open(creds_file, "w") as f:
        json.dump(creds_dict, f)

    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1CYPLuS86Gqch8tutw_WcKVuV-gxaJpzW4zd5T6qKH9c/edit#gid=0")
    worksheet = sheet.get_worksheet(0)

    lag_date = get_lag_date()
    file_path = f"data/mrg_trading_{lag_date}.csv"
    df = pd.read_csv(file_path)

    worksheet.clear()
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

    print(f"✅ Uploaded CSV to Google Sheets for {lag_date}")

if __name__ == "__main__":
    main()
