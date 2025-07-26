import requests

# 1) Configuration
BASE_URL      = "http://127.0.0.1:8000"   # your FastAPI server URL
USERNAME      = "abdulsami"               # as registered in your users db
PASSWORD      = "1234"
CLIENT_ID     = "ali"                     # from your OAuth2 settings
CLIENT_SECRET = "taha"

def get_access_token():
    """
    Exchange username/password for a JWT bearer token.
    """
    url = f"{BASE_URL}/token"
    payload = {
        "username":     USERNAME,
        "password":     PASSWORD,
        "grant_type":   "password",
        "scope":        "",       # leave blank unless your API uses scopes
        "client_id":    CLIENT_ID,
        "client_secret":CLIENT_SECRET
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    resp = requests.post(url, data=payload, headers=headers)
    resp.raise_for_status()  # throw exception on HTTP error
    data = resp.json()
    token = data.get("access_token")
    print("✔️ Obtained token:", token)
    return token

def call_protected_endpoint(token: str, endpoint: str):
    """
    Call a protected GET endpoint, passing the JWT as a Bearer token.
    """
    url = f"{BASE_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

if __name__ == "__main__":
    # Step 1: get our access token
    token = get_access_token()
    
    # Step 2: call a protected endpoint; e.g. "/volume"
    result = call_protected_endpoint(token, "/volume")
    print("🔍 /volume response:")
    print(result)
