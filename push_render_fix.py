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
    resp = requests.get(url, headers=headers)
    sha = resp.json().get("sha") if resp.status_code == 200 else None
    data = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("utf-8")
    }
    if sha:
        data["sha"] = sha
    r = requests.put(url, headers=headers, json=data)
    print(f"[{r.status_code}] {path}: {'OK' if r.status_code in [200,201] else r.text[:100]}")

# 1. Pin Python version for Render (runtime.txt in backend dir)
push_file("backend/runtime.txt", "python-3.11.0\n", "fix: Pin Python 3.11 for Render compatibility")

# 2. render.yaml at root - tells Render exactly how to deploy
render_yaml = """services:
  - type: web
    name: SportSkyline
    runtime: python
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: ENVIRONMENT
        value: production
      - key: PYTHON_VERSION
        value: 3.11.0
"""
push_file("render.yaml", render_yaml, "fix: Add render.yaml config")

# 3. requirements.txt - ensure bcrypt is at 4.0.1 to avoid py3.14 issues on render's py3.11
requirements = """# SportSkyline Backend Requirements

# --- Core Framework ---
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
python-multipart>=0.0.9

# --- Database ---
sqlalchemy[asyncio]>=2.0.30
asyncpg>=0.29.0
alembic>=1.13.1

# --- Pydantic (v2) ---
pydantic>=2.7.1
pydantic-settings>=2.2.1
email-validator>=2.1.1

# --- Auth ---
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
bcrypt==4.0.1

# --- Utils ---
slowapi>=0.1.9
apscheduler>=3.10.4
httpx>=0.27.0
python-slugify>=8.0.4
python-dotenv>=1.0.1
orjson>=3.10.3
loguru>=0.7.2
"""
push_file("backend/requirements.txt", requirements, "fix: Pin bcrypt==4.0.1 for Render Python 3.11 compatibility")

print("All fixes pushed!")
