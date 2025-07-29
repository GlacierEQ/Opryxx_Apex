"""
GitHub Hyper-Pro Repository Loader
Advanced repository management with AI-powered analysis and optimization
"""
import subprocess
import requests
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import ast
import re

class HyperProGitHubLoader:
    def __init__(self, token=None):
        self.token = token
        self.headers = {'Authorization': f'token {token}'} if token else {}
        
    def analyze_repo_tech_stack(self, repo_path):
        """AI-powered tech stack analysis"""
        tech_stack = {'languages': [], 'frameworks': [], 'tools': []}
        
        # Language detection
        for file_path in Path(repo_path).rglob('*'):
            if file_path.is_file():
                ext = file_path.suffix.lower()
                if ext == '.py': tech_stack['languages'].append('Python')
                elif ext == '.js': tech_stack['languages'].append('JavaScript')
                elif ext == '.ts': tech_stack['languages'].append('TypeScript')
                elif ext == '.java': tech_stack['languages'].append('Java')
                elif ext == '.cpp': tech_stack['languages'].append('C++')
                elif ext == '.cs': tech_stack['languages'].append('C#')
                elif ext == '.go': tech_stack['languages'].append('Go')
                elif ext == '.rs': tech_stack['languages'].append('Rust')
        
        # Framework detection
        if Path(repo_path, 'package.json').exists():
            with open(Path(repo_path, 'package.json')) as f:
                pkg = json.load(f)
                deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                if 'react' in deps: tech_stack['frameworks'].append('React')
                if 'vue' in deps: tech_stack['frameworks'].append('Vue')
                if 'angular' in deps: tech_stack['frameworks'].append('Angular')
                if 'express' in deps: tech_stack['frameworks'].append('Express')
        
        if Path(repo_path, 'requirements.txt').exists():
            with open(Path(repo_path, 'requirements.txt')) as f:
                reqs = f.read().lower()
                if 'django' in reqs: tech_stack['frameworks'].append('Django')
                if 'flask' in reqs: tech_stack['frameworks'].append('Flask')
                if 'fastapi' in reqs: tech_stack['frameworks'].append('FastAPI')
        
        return tech_stack
    
    def generate_hyper_readme(self, repo_path, repo_data, tech_stack):
        """Generate hyper-professional README"""
        readme_content = f"""# 🚀 {repo_data['name']}

[![GitHub stars](https://img.shields.io/github/stars/{repo_data['full_name']})](https://github.com/{repo_data['full_name']}/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/{repo_data['full_name']})](https://github.com/{repo_data['full_name']}/network)
[![GitHub issues](https://img.shields.io/github/issues/{repo_data['full_name']})](https://github.com/{repo_data['full_name']}/issues)

## 📋 Overview
{repo_data.get('description', 'Advanced project with cutting-edge technology stack')}

## 🛠️ Tech Stack
**Languages:** {', '.join(set(tech_stack['languages']))}
**Frameworks:** {', '.join(set(tech_stack['frameworks']))}

## 🚀 Quick Start
```bash
git clone {repo_data['clone_url']}
cd {repo_data['name']}
# Auto-generated setup commands will be added here
```

## 📊 Project Stats
- **Created:** {repo_data['created_at'][:10]}
- **Last Updated:** {repo_data['updated_at'][:10]}
- **Size:** {repo_data['size']} KB

## 🤝 Contributing
Contributions are welcome! Please read our contributing guidelines.

## 📄 License
{repo_data.get('license', {}).get('name', 'MIT') if repo_data.get('license') else 'MIT'}
"""
        
        readme_path = Path(repo_path, 'README.md')
        if not readme_path.exists():
            with open(readme_path, 'w') as f:
                f.write(readme_content)
    
    def create_dev_environment(self, repo_path, tech_stack):
        """Create development environment files"""
        
        # VS Code settings
        vscode_dir = Path(repo_path, '.vscode')
        vscode_dir.mkdir(exist_ok=True)
        
        settings = {
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {"source.fixAll": True},
            "python.defaultInterpreterPath": "./venv/bin/python",
            "typescript.preferences.importModuleSpecifier": "relative"
        }
        
        with open(vscode_dir / 'settings.json', 'w') as f:
            json.dump(settings, f, indent=2)
        
        # Docker setup for complex projects
        if len(tech_stack['languages']) > 1:
            dockerfile = """FROM node:16-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "start"]"""
            
            with open(Path(repo_path, 'Dockerfile'), 'w') as f:
                f.write(dockerfile)
        
        # GitHub Actions CI/CD
        github_dir = Path(repo_path, '.github', 'workflows')
        github_dir.mkdir(parents=True, exist_ok=True)
        
        ci_yaml = """name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup
      run: echo "Setting up environment"
    - name: Test
      run: echo "Running tests"
    - name: Deploy
      run: echo "Deploying application"
"""
        
        with open(github_dir / 'ci.yml', 'w') as f:
            f.write(ci_yaml)
    
    def optimize_repository(self, repo_path, repo_data):
        """Apply hyper-pro optimizations to repository"""
        try:
            # Analyze tech stack
            tech_stack = self.analyze_repo_tech_stack(repo_path)
            
            # Generate professional README
            self.generate_hyper_readme(repo_path, repo_data, tech_stack)
            
            # Create development environment
            self.create_dev_environment(repo_path, tech_stack)
            
            # Add .gitignore if missing
            gitignore_path = Path(repo_path, '.gitignore')
            if not gitignore_path.exists():
                gitignore_content = """# Dependencies
node_modules/
venv/
__pycache__/

# Build outputs
dist/
build/
*.exe
*.dll

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/
"""
                with open(gitignore_path, 'w') as f:
                    f.write(gitignore_content)
            
            # Initialize git hooks
            hooks_dir = Path(repo_path, '.git', 'hooks')
            if hooks_dir.exists():
                pre_commit = """#!/bin/sh
echo "Running pre-commit checks..."
# Add your pre-commit checks here
"""
                with open(hooks_dir / 'pre-commit', 'w') as f:
                    f.write(pre_commit)
                os.chmod(hooks_dir / 'pre-commit', 0o755)
            
            print(f"🔧 Optimized {repo_data['name']}")
            return True
            
        except Exception as e:
            print(f"❌ Optimization failed for {repo_data['name']}: {e}")
            return False
    
    def clone_and_enhance_repo(self, repo, base_path):
        """Clone repository and apply hyper-pro enhancements"""
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
            
            # Apply hyper-pro optimizations
            self.optimize_repository(local_path, repo)
            
            # Add to GitHub Desktop
            subprocess.run(['cmd', '/c', f'start github "{local_path}"'], 
                         shell=True, capture_output=True)
            
            print(f"✅ Enhanced {repo_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed {repo_name}: {e}")
            return False
    
    def hyper_bulk_load(self, accounts, base_path="C:\\GitHub-Pro", max_workers=3):
        """Load and enhance multiple repositories with hyper-pro features"""
        os.makedirs(base_path, exist_ok=True)
        
        all_repos = []
        
        # Collect repositories
        for account in accounts:
            if account.get('type') == 'org':
                repos = self.get_org_repos(account['name'])
            else:
                repos = self.get_user_repos(account['name'])
            
            print(f"📦 Found {len(repos)} repos for {account['name']}")
            all_repos.extend(repos)
        
        # Process repositories with enhancements
        print(f"🚀 Processing {len(all_repos)} repositories with hyper-pro features...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.clone_and_enhance_repo, repo, base_path) 
                      for repo in all_repos]
            
            success_count = sum(1 for future in futures if future.result())
        
        print(f"🎉 Successfully enhanced {success_count}/{len(all_repos)} repositories!")
        
        # Generate master project index
        self.generate_project_index(all_repos, base_path)
    
    def generate_project_index(self, repos, base_path):
        """Generate master project index with analytics"""
        index_content = """# 🚀 GitHub Projects Master Index

## 📊 Repository Analytics
"""
        
        # Language statistics
        languages = {}
        for repo in repos:
            lang = repo.get('language')
            if lang:
                languages[lang] = languages.get(lang, 0) + 1
        
        index_content += "\n### 🔤 Languages\n"
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            index_content += f"- **{lang}**: {count} repositories\n"
        
        # Repository list
        index_content += "\n### 📁 Repositories\n"
        for repo in sorted(repos, key=lambda x: x['name']):
            index_content += f"- [{repo['name']}](./{repo['name']}) - {repo.get('description', 'No description')}\n"
        
        with open(Path(base_path, 'PROJECT_INDEX.md'), 'w') as f:
            f.write(index_content)
    
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

def main():
    print("🚀 GitHub Hyper-Pro Repository Loader")
    print("=" * 50)
    
    token = input("GitHub token (recommended): ") or None
    
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
    
    base_path = input("Local path (default C:\\GitHub-Pro): ") or "C:\\GitHub-Pro"
    
    loader = HyperProGitHubLoader(token)
    loader.hyper_bulk_load(accounts, base_path)

if __name__ == "__main__":
    main()