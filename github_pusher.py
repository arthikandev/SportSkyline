import os
import base64
import httpx
import json
import time

# --- Configuration ---
TOKEN = os.getenv("GITHUB_TOKEN", "")
OWNER = "arthikandev"
REPO = "SportSkyline"
BRANCH = "main"

if not TOKEN:
    raise RuntimeError("Missing GITHUB_TOKEN environment variable.")

# Only include relevant folders/files
DIRS_TO_UPLOAD = [".", "backend"]
EXCLUDE_DIRS = [".venv", "__pycache__", ".git", ".pytest_cache", ".gemini", "node_modules", ".agents"]
EXCLUDE_FILES = ["github_pusher.py", "uploader.py", ".env"] # Security: don't push .env to public repo

GITHUB_API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/"

def get_all_files(root_dir):
    file_list = []
    for root, dirs, files in os.walk(root_dir):
        # Filter excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        
        for file in files:
            if file in EXCLUDE_FILES or file.startswith('.'):
                continue
            
            full_path = os.path.join(root, file)
            # Create relative path for GitHub
            rel_path = os.path.relpath(full_path, root_dir).replace("\\", "/")
            file_list.append((full_path, rel_path))
    return file_list

async def upload_file(client, local_path, git_path):
    print(f"Uploading {git_path}...")
    
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
        
    url = GITHUB_API_URL + git_path
    
    # Check if file exists to get SHA (for updates)
    resp = await client.get(url)
    sha = None
    if resp.status_code == 200:
        sha = resp.json().get("sha")
        
    data = {
        "message": f"Upload {git_path} via API",
        "content": content,
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha
        
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    response = await client.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print(f"SUCCESS: {git_path}")
    else:
        print(f"FAILED: {git_path} - {response.status_code} - {response.text}")

async def main():
    files = get_all_files(".")
    print(f"Found {len(files)} files to upload.")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for local_path, git_path in files:
            await upload_file(client, local_path, git_path)
            time.sleep(0.5) # Avoid rate limits

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
