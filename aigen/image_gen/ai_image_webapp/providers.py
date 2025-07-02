
# 📁 providers.py


import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file (or api.env if you prefer)
load_dotenv()  # You can use load_dotenv("api.env") if your file is named api.env

# Provider configuration: add more providers as needed
def get_providers():
    """
    Returns a list of provider configs in failover order.
    Each config is a dict with keys: name, url, headers, json_key, and env_keys.
    """
    return [
        {
            "name": "cloudflare",
            "url": f"https://api.cloudflare.com/client/v4/accounts/{os.getenv('CF_ACCOUNT')}/ai/run/@cf/runwayml/stable-diffusion-v1-5",
            "headers": {
                "Authorization": f"Bearer {os.getenv('CF_TOKEN')}",
                "Content-Type": "application/json"
            },
            "json_key": "prompt",
            "env_keys": ["CF_ACCOUNT", "CF_TOKEN"],
        },
        {
            "name": "deepai",
            "url": "https://api.deepai.org/api/text2img",
            "headers": {"api-key": os.getenv('DEEPAI_KEY')},
            "json_key": "text",
            "env_keys": ["DEEPAI_KEY"],
        },
        {
            "name": "huggingface",
            "url": "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            "headers": {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"},
            "json_key": "inputs",
            "env_keys": ["HF_TOKEN"],
        },
    ]

def is_provider_ready(provider):
    """
    Checks if all required environment variables for a provider are set and non-empty.
    """
    for key in provider["env_keys"]:
        if not os.getenv(key):
            return False
    return True

def try_provider(prompt: str):
    """
    Tries each provider in order. Returns (image_bytes, provider_name) on success.
    Raises RuntimeError with a friendly message if all fail.
    """
    last_err = None
    for provider in get_providers():
        name = provider["name"]
        if not is_provider_ready(provider):
            continue  # Skip if required env vars are missing
        payload = {provider["json_key"]: prompt}
        try:
            r = requests.post(provider["url"], headers=provider["headers"], json=payload, timeout=60)
        except Exception as e:
            last_err = f"{name}: Exception {str(e)}"
            continue
        # Check for HTTP errors that mean quota/unauthorized/limit
        if r.status_code in (401, 403, 429):
            last_err = f"{name}: API quota/authorization error ({r.status_code}). Trying next provider."
            continue
        if r.ok and r.headers.get("content-type", "").startswith(("image/", "application/octet")):
            # Log which provider was used (could also use logging module)
            print(f"[INFO] Image generated via {name}")
            return r.content, name
        # Other errors
        last_err = f"{name}: {r.status_code} {r.text[:120]}"
    raise RuntimeError(last_err or "All APIs exhausted. Try again later.")

