"""
GitHub Bulk Repository Loader - Enhanced Version
Loads multiple GitHub accounts and organizations into GitHub Desktop
"""
import subprocess
import requests
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

class GitHubLoader:
    def __init__(self, token=None):
        self.token = token
        self.headers = {'Authorization': f'token {token}'} if token else {}
        
    def get_user_repos(self, username):
        """Get all repositories for a user"""
        repos = []
        page = 1
        while True:
            url = f"https://api.github.com/users/{username}/repos?page={page}&per_page=100"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200 or not response.json():
                break
            repos.extend(response.json())
            page += 1
        return repos
    
    def get_org_repos(self, org_name):
        """Get all repositories for an organization"""
        repos = []
        page = 1
        while True:
            url = f"https://api.github.com/orgs/{org_name}/repos?page={page}&per_page=100"
            response = requests.get(url, headers=self.headers)
            if response.status_code != 200 or not response.json():
                break
            repos.extend(response.json())
            page += 1
        return repos
    
    def clone_repo(self, repo, base_path):
        """Clone repository and add to GitHub Desktop"""
        repo_name = repo['name']
        repo_url = repo['clone_url']
        local_path = os.path.join(base_path, repo_name)
        
        if os.path.exists(local_path):
            print(f"⏭️ Skipping {repo_name} (exists)")
            return True
            
        try:
            # Clone repository
            subprocess.run(['git', 'clone', repo_url, local_path], 
                         check=True, capture_output=True)
            
            # Add to GitHub Desktop
            subprocess.run(['cmd', '/c', f'start github "{local_path}"'], 
                         shell=True, capture_output=True)
            
            print(f"✅ Loaded {repo_name}")
            return True
        except:
            print(f"❌ Failed {repo_name}")
            return False
    
    def bulk_load(self, accounts, base_path="C:\\GitHub", max_workers=5):
        """Load multiple accounts/orgs in parallel"""
        os.makedirs(base_path, exist_ok=True)
        
        all_repos = []
        
        # Collect all repositories
        for account in accounts:
            if account.get('type') == 'org':
                repos = self.get_org_repos(account['name'])
            else:
                repos = self.get_user_repos(account['name'])
            
            print(f"Found {len(repos)} repos for {account['name']}")
            all_repos.extend(repos)
        
        # Clone repositories in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.clone_repo, repo, base_path) 
                      for repo in all_repos]
            
            for future in futures:
                future.result()

def main():
    # Configuration
    token = input("GitHub token (optional): ") or None
    
    # Define accounts to load
    accounts = []
    
    while True:
        account_type = input("Add (u)ser, (o)rg, or (d)one: ").lower()
        if account_type == 'd':
            break
        elif account_type in ['u', 'o']:
            name = input("Enter name: ")
            accounts.append({
                'name': name,
                'type': 'org' if account_type == 'o' else 'user'
            })
    
    base_path = input("Local path (default C:\\GitHub): ") or "C:\\GitHub"
    
    # Load repositories
    loader = GitHubLoader(token)
    loader.bulk_load(accounts, base_path)
    
    print("✅ All repositories loaded into GitHub Desktop!")

if __name__ == "__main__":
    main()