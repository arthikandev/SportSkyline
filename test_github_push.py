import requests
import base64
import json

TOKEN = "github_pat_11B5NYYWA01YIgwnJ6OW5j_kih7hKGcpxHaUjKK9ejY1ZVJ00Rq4HjI7iTtRgGFy8IM4265LIVufS7i"
OWNER = "arthikandev"
REPO = "SportSkyline"
PATH = "README.md"
CONTENT = "SportSkyline - Live Scores & News"

print(f"Testing push for {PATH}...")

url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{PATH}"
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

encoded_content = base64.b64encode(CONTENT.encode("utf-8")).decode("utf-8")

data = {
    "message": "Initial commit via API",
    "content": encoded_content
}

print(f"Sending PUT request to {url}...")
try:
    response = requests.put(url, headers=headers, json=data, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
