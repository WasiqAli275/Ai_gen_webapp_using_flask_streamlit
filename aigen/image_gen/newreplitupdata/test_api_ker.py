import requests

API_KEY = "1JUV860DC7YJRVYM"  # Tumhari key
url = "https://www.alphavantage.co/query"

params = {
    "function": "TIME_SERIES_INTRADAY",
    "symbol": "AAPL",          # Apple stock example
    "interval": "1min",        # 1-minute interval
    "apikey": API_KEY
}

response = requests.get(url, params=params)
data = response.json()

# Check response
if "Time Series (1min)" in data:
    print("✅ API Key is working!")
elif "Note" in data:
    print("⚠️ API key is valid but request limit exceeded (wait a bit).")
elif "Error Message" in data:
    print("❌ Invalid API key or incorrect parameters.")
else:
    print("❓ Unexpected response:", data)
