import os
import subprocess
import shutil
import tempfile
import json
from datetime import datetime

# CONFIG: List of target repo HTTPS URLs (or load from a file)
REPOS_CONFIG = os.path.join(os.path.dirname(__file__), 'target_repos.json')
WORKFLOWS_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workflows'))
LOG_FILE = os.path.join(os.path.dirname(__file__), 'sync-log.md')


def load_repos():
    if os.path.exists(REPOS_CONFIG):
        with open(REPOS_CONFIG, 'r') as f:
            return json.load(f)
    return []

def log(msg):
    timestamp = datetime.utcnow().isoformat()
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {msg}\n")


def sync_repo(repo_url):
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    with tempfile.TemporaryDirectory() as tmpdir:
        try:
            subprocess.check_call(['git', 'clone', repo_url, tmpdir])
            workflows_dst = os.path.join(tmpdir, '.github', 'workflows')
            os.makedirs(workflows_dst, exist_ok=True)
            # Copy all workflow files
            for fname in os.listdir(WORKFLOWS_SRC):
                src = os.path.join(WORKFLOWS_SRC, fname)
                dst = os.path.join(workflows_dst, fname)
                shutil.copy2(src, dst)
            subprocess.check_call(['git', 'add', '.github/workflows'], cwd=tmpdir)
            subprocess.check_call(['git', 'commit', '-m', 'Sync GitHub Actions workflows from canonical source'], cwd=tmpdir)
            subprocess.check_call(['git', 'push'], cwd=tmpdir)
            log(f"SUCCESS: Synced workflows to {repo_url}")
        except subprocess.CalledProcessError as e:
            log(f"ERROR: Failed to sync {repo_url}: {e}")
        except Exception as e:
            log(f"ERROR: Unexpected error for {repo_url}: {e}")

def main():
    repos = load_repos()
    if not repos:
        log("No target repos configured. Add repo URLs to target_repos.json.")
        return
    for repo_url in repos:
        sync_repo(repo_url)

if __name__ == '__main__':
    main()
