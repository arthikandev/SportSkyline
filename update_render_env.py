"""
Update Render environment variable via Render API.
Uses your service ID to patch DATABASE_URL directly.
"""
import requests

# Render service ID from the dashboard URL
SERVICE_ID = "srv-d7ec7ld7vvec73f5is30"

# We need the Render API key - let's try to get it
# First, try to use the Render API to list env vars (requires API key)
# Get API key from: https://dashboard.render.com/u/settings#apikeys

# Read new DATABASE_URL from environment to avoid hardcoding credentials
NEW_DB_URL = os.environ.get("NEW_DATABASE_URL", "")

print("To update DATABASE_URL via Render API, I need your Render API Key.")
print()
print("Finding it from dashboard...")
print()
print("You can get it from: https://dashboard.render.com/u/settings#apikeys")
print("It looks like: rnd_xxxxxxxxxxxxxxxx")
print()
print("Once you have it, set RENDER_API_KEY environment variable and re-run.")

api_key = os.environ.get("RENDER_API_KEY")
if api_key:
    print(f"Found API key: {api_key[:10]}...")
    # Update env var
    url = f"https://api.render.com/v1/services/{SERVICE_ID}/env-vars"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    # Put env vars - this replaces all env vars, so we need to be careful
    # First GET current env vars
    resp = requests.get(url, headers=headers)
    print(f"GET status: {resp.status_code}")
    if resp.status_code == 200:
        env_vars = resp.json()
        print(f"Current env vars: {[e['envVar']['key'] for e in env_vars]}")
        if not NEW_DB_URL:
            print("Set NEW_DATABASE_URL in your environment to update DATABASE_URL safely.")
else:
    print()
    print("No API key found. Please enter it when prompted.")
