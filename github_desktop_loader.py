"""
GitHub Desktop Repository Loader
Loads all GitHub repositories into GitHub Desktop interface
"""
import subprocess
import requests
import json
import os
from pathlib import Path

def get_github_repos(username, token=None):
    """Get all repositories for a GitHub user"""
    headers = {'Authorization': f'token {token}'} if token else {}
    
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            break
            
        page_repos = response.json()
        if not page_repos:
            break
            
        repos.extend(page_repos)
        page += 1
    
    return repos

def clone_to_github_desktop(repo_url, local_path):
    """Clone repository and add to GitHub Desktop"""
    try:
        # Clone repository
        subprocess.run(['git', 'clone', repo_url, local_path], check=True)
        
        # Add to GitHub Desktop (Windows)
        subprocess.run(['github', local_path], shell=True)
        
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    # Configuration
    GITHUB_USERNAME = input("Enter GitHub username: ")
    GITHUB_TOKEN = input("Enter GitHub token (optional): ") or None
    BASE_PATH = input("Enter local directory path: ") or "C:\\GitHub"
    
    # Create base directory
    Path(BASE_PATH).mkdir(parents=True, exist_ok=True)
    
    # Get repositories
    print("Fetching repositories...")
    repos = get_github_repos(GITHUB_USERNAME, GITHUB_TOKEN)
    
    print(f"Found {len(repos)} repositories")
    
    # Clone each repository
    for repo in repos:
        repo_name = repo['name']
        repo_url = repo['clone_url']
        local_path = os.path.join(BASE_PATH, repo_name)
        
        if os.path.exists(local_path):
            print(f"Skipping {repo_name} (already exists)")
            continue
            
        print(f"Cloning {repo_name}...")
        if clone_to_github_desktop(repo_url, local_path):
            print(f"✅ {repo_name} loaded into GitHub Desktop")
        else:
            print(f"❌ Failed to load {repo_name}")

if __name__ == "__main__":
    main()