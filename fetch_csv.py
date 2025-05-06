import requests
from zipfile import ZipFile
from io import BytesIO

def fetch_cookies(session):
    """ Fetch cookies by making a simple request to the NSE homepage. """
    session.get('https://www.nseindia.com')
    return session.cookies

def download_and_extract(date, session, cookies):
    """ Download the CSV zip file for the given date and extract it. """
    url = f"https://www.nseindia.com/api/reports?archives=%5B%7B%22name%22%3A%22CM%20-%20Margin%20Trading%20Disclosure%22%2C%22type%22%3A%22archives%22%2C%22category%22%3A%22capital-market%22%2C%22section%22%3A%22equities%22%7D%5D&date={date}&type=equities&mode=single"
    
    response = session.get(url, cookies=cookies, headers={'User-Agent': 'Mozilla/5.0'})
    
    if response.status_code == 200:
        with ZipFile(BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(f"data/{date}")
            print(f"CSV extracted successfully for {date}.")
    else:
        print(f"Failed to download for {date}, status code: {response.status_code}")

def main():
    session = requests.Session()
    cookies = fetch_cookies(session)

    # Specify the date you want to download
    date = '30-Apr-2025'
    
    download_and_extract(date, session, cookies)

if __name__ == "__main__":
    main()
