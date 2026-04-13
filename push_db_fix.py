"""
Push Render deployment fixes to GitHub.
Fixes:
1. database.py  – statement_cache_size=0 (required for Supabase pooler)
2. render.yaml  – correct pooler DATABASE_URL (IPv4-compatible for Render free tier)
3. requirements.txt – pinned bcrypt==4.0.1, removed test deps
"""
import requests
import base64
import os

TOKEN = os.getenv("GITHUB_TOKEN", "")
OWNER = "arthikandev"
REPO = "SportSkyline"
BRANCH = "main"

if not TOKEN:
    raise RuntimeError("Missing GITHUB_TOKEN environment variable.")

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def push_file(local_path, git_path, commit_msg):
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{git_path}"
    resp = requests.get(url, headers=HEADERS)
    sha = resp.json().get("sha") if resp.status_code == 200 else None

    data = {"message": commit_msg, "content": content, "branch": BRANCH}
    if sha:
        data["sha"] = sha

    r = requests.put(url, headers=HEADERS, json=data)
    status = "OK" if r.status_code in [200, 201] else f"FAILED: {r.text[:300]}"
    print(f"[{r.status_code}] {git_path}: {status}")
    return r.status_code in [200, 201]

files = [
    (
        r"d:\System\SportSkyline\backend\app\database.py",
        "backend/app/database.py",
        "fix: Add statement_cache_size=0 for Supabase pooler (fixes Render startup crash)"
    ),
    (
        r"d:\System\SportSkyline\render.yaml",
        "render.yaml",
        "fix: Use Supabase IPv4 pooler DATABASE_URL + full env vars for Render"
    ),
    (
        r"d:\System\SportSkyline\backend\requirements.txt",
        "backend/requirements.txt",
        "fix: Pin bcrypt==4.0.1, remove test deps for Render Python 3.11"
    ),
]

print("Pushing Render deployment fixes to GitHub...\n")
success = 0
for local, git, msg in files:
    if push_file(local, git, msg):
        success += 1

print(f"\n{'='*50}")
print(f"Done! {success}/{len(files)} files pushed.")
if success == len(files):
    print("Render will auto-redeploy. Check: https://dashboard.render.com")
else:
    print("Some files failed. Check errors above.")
