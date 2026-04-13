import requests
import base64
import os

TOKEN = os.getenv("GITHUB_TOKEN", "")
OWNER = "arthikandev"
REPO = "SportSkyline"

if not TOKEN:
    raise RuntimeError("Missing GITHUB_TOKEN environment variable.")

def push_file(path, content, message):
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}"
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Get SHA if exists
    resp = requests.get(url, headers=headers)
    sha = resp.json().get("sha") if resp.status_code == 200 else None
    
    data = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8")
    }
    if sha:
        data["sha"] = sha
    
    r = requests.put(url, headers=headers, json=data)
    print(f"[{r.status_code}] {path}")

# Updated Procfile - Render needs this to know how to run the app
procfile = "web: uvicorn app.main:app --host 0.0.0.0 --port $PORT\n"
push_file("backend/Procfile", procfile, "fix: Update Procfile for Render")

# render.yaml for better Render configuration
render_yaml = """services:
  - type: web
    name: SportSkyline
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: JWT_SECRET_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_ANON_KEY
        sync: false
      - key: ENVIRONMENT
        value: production
      - key: PYTHON_VERSION
        value: 3.11.0
"""
push_file("render.yaml", render_yaml, "fix: Add render.yaml with Python 3.11 pin")

print("Done!")
