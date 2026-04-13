import requests
import base64
import os

TOKEN = os.getenv("GITHUB_TOKEN", "")
OWNER = "arthikandev"
REPO = "SportSkyline"

if not TOKEN:
    raise RuntimeError("Missing GITHUB_TOKEN environment variable.")

def push_file(local_path, git_path, message):
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{git_path}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    resp = requests.get(url, headers=headers)
    sha = resp.json().get("sha") if resp.status_code == 200 else None
    data = {"message": message, "content": content}
    if sha:
        data["sha"] = sha
    r = requests.put(url, headers=headers, json=data)
    print(f"[{r.status_code}] {git_path}: {'OK' if r.status_code in [200,201] else r.text[:200]}")

push_file(
    r"d:\System\SportSkyline\backend\app\main.py",
    "backend/app/main.py",
    "fix: Resilient startup + safe static file mounts for Render"
)
push_file(
    r"d:\System\SportSkyline\backend\app\config.py",
    "backend/app/config.py",
    "fix: Add production URL to CORS origins"
)
print("Done! Deploy will trigger automatically on Render.")
