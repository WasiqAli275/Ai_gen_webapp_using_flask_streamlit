import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"
USERNAME = "abdulsami"
PASSWORD = "1234"
CLIENT_ID = "ali"
CLIENT_SECRET = "taha"

def get_access_token():
    url = f"{BASE_URL}/token"
    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "grant_type": "password",
        "scope": "",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()
    token = response.json()["access_token"]
    print("✔️ Access token mil gaya:", token)
    return token

def fetch_psx_data(token):
    headers = {"Authorization": f"Bearer {token}"}
    data = {}
    endpoints = {
        "Total Volume": "/volume",
        "Status": "/status",
        "Total Trades": "/tradesinstockmarket",
        # "Total Companies": "/totalcompanies",   # temporarily skip
        "Companies in Profit": "/companiesinprofit",
        "Companies in Loss": "/companiesinloss"
    }

    for key, endpoint in endpoints.items():
        url = f"{BASE_URL}{endpoint}"
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            data[key] = list(result.values())[0]
        except Exception as e:
            print(f"❌ Error calling {endpoint}: {e}")
            data[key] = None  # so CSV still gets column

    return data

def save_to_csv(data, filename="psx_today_data.csv"):
    df = pd.DataFrame([data])
    df.to_csv(filename, index=False)
    print(f"📦 Data CSV file mai save ho gaya: {filename}")

if __name__ == "__main__":
    token = get_access_token()
    psx_data = fetch_psx_data(token)
    print("🔍 Scraped PSX data:")
    print(psx_data)
    save_to_csv(psx_data)
