import os
import base64
import requests
import time

# --- Configuration ---
TOKEN = os.getenv("GITHUB_TOKEN", "")
OWNER = "arthikandev"
REPO = "SportSkyline"
BRANCH = "main"

if not TOKEN:
    raise RuntimeError("Missing GITHUB_TOKEN environment variable.")

EXCLUDE_DIRS = [".venv", "__pycache__", ".git", ".pytest_cache", ".gemini", "node_modules", ".agents"]
EXCLUDE_FILES = ["github_pusher.py", "github_pusher_v2.py", "debug_files.py", "uploader.py", ".env"]

GITHUB_API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/"

def get_all_files(root_dir):
    file_list = []
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
        for file in files:
            if file in EXCLUDE_FILES or file.startswith('.'):
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, root_dir).replace("\\", "/")
            file_list.append((full_path, rel_path))
    return file_list

def upload_file(local_path, git_path):
    print(f"Preparing {git_path}...")
    
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")
        
    url = GITHUB_API_URL + git_path
    headers = {
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Get file info to handle updates
    resp = requests.get(url, headers=headers)
    sha = None
    if resp.status_code == 200:
        sha = resp.json().get("sha")
    
    data = {
        "message": f"Upload {git_path} via SportSkyline Pusher",
        "content": content,
        "branch": BRANCH
    }
    if sha:
        data["sha"] = sha
        
    response = requests.put(url, headers=headers, json=data)
    if response.status_code in [200, 201]:
        print(f"SUCCESS: {git_path}")
    else:
        print(f"FAILED: {git_path} - {response.status_code} - {response.text}")

def main():
    files = get_all_files(".")
    total = len(files)
    print(f"Starting upload for {total} files...")
    
    for i, (local_path, git_path) in enumerate(files):
        print(f"[{i+1}/{total}] ", end="")
        upload_file(local_path, git_path)
        time.sleep(0.2) # Small delay to be polite

if __name__ == "__main__":
    main()
